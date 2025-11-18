# functions/index.py
from flask import Flask, render_template_string
import io

# 初始化 Flask 实例（单个文件独立初始化，避免跨文件依赖）
app = Flask(__name__)

# HTML 模板（完整复制原模板）
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Test</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a1a;
            color: #ffd700;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        .container {
            max-width: 800px;
            width: 100%;
            text-align: center;
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 3rem;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
            to { text-shadow: 0 0 30px rgba(255, 215, 0, 0.8); }
        }
        .test-button {
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            color: #1a1a1a;
            border: 4px solid #ffd700;
            padding: 2rem 4rem;
            font-size: 2rem;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 40px rgba(255, 215, 0, 0.3);
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .test-button:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(255, 215, 0, 0.5);
            background: linear-gradient(135deg, #ffed4e 0%, #ffd700 100%);
        }
        .test-button:active {
            transform: translateY(-2px);
        }
        .test-button:disabled {
            background: #666;
            border-color: #666;
            cursor: not-allowed;
            color: #999;
            box-shadow: none;
            transform: none;
        }
        .spinner {
            border: 4px solid #333;
            border-top: 4px solid #ffd700;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 3rem auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .results {
            margin-top: 3rem;
            display: none;
        }
        .results.show {
            display: block;
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .status-banner {
            padding: 2rem;
            border-radius: 20px;
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 2rem;
            border: 3px solid;
        }
        .status-success {
            background: rgba(255, 215, 0, 0.1);
            border-color: #ffd700;
            color: #ffd700;
        }
        .status-failure {
            background: rgba(255, 69, 0, 0.1);
            border-color: #ff4500;
            color: #ff4500;
        }
        .status-partial {
            background: rgba(255, 165, 0, 0.1);
            border-color: #ffa500;
            color: #ffa500;
        }
        .test-details {
            background: #2a2a2a;
            border: 2px solid #ffd700;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            text-align: left;
        }
        .test-name {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #ffd700;
        }
        .test-status {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 5px;
            font-size: 0.9rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .test-pass { background: #ffd700; color: #1a1a1a; }
        .test-fail { background: #ff4500; color: #fff; }
        .test-message {
            color: #ccc;
            margin-top: 0.5rem;
            font-size: 1rem;
        }
        .test-metrics {
            background: #1a1a1a;
            padding: 1rem;
            border-radius: 10px;
            margin-top: 1rem;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }
        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 0.3rem 0;
            border-bottom: 1px solid #333;
        }
        .metric-row:last-child {
            border-bottom: none;
        }
        .metric-label { color: #888; }
        .metric-value { color: #ffd700; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>NETWORK TEST</h1>
        
        <button id="testBtn" class="test-button" onclick="runTest()">
            RUN TEST
        </button>
        
        <div id="loading" class="hidden">
            <div class="spinner"></div>
            <p style="font-size: 1.2rem; color: #ffd700;">Testing network...</p>
        </div>
        
        <div id="results" class="results"></div>
    </div>

    <script>
        async function runTest() {
            const btn = document.getElementById('testBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            btn.disabled = true;
            loading.classList.remove('hidden');
            results.classList.remove('show');
            results.innerHTML = '';
            
            try {
                const response = await fetch('/run-test', {
                    method: 'POST'
                });
                
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                results.innerHTML = `
                    <div class="status-banner status-failure">
                        ❌ TEST FAILED
                    </div>
                    <div class="test-details">
                        <div class="test-name">System Error</div>
                        <div class="test-message">Could not complete test: ${error.message}</div>
                    </div>
                `;
                results.classList.add('show');
            } finally {
                loading.classList.add('hidden');
                btn.disabled = false;
            }
        }

        function displayResults(data) {
            const results = document.getElementById('results');
            
            const passed = data.results.filter(r => r.status === 'success').length;
            const total = data.results.length;
            
            let statusClass, statusText, statusIcon;
            if (passed === total) {
                statusClass = 'status-success';
                statusText = 'ALL TESTS PASSED';
                statusIcon = '✅';
            } else if (passed === 0) {
                statusClass = 'status-failure';
                statusText = 'ALL TESTS FAILED';
                statusIcon = '❌';
            } else {
                statusClass = 'status-partial';
                statusText = 'PARTIAL SUCCESS';
                statusIcon = '⚠️';
            }
            
            let html = `
                <div class="status-banner ${statusClass}">
                    ${statusIcon} ${statusText} (${passed}/${total})
                </div>
            `;
            
            data.results.forEach(result => {
                const statusClass = result.status === 'success' ? 'test-pass' : 'test-fail';
                const statusText = result.status === 'success' ? 'PASS' : 'FAIL';
                
                let metricsHtml = '';
                if (result.details) {
                    metricsHtml = '<div class="test-metrics">';
                    for (const [key, value] of Object.entries(result.details)) {
                        metricsHtml += `
                            <div class="metric-row">
                                <span class="metric-label">${key}</span>
                                <span class="metric-value">${value}</span>
                            </div>
                        `;
                    }
                    metricsHtml += '</div>';
                }
                
                html += `
                    <div class="test-details">
                        <div class="test-name">${result.test}</div>
                        <span class="test-status ${statusClass}">${statusText}</span>
                        <div class="test-message">${result.message}</div>
                        ${metricsHtml}
                    </div>
                `;
            });
            
            results.innerHTML = html;
            results.classList.add('show');
        }
    </script>
</body>
</html>
'''

# Pages Functions 入口（固定格式）
def on_fetch(request):
    # 只处理 GET 请求（首页）
    if request.method == 'GET':
        return new Response(
            render_template_string(HTML_TEMPLATE),
            headers={'Content-Type': 'text/html; charset=utf-8'}
        )
    # 其他请求返回 405
    return new Response('Method Not Allowed', status=405)