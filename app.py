from flask import Flask, render_template, request, jsonify, send_file, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import queue
import os
import time
import uuid
import random
from dotenv import load_dotenv
from test import generate_image_with_comfyui
from generator_prompt import generate_prompt

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

# Track connected clients
connected_clients = set()

@socketio.on('connect')
def handle_connect():
    connected_clients.add(request.sid)
    join_room('generation')
    print(f"Client connected: {request.sid}, Total clients: {len(connected_clients)}", flush=True)

@socketio.on('disconnect')
def handle_disconnect():
    connected_clients.discard(request.sid)
    leave_room('generation')
    print(f"Client disconnected: {request.sid}, Total clients: {len(connected_clients)}", flush=True)

# Global state
generation_queue = queue.Queue()
current_generation = {
    'is_running': False,
    'current_prompt': None,
    'width': 800,  # Default width
    'height': 1200,  # Default height
    'total_count': 10,
    'generated_count': 0,
    'images': [],
    'stop_flag': False
}


def worker_thread():
    """Background worker to generate images"""
    print("=" * 50, flush=True)
    print("WORKER THREAD STARTED", flush=True)
    print("=" * 50, flush=True)

    while current_generation['is_running']:
        try:
            if current_generation['stop_flag']:
                break

            # Update progress - generating prompt
            print(f"Emitting progress (generating prompt): {current_generation['generated_count']}/{current_generation['total_count']}", flush=True)
            socketio.emit('progress', {
                'current': current_generation['generated_count'],
                'total': current_generation['total_count'],
                'status': 'generating_prompt'
            }, room='generation')

            # 定义日志回调函数，用于实时发送日志到前端
            def log_callback(message):
                """实时发送日志到前端"""
                socketio.emit('log', {'message': message}, room='generation')

            # Generate prompt (with cache) - 使用 stream 模式
            positive_prompt, negative_prompt = generate_prompt(
                current_generation['current_prompt'],
                stream=True,
                log_callback=log_callback
            )            

            # Update progress - generating image
            print(f"Emitting progress (generating image): {current_generation['generated_count']}/{current_generation['total_count']}", flush=True)
            socketio.emit('progress', {
                'current': current_generation['generated_count'],
                'total': current_generation['total_count'],
                'status': 'generating_image'
            }, room='generation')

            print(f"Starting generation {current_generation['generated_count'] + 1}/{current_generation['total_count']}", flush=True)

            # Generate image using ComfyUI
            images = generate_image_with_comfyui(
                positive_prompt,
                negative_prompt,
                width=current_generation['width'],
                height=current_generation['height']
            )

            # Save images
            for idx, image_data in enumerate(images):
                filename = f"output_{uuid.uuid4().hex}.png"
                filepath = os.path.join('static', 'generated', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                with open(filepath, 'wb') as f:
                    f.write(image_data)

                current_generation['images'].append(filename)
                current_generation['generated_count'] += 1

                print(f"Generated image {current_generation['generated_count']}/{current_generation['total_count']}: {filename}", flush=True)

                # Emit new image with updated progress
                print(f"Emitting new_image event: {filename}", flush=True)
                socketio.emit('new_image', {
                    'filename': filename,
                    'current': current_generation['generated_count'],
                    'total': current_generation['total_count']
                }, room='generation')

                # Update progress bar
                print(f"Emitting progress event: {current_generation['generated_count']}/{current_generation['total_count']}", flush=True)
                socketio.emit('progress', {
                    'current': current_generation['generated_count'],
                    'total': current_generation['total_count'],
                    'status': 'generating'
                }, room='generation')

            # Check if target count reached
            if current_generation['generated_count'] >= current_generation['total_count']:
                current_generation['is_running'] = False
                print(f"Emitting generation_complete event", flush=True)
                socketio.emit('generation_complete', {
                    'total': current_generation['generated_count']
                }, room='generation')
                print(f"Generation complete! Total: {current_generation['generated_count']}", flush=True)
                break

        except Exception as e:
            print(f"Error generating image: {e}", flush=True)
            import traceback
            traceback.print_exc()
            print(f"Emitting error event: {str(e)}", flush=True)
            socketio.emit('error', {'message': str(e)}, room='generation')
            time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test_emit', methods=['POST'])
def test_emit():
    """Test emit from request context"""
    socketio.emit('test_message', {'message': 'Test from API'}, room='generation')
    return jsonify({'success': True})

@app.route('/api/start', methods=['POST'])
def start_generation():
    """Start or continue image generation"""
    data = request.json
    user_prompt = data.get('prompt')
    count = data.get('count', 10)
    width = data.get('width', 800)  # Get width from request
    height = data.get('height', 1200)  # Get height from request

    # Update or reset state
    if user_prompt and user_prompt != current_generation['current_prompt']:
        # New prompt - reset everything
        current_generation['current_prompt'] = user_prompt
        current_generation['width'] = width  # Update width
        current_generation['height'] = height  # Update height
        current_generation['total_count'] = count
        current_generation['generated_count'] = 0
        current_generation['images'] = []
    else:
        # Same prompt - increase count
        current_generation['total_count'] += count

    # Start generation if not running
    if not current_generation['is_running']:
        print(f"Starting worker thread for prompt: {current_generation['current_prompt']}", flush=True)
        current_generation['is_running'] = True
        current_generation['stop_flag'] = False
        thread = threading.Thread(target=worker_thread, daemon=True)
        thread.start()
        print(f"Worker thread started successfully", flush=True)
    else:
        print(f"Worker thread already running", flush=True)

    return jsonify({
        'success': True,
        'current_prompt': current_generation['current_prompt'],
        'total_count': current_generation['total_count']
    })

@app.route('/api/stop', methods=['POST'])
def stop_generation():
    """Stop image generation"""
    current_generation['stop_flag'] = True
    current_generation['is_running'] = False
    return jsonify({'success': True})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current generation status"""
    return jsonify({
        'is_running': current_generation['is_running'],
        'current_prompt': current_generation['current_prompt'],
        'width': current_generation['width'],
        'height': current_generation['height'],
        'total_count': current_generation['total_count'],
        'generated_count': current_generation['generated_count'],
        'images': current_generation['images']
    })

def get_preset_prompts():
    """从环境变量读取预设提示词"""
    prompts = []
    i = 1
    while True:
        prompt_key = f'PROMPT_{i}'
        prompt_value = os.getenv(prompt_key)
        if prompt_value:
            prompts.append(prompt_value)
            i += 1
        else:
            break
    return prompts

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    """获取预设提示词列表"""
    prompts = get_preset_prompts()
    if not prompts:
        return jsonify({'success': False, 'message': '没有找到预设提示词'})

    # 随机返回一个提示词
    selected_prompt = random.choice(prompts)
    return jsonify({
        'success': True,
        'prompt': selected_prompt,
        'all_prompts': prompts
    })

@app.route('/api/delete_image', methods=['POST'])
def delete_image():
    """删除指定的图片"""
    data = request.json
    filename = data.get('filename')

    if not filename:
        return jsonify({'success': False, 'message': '缺少文件名参数'})

    try:
        # 从图片列表中移除
        if filename in current_generation['images']:
            current_generation['images'].remove(filename)
            current_generation['generated_count'] = len(current_generation['images'])

            # 删除物理文件
            file_path = os.path.join('static', 'generated', filename)
            if os.path.exists(file_path):
                os.remove(file_path)

            return jsonify({
                'success': True,
                'remaining_count': len(current_generation['images']),
                'images': current_generation['images']
            })
        else:
            return jsonify({'success': False, 'message': '图片不存在'})
    except Exception as e:
        print(f"删除图片失败: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/add_more', methods=['POST'])
def add_more():
    """Add more images to generation queue (triggered by scroll)"""
    data = request.json
    additional_count = data.get('count', 10)

    current_generation['total_count'] += additional_count

    # Start generation if not running
    if not current_generation['is_running'] and current_generation['current_prompt']:
        current_generation['is_running'] = True
        current_generation['stop_flag'] = False
        thread = threading.Thread(target=worker_thread, daemon=True)
        thread.start()

    return jsonify({
        'success': True,
        'new_total': current_generation['total_count']
    })

if __name__ == '__main__':
    # Create static/generated directory
    os.makedirs('static/generated', exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
