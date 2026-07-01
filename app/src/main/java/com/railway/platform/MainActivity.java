package com.railway.platform;

import android.os.Bundle;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.FrameLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.chaquo.python.Python;
import com.chaquo.python.PyObject;

public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private SwipeRefreshLayout swipeRefresh;
    private ProgressBar progressBar;
    private TextView statusText;
    private static final int FLASK_PORT = 5001;
    private static final String LOCAL_URL = "http://127.0.0.1:" + FLASK_PORT + "/";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        swipeRefresh = findViewById(R.id.swipe_refresh);
        progressBar = findViewById(R.id.progress_bar);
        statusText = findViewById(R.id.status_text);

        setupWebView();
        setupSwipeRefresh();

        // Start Flask and load page
        startFlaskServer();
    }

    private void setupWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setAllowFileAccess(false); // Security: no file access
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);

        // Enable responsive layout
        settings.setLayoutAlgorithm(WebSettings.LayoutAlgorithm.NORMAL);

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                if (newProgress < 100) {
                    progressBar.setVisibility(View.VISIBLE);
                    progressBar.setProgress(newProgress);
                    statusText.setText("加载中... " + newProgress + "%");
                } else {
                    progressBar.setVisibility(View.GONE);
                    statusText.setText("");
                }
            }
        });
    }

    private void setupSwipeRefresh() {
        swipeRefresh.setColorSchemeResources(
            R.color.primary,
            R.color.accent,
            R.color.dark_blue
        );
        swipeRefresh.setOnRefreshListener(() -> {
            webView.reload();
            swipeRefresh.setRefreshing(false);
        });
    }

    private void startFlaskServer() {
        statusText.setVisibility(View.VISIBLE);
        statusText.setText("正在启动服务...");

        new Thread(() -> {
            try {
                Python py = Python.getInstance();
                PyObject pyModule = py.getModule("run_app");
                PyObject startFunc = pyModule.callAttr("start_server", FLASK_PORT);
                String result = startFunc.toString();

                runOnUiThread(() -> {
                    statusText.setText("服务已启动");
                    loadWebPage();
                });

            } catch (Exception e) {
                e.printStackTrace();
                runOnUiThread(() -> {
                    statusText.setText("启动失败: " + e.getMessage());
                });
            }
        }).start();
    }

    private void loadWebPage() {
        runOnUiThread(() -> {
            webView.loadUrl(LOCAL_URL);
            // Auto-hide status after delay
            new android.os.Handler().postDelayed(() ->
                statusText.setVisibility(View.GONE), 3000);
        });
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
}
