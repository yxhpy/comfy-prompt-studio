import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_status():
    """测试状态 API"""
    print("=== 测试状态 API ===")
    response = requests.get(f"{BASE_URL}/api/status")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_start_generation():
    """测试启动生成 API"""
    print("=== 测试启动生成 API ===")
    data = {
        "prompt": "beautiful mountain landscape with lake",
        "count": 1
    }
    response = requests.post(
        f"{BASE_URL}/api/start",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    return response.json()

def test_stop_generation():
    """测试停止生成 API"""
    print("=== 测试停止生成 API ===")
    response = requests.post(f"{BASE_URL}/api/stop")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_add_more():
    """测试添加更多 API"""
    print("=== 测试添加更多 API ===")
    data = {"count": 5}
    response = requests.post(
        f"{BASE_URL}/api/add_more",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    # 测试初始状态
    test_status()

    # 测试启动生成
    result = test_start_generation()

    # 等待 3 秒
    print("等待 3 秒...")
    time.sleep(3)

    # 再次查看状态
    test_status()

    # 测试添加更多
    test_add_more()

    # 等待 2 秒
    print("等待 2 秒...")
    time.sleep(2)

    # 测试停止
    test_stop_generation()

    # 查看最终状态
    test_status()

    print("✅ API 测试完成!")
