from flask import Flask, render_template, request, jsonify, send_file, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
import threading
import queue
import os
import time
import uuid
import random
from dotenv import load_dotenv
from test import generate_image_with_comfyui
from generator_prompt import generate_prompt
from history_manager import history_manager, generate_prompt_id

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB
app.config['UPLOAD_FOLDER'] = 'upload'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    'prompt_id': None,  # 当前提示词的ID
    'positive_prompt': None,  # 保存生成的正面提示词
    'negative_prompt': None,  # 保存生成的负面提示词
    'image_path': None,  # 用户上传的图片路径
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

            # 保存提示词到全局状态和历史记录
            current_generation['positive_prompt'] = positive_prompt
            current_generation['negative_prompt'] = negative_prompt

            # 添加或更新历史记录
            prompt_id = history_manager.add_record(
                current_generation['current_prompt'],
                positive_prompt,
                negative_prompt,
                current_generation['width'],
                current_generation['height']
            )
            current_generation['prompt_id'] = prompt_id

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
                height=current_generation['height'],
                image_path=current_generation['image_path']
            )

            # Save images
            for idx, image_data in enumerate(images):
                filename = f"{uuid.uuid4().hex}.png"
                # 新的路径结构: static/generated/[prompt_id]/filename.png
                prompt_dir = os.path.join('static', 'generated', current_generation['prompt_id'])
                os.makedirs(prompt_dir, exist_ok=True)

                filepath = os.path.join(prompt_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(image_data)

                # 图片文件名包含prompt_id路径
                image_path = f"{current_generation['prompt_id']}/{filename}"
                current_generation['images'].append(image_path)
                current_generation['generated_count'] += 1

                # 更新历史记录中的图片列表
                history_manager.update_images(current_generation['prompt_id'], filename)

                print(f"Generated image {current_generation['generated_count']}/{current_generation['total_count']}: {image_path}", flush=True)

                # Emit new image with updated progress
                print(f"Emitting new_image event: {image_path}", flush=True)
                socketio.emit('new_image', {
                    'filename': image_path,
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

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有文件被上传'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 为避免文件名冲突，使用UUID前缀
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        # 确保upload目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        return jsonify({
            'success': True,
            'filename': unique_filename,
            'filepath': filepath
        })
    else:
        return jsonify({'success': False, 'message': '不支持的文件类型'})

@app.route('/api/start', methods=['POST'])
def start_generation():
    """Start or continue image generation"""
    data = request.json
    user_prompt = data.get('prompt')
    count = data.get('count', 10)
    width = data.get('width', 800)  # Get width from request
    height = data.get('height', 1200)  # Get height from request
    image_path = data.get('image_path')  # Get image path from request

    # Update or reset state
    if user_prompt and user_prompt != current_generation['current_prompt']:
        # New prompt - reset everything
        current_generation['current_prompt'] = user_prompt
        current_generation['width'] = width  # Update width
        current_generation['height'] = height  # Update height
        current_generation['image_path'] = image_path  # Update image path
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
        'image_path': current_generation['image_path'],
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
    filename = data.get('filename')  # 格式: prompt_id/image.png

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

            # 从历史记录中移除
            parts = filename.split('/')
            if len(parts) == 2:
                prompt_id, image_name = parts
                history_manager.remove_image(prompt_id, image_name)

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

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取所有历史记录"""
    records = history_manager.get_all_records()
    return jsonify({
        'success': True,
        'records': records
    })

@app.route('/api/history/<prompt_id>', methods=['GET'])
def get_history_by_id(prompt_id):
    """根据ID获取历史记录"""
    record = history_manager.get_record_by_id(prompt_id)
    if record:
        return jsonify({
            'success': True,
            'record': record
        })
    else:
        return jsonify({'success': False, 'message': '记录不存在'})

@app.route('/api/history/<prompt_id>', methods=['DELETE'])
def delete_history(prompt_id):
    """删除历史记录"""
    try:
        # 删除该提示词的所有图片文件
        prompt_dir = os.path.join('static', 'generated', prompt_id)
        if os.path.exists(prompt_dir):
            import shutil
            shutil.rmtree(prompt_dir)

        # 删除历史记录
        history_manager.delete_record(prompt_id)

        return jsonify({'success': True})
    except Exception as e:
        print(f"删除历史记录失败: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/switch_prompt', methods=['POST'])
def switch_prompt():
    """切换到历史提示词"""
    data = request.json
    prompt_id = data.get('prompt_id')

    if not prompt_id:
        return jsonify({'success': False, 'message': '缺少prompt_id参数'})

    record = history_manager.get_record_by_id(prompt_id)
    if not record:
        return jsonify({'success': False, 'message': '历史记录不存在'})

    # 更新当前生成状态
    current_generation['current_prompt'] = record['prompt']
    current_generation['prompt_id'] = prompt_id
    current_generation['positive_prompt'] = record['positive_prompt']
    current_generation['negative_prompt'] = record['negative_prompt']
    current_generation['width'] = record['width']
    current_generation['height'] = record['height']
    current_generation['images'] = [f"{prompt_id}/{img}" for img in record.get('images', [])]
    current_generation['generated_count'] = len(current_generation['images'])
    # 重置 total_count，确保可以继续生成
    current_generation['total_count'] = current_generation['generated_count']

    return jsonify({
        'success': True,
        'record': record,
        'images': current_generation['images']
    })

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
