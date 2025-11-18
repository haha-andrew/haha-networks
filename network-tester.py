from flask import Flask, render_template_string, jsonify
import requests
import time
from datetime import datetime
import socket
import os
import io

app = Flask(__name__)

# Pre-generated test files (embedded in code)
def create_test_image():
    """Create a simple test image"""
    # 1x1 PNG image (smallest valid PNG)
    return io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

def create_test_video():
    """Create a simple test video file"""
    # Minimal valid MP4 file
    return io.BytesIO(b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free')

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

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/run-test', methods=['POST'])
def run_test():
    results = []
    
    # Pre-configured test URL
    target_url = 'https://hahavending.com'
    
    # Test 1: HTTP Connectivity
    results.append(test_http_ping(target_url))
    
    # Test 2: DNS Resolution
    results.append(test_dns_resolution(target_url))
    
    # Test 3: Image Upload (using pre-generated image)
    results.append(test_image_upload(target_url))
    
    # Test 4: Video Upload (using pre-generated video)
    results.append(test_video_upload(target_url))
    
    return jsonify({'results': results})

def test_http_ping(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        duration = round((time.time() - start_time) * 1000)
        
        return {
            'test': 'HTTP Connectivity',
            'status': 'success' if response.status_code == 200 else 'error',
            'message': f'Connection established successfully' if response.status_code == 200 else f'Connection returned status {response.status_code}',
            'details': {
                'Status': response.status_code,
                'Latency': f'{duration}ms',
                'Response Size': f'{len(response.content)} bytes'
            }
        }
    except Exception as e:
        return {
            'test': 'HTTP Connectivity',
            'status': 'error',
            'message': 'Connection blocked or failed',
            'details': {'Error': str(e)[:100]}
        }

def test_dns_resolution(url):
    try:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname
        
        start_time = time.time()
        ip_address = socket.gethostbyname(hostname)
        duration = round((time.time() - start_time) * 1000)
        
        return {
            'test': 'DNS Resolution',
            'status': 'success',
            'message': 'DNS resolved successfully',
            'details': {
                'Hostname': hostname,
                'IP Address': ip_address,
                'Resolution Time': f'{duration}ms'
            }
        }
    except Exception as e:
        return {
            'test': 'DNS Resolution',
            'status': 'error',
            'message': 'DNS resolution failed',
            'details': {'Error': str(e)[:100]}
        }

def test_image_upload(url):
    try:
        image_data = create_test_image()
        files = {'image': ('test_image.png', image_data, 'image/png')}
        
        start_time = time.time()
        response = requests.post(url, files=files, timeout=30)
        duration = round((time.time() - start_time) * 1000)
        
        return {
            'test': 'Image Upload',
            'status': 'success' if response.status_code == 200 else 'error',
            'message': 'Image upload successful' if response.status_code == 200 else f'Image upload failed (Status {response.status_code})',
            'details': {
                'File': 'test_image.png',
                'Size': '0.1 KB',
                'Status': response.status_code,
                'Upload Time': f'{duration}ms'
            }
        }
    except Exception as e:
        return {
            'test': 'Image Upload',
            'status': 'error',
            'message': 'Image upload blocked or failed',
            'details': {'Error': str(e)[:100]}
        }

def test_video_upload(url):
    try:
        video_data = create_test_video()
        files = {'video': ('test_video.mp4', video_data, 'video/mp4')}
        
        start_time = time.time()
        response = requests.post(url, files=files, timeout=30)
        duration = round((time.time() - start_time) * 1000)
        
        return {
            'test': 'Video Upload',
            'status': 'success' if response.status_code == 200 else 'error',
            'message': 'Video upload successful' if response.status_code == 200 else f'Video upload failed (Status {response.status_code})',
            'details': {
                'File': 'test_video.mp4',
                'Size': '0.03 KB',
                'Status': response.status_code,
                'Upload Time': f'{duration}ms'
            }
        }
    except Exception as e:
        return {
            'test': 'Video Upload',
            'status': 'error',
            'message': 'Video upload blocked or failed',
            'details': {'Error': str(e)[:100]}
        }

if __name__ == '__main__':
    print("="*60)
    print("⚡ NETWORK TEST - Yellow & Black Edition")
    print("="*60)
    print("\n✅ Server running on http://localhost:5000")
    print("🌐 Open your browser and click the big button!")
    print("\nPress CTRL+C to stop\n")
    app.run(debug=True, host='0.0.0.0', port=5000)