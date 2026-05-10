package com.neuroassistant

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.KeyEvent
import android.webkit.*
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this).apply {
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true
                allowFileAccess = true
                allowContentAccess = true
                setSupportZoom(false)
                builtInZoomControls = false
                displayZoomControls = false
                useWideViewPort = true
                loadWithOverviewMode = true
                // Allow mixed content (HTTP inside HTTPS)
                mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            }

            webViewClient = object : WebViewClient() {
                override fun onReceivedError(
                    view: WebView?,
                    request: WebResourceRequest?,
                    error: WebResourceError?
                ) {
                    if (request?.isForMainFrame == true) {
                        val msg = error?.description?.toString() ?: "Unknown error"
                        Toast.makeText(
                            this@MainActivity,
                            "Ошибка загрузки: $msg",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }
            }

            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(msg: ConsoleMessage?): Boolean {
                    return true // suppress console logs
                }
            }
        }

        setContentView(webView)

        // Load saved URL or default
        val prefs = getSharedPreferences("na_prefs", MODE_PRIVATE)
        val savedUrl = prefs.getString("server_url", "") ?: ""

        if (savedUrl.isNotEmpty()) {
            webView.loadUrl(savedUrl)
        } else {
            // Load onboarding page from assets
            webView.loadUrl("file:///android_asset/index.html")
        }
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }

    override fun onPause() {
        super.onPause()
        webView.onPause()
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
    }
}
