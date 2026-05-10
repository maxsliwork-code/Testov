from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai
import sqlite3, os, uuid, json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

app = FastAPI(title="Neuro Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "keys.db"

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            key TEXT PRIMARY KEY,
            name TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT,
            role TEXT,
            text TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    con.commit()
    return con

def check_key(key: str):
    con = get_db()
    row = con.execute("SELECT active FROM api_keys WHERE key=?", (key,)).fetchone()
    con.close()
    if not row:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if row["active"] == 0:
        raise HTTPException(status_code=403, detail="API key is disabled")

# ── Frontend ────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def frontend():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        return open(html_path, encoding="utf-8").read()
    return HTMLResponse("<h1>index.html not found</h1>", status_code=404)

# ── Chat ─────────────────────────────────────────────────────────────────────
@app.post("/chat")
async def chat(body: dict, x_api_key: str = Header(...)):
    check_key(x_api_key)
    message = body.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Empty message")

    con = get_db()
    rows = con.execute(
        "SELECT role, text FROM history WHERE api_key=? ORDER BY id DESC LIMIT 20",
        (x_api_key,)
    ).fetchall()
    history = [{"role": r["role"], "parts": [r["text"]]} for r in reversed(rows)]

    model = genai.GenerativeModel("gemini-2.0-flash")
    session = model.start_chat(history=history)

    def stream():
        try:
            response = session.send_message(message, stream=True)
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    yield f"data: {json.dumps({'text': chunk.text})}\n\n"
            # save to history
            save_con = get_db()
            save_con.execute(
                "INSERT INTO history (api_key, role, text) VALUES (?,?,?)",
                (x_api_key, "user", message)
            )
            save_con.execute(
                "INSERT INTO history (api_key, role, text) VALUES (?,?,?)",
                (x_api_key, "model", full_text)
            )
            save_con.commit()
            save_con.close()
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
            con.close()

    return StreamingResponse(stream(), media_type="text/event-stream")

@app.delete("/chat/history")
def clear_history(x_api_key: str = Header(...)):
    check_key(x_api_key)
    con = get_db()
    con.execute("DELETE FROM history WHERE api_key=?", (x_api_key,))
    con.commit()
    con.close()
    return {"status": "cleared"}

# ── Admin ─────────────────────────────────────────────────────────────────────
def check_admin(key: str):
    if key != os.getenv("ADMIN_KEY", "changeme"):
        raise HTTPException(status_code=403, detail="Not authorized")

@app.get("/admin/keys")
def list_keys(x_admin_key: str = Header(...)):
    check_admin(x_admin_key)
    con = get_db()
    rows = con.execute("SELECT key, name, active, created_at FROM api_keys").fetchall()
    con.close()
    return [dict(r) for r in rows]

@app.post("/admin/keys")
def create_key(body: dict, x_admin_key: str = Header(...)):
    check_admin(x_admin_key)
    new_key = "na_" + uuid.uuid4().hex
    name = body.get("name", "user")
    con = get_db()
    con.execute("INSERT INTO api_keys (key, name) VALUES (?,?)", (new_key, name))
    con.commit()
    con.close()
    return {"api_key": new_key, "name": name}

@app.patch("/admin/keys/{key}/disable")
def disable_key(key: str, x_admin_key: str = Header(...)):
    check_admin(x_admin_key)
    con = get_db()
    con.execute("UPDATE api_keys SET active=0 WHERE key=?", (key,))
    con.commit()
    con.close()
    return {"status": "disabled"}

@app.patch("/admin/keys/{key}/enable")
def enable_key(key: str, x_admin_key: str = Header(...)):
    check_admin(x_admin_key)
    con = get_db()
    con.execute("UPDATE api_keys SET active=1 WHERE key=?", (key,))
    con.commit()
    con.close()
    return {"status": "enabled"}

@app.delete("/admin/keys/{key}")
def delete_key(key: str, x_admin_key: str = Header(...)):
    check_admin(x_admin_key)
    con = get_db()
    con.execute("DELETE FROM api_keys WHERE key=?", (key,))
    con.commit()
    con.close()
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
