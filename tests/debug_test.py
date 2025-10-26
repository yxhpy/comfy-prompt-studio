#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试测试脚本 - 测试图片生成流程"""

import os
import sys
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.prompt.generator import generate_prompt
from src.core.comfyui.client import generate_image_with_comfyui

def test_prompt_generation():
    """测试提示词生成"""
    print("=" * 50)
    print("测试提示词生成...")
    print("=" * 50)

    try:
        test_input = "一个美女"
        print(f"输入: {test_input}")
        positive, negative = generate_prompt(test_input)
        print(f"\n正面提示词: {positive[:100]}...")
        print(f"\n负面提示词: {negative[:100]}...")
        print("\n[OK] 提示词生成成功")
        return positive, negative
    except Exception as e:
        print(f"\n[FAIL] 提示词生成失败: {e}")
        traceback.print_exc()
        return None, None

def test_comfyui_connection():
    """测试ComfyUI连接"""
    print("\n" + "=" * 50)
    print("测试ComfyUI连接...")
    print("=" * 50)

    try:
        import requests
        response = requests.get("http://127.0.0.1:8188/system_stats", timeout=5)
        if response.status_code == 200:
            print("[OK] ComfyUI服务器连接成功")
            return True
        else:
            print(f"[FAIL] ComfyUI返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] ComfyUI连接失败: {e}")
        traceback.print_exc()
        return False

def test_image_generation():
    """测试图片生成"""
    print("\n" + "=" * 50)
    print("测试图片生成...")
    print("=" * 50)

    try:
        # 使用简单的提示词测试
        positive = "a beautiful woman, portrait, high quality"
        negative = "blurry, low quality"

        print(f"正面提示词: {positive}")
        print(f"负面提示词: {negative}")
        print("\n开始生成图片...")

        images = generate_image_with_comfyui(positive, negative)
        print(f"\n[OK] 图片生成成功! 共生成 {len(images)} 张图片")
        print(f"  第一张图片大小: {len(images[0])} bytes")
        return True
    except Exception as e:
        print(f"\n[FAIL] 图片生成失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始诊断测试...\n")

    # 测试ComfyUI连接
    comfyui_ok = test_comfyui_connection()

    if not comfyui_ok:
        print("\n请确保ComfyUI服务器正在运行在 http://127.0.0.1:8188")
        sys.exit(1)

    # 测试提示词生成
    positive, negative = test_prompt_generation()

    if not positive:
        print("\n请确保Ollama服务器正在运行，并且有 huihui_ai/qwen3-abliterated:30b 模型")
        sys.exit(1)

    # 测试图片生成
    test_image_generation()

    print("\n" + "=" * 50)
    print("诊断测试完成")
    print("=" * 50)
