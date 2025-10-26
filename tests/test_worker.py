#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试worker线程"""

import sys
import time
import threading
from test import generate_image_with_comfyui
from generator_prompt import generate_prompt

# 模拟current_generation状态
current_generation = {
    'is_running': True,
    'current_prompt': 'test',
    'total_count': 1,
    'generated_count': 0,
    'images': [],
    'thread': None,
    'stop_flag': False
}

def worker_thread():
    """Background worker to generate images"""
    print(f"Worker thread started")
    print(f"current_generation: {current_generation}")

    while current_generation['is_running']:
        try:
            if current_generation['stop_flag']:
                print("Stop flag detected")
                break

            print(f"Generating prompt for: {current_generation['current_prompt']}")

            # Generate image
            positive_prompt, negative_prompt = generate_prompt(current_generation['current_prompt'])

            print(f"Starting generation {current_generation['generated_count'] + 1}/{current_generation['total_count']}")
            print(f"Positive: {positive_prompt[:50]}...")
            print(f"Negative: {negative_prompt[:50]}...")

            # Generate image using ComfyUI
            images = generate_image_with_comfyui(positive_prompt, negative_prompt)

            print(f"Generated {len(images)} images")

            # 保存图片
            import os
            import uuid
            for idx, image_data in enumerate(images):
                filename = f"output_{uuid.uuid4().hex}.png"
                filepath = os.path.join('static', 'generated', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                with open(filepath, 'wb') as f:
                    f.write(image_data)

                current_generation['images'].append(filename)
                current_generation['generated_count'] += 1

                print(f"Generated image {current_generation['generated_count']}/{current_generation['total_count']}: {filename}")

            # Check if target count reached
            if current_generation['generated_count'] >= current_generation['total_count']:
                current_generation['is_running'] = False
                print(f"Generation complete! Total: {current_generation['generated_count']}")
                break

        except Exception as e:
            print(f"Error generating image: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(1)

if __name__ == "__main__":
    print("Testing worker thread...")

    thread = threading.Thread(target=worker_thread)
    thread.daemon = True
    thread.start()

    # Wait for thread to finish
    thread.join(timeout=120)

    print(f"\nFinal state:")
    print(f"  Generated: {current_generation['generated_count']}")
    print(f"  Images: {current_generation['images']}")
