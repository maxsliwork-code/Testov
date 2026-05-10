# 🤖 Нейро-ассистент

Чат-бот на базе **Google Gemini API** с системой белых списков (whitelist).  
Работает как веб-приложение (ПК) и как Android APK.

---

## 📦 Структура проекта

```
neuro-assistant/
├── backend/          # Python FastAPI сервер
│   ├── main.py       # весь бэкенд в одном файле
│   ├── index.html    # веб-интерфейс (ПК + Android)
│   ├── requirements.txt
│   └── .env.example
├── android/          # Android Studio проект (WebView APK)
│   ├── app/
│   └── ...
└── .github/
    └── workflows/
        └── build-apk.yml  # автосборка APK
```

---

## 🚀 Быстрый старт (Бэкенд)

### 1. Установка

```bash
cd backend
pip install -r requirements.txt
```

### 2. Настройка

```bash
cp .env.example .env
```

Открой `.env` и заполни:
```
GEMINI_API_KEY=твой_ключ_от_google_ai_studio
ADMIN_KEY=любой_секретный_пароль
```

Получить Gemini API ключ: https://aistudio.google.com/apikey

### 3. Запуск

```bash
python main.py
```

Сервер запустится на `http://0.0.0.0:8000`

---

## 🔑 Управление ключами (Whitelist)

### Создать API ключ для пользователя

```bash
curl -X POST http://localhost:8000/admin/keys \
  -H "x-admin-key: твой_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Пользователь 1"}'
```

Ответ:
```json
{"api_key": "na_abc123...", "name": "Пользователь 1"}
```

### Отключить ключ

```bash
curl -X PATCH http://localhost:8000/admin/keys/na_abc123.../disable \
  -H "x-admin-key: твой_ADMIN_KEY"
```

### Список всех ключей

```bash
curl http://localhost:8000/admin/keys \
  -H "x-admin-key: твой_ADMIN_KEY"
```

---

## 🖥️ Использование на ПК

1. Запусти сервер (`python main.py`)
2. Открой браузер: `http://localhost:8000`
3. Вставь API ключ (`na_...`)
4. Пиши сообщения

---

## 📱 Android APK

### Вариант 1 — Скачать готовый APK (рекомендуется)

1. Открой вкладку **Actions** в GitHub репозитории
2. Выбери последний запуск `Build Android APK`
3. Скачай **neuro-assistant-debug-apk**
4. Установи на Android (нужно разрешить установку из неизвестных источников)

### Вариант 2 — Сборка вручную (Android Studio)

1. Открой папку `android/` в Android Studio
2. `Build → Build Bundle(s) / APK(s) → Build APK(s)`
3. APK будет в `android/app/build/outputs/apk/debug/`

### Настройка APK

После установки:
1. Открой приложение
2. Введи URL сервера (если сервер на ПК в той же сети: `http://192.168.x.x:8000`)
3. Нажми **Подключиться**
4. Введи API ключ и общайся

---

## 🌐 Деплой на VPS (опционально)

```bash
# На сервере
pip install -r requirements.txt
# Создай .env с ключами
nohup python main.py &
```

Или через systemd/docker для постоянной работы.

---

## 📡 API эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| `GET` | `/` | Веб-интерфейс |
| `POST` | `/chat` | Отправить сообщение (SSE стриминг) |
| `DELETE` | `/chat/history` | Очистить историю |
| `GET` | `/admin/keys` | Список всех ключей |
| `POST` | `/admin/keys` | Создать новый ключ |
| `PATCH` | `/admin/keys/{key}/disable` | Отключить ключ |
| `PATCH` | `/admin/keys/{key}/enable` | Включить ключ |
| `DELETE` | `/admin/keys/{key}` | Удалить ключ |

Заголовки:
- `x-api-key: na_...` — для пользовательских запросов
- `x-admin-key: ...` — для административных запросов

---

## ⚙️ Технологии

- **Backend**: Python 3.10+ / FastAPI / SQLite / SSE стриминг
- **AI**: Google Gemini 2.0 Flash
- **Frontend**: HTML/CSS/JS (без фреймворков)
- **Android**: Kotlin / WebView
- **CI/CD**: GitHub Actions
