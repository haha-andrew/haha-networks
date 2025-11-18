# functions/run-test.py
import requests
import time
import socket
import io
from urllib.parse import urlparse

# 测试文件生成函数
def create_test_image():
    return io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

def create_test_video():
    return io.BytesIO(b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free')

# 测试工具函数
def test_http_ping(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        duration = round((time.time() - start_time) * 1000)
        return {
            'test': 'HTTP Connectivity',
            'status': 'success' if response.status_code == 200 else 'error',
            'message': f'Connection established successfully' if response.status_code == 200 else f'Connection returned status {response.status_code}',
            'details': {'Status': response.status_code, 'Latency': f'{duration}ms', 'Response Size': f'{len(response.content)} bytes'}
        }
    except Exception as e:
        return {'test': 'HTTP Connectivity', 'status': 'error', 'message': 'Connection blocked or failed', 'details': {'Error': str(e)[:100]}}

def test_dns_resolution(url):
    try:
        hostname = urlparse(url).hostname
        start_time = time.time()
        ip_address = socket.gethostbyname(hostname)
        duration = round((time.time() - start_time) * 1000)
        return {
            'test': 'DNS Resolution',
            'status': 'success',
            'message': 'DNS resolved successfully',
            'details': {'Hostname': hostname, 'IP Address': ip_address, 'Resolution Time': f'{duration}ms'}
        }
    except Exception as e:
        return {'test': 'DNS Resolution', 'status': 'error', 'message': 'DNS resolution failed', 'details': {'Error': str(e)[:100]}}

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
            'details': {'File': 'test_image.png', 'Size': '0.1 KB', 'Status': response.status_code, 'Upload Time': f'{duration}ms'}
        }
    except Exception as e:
        return {'test': 'Image Upload', 'status': 'error', 'message': 'Image upload blocked or failed', 'details': {'Error': str(e)[:100]}}

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
            'details': {'File': 'test_video.mp4', 'Size': '0.03 KB', 'Status': response.status_code, 'Upload Time': f'{duration}ms'}
        }
    except Exception as e:
        return {'test': 'Video Upload', 'status': 'error', 'message': 'Video upload blocked or failed', 'details': {'Error': str(e)[:100]}}

# Pages Functions 入口（固定格式）
def on_fetch(request):
    # 只处理 POST 请求（测试接口）
    if request.method == 'POST':
        target_url = 'https://hahavending.com'
        results = [
            test_http_ping(target_url),
            test_dns_resolution(target_url),
            test_image_upload(target_url),
            test_video_upload(target_url)
        ]
        # 返回 JSON 结果
        import json
        return new Response(
            json.dumps({'results': results}),