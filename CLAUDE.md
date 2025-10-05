# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI image generation web application that integrates ComfyUI workflow execution with Ollama-based prompt enhancement. It provides a mobile-optimized UI for continuous image generation with real-time progress updates.

## Architecture

The application follows a three-layer architecture:

1. **Prompt Generation Layer** (`generator_prompt.py`)
   - Uses Ollama API (localhost:11434) with model `huihui_ai/qwen3-abliterated:30b`
   - Converts user requirements into detailed positive/negative prompts for image generation
   - Returns structured prompts in XML-tagged format

2. **ComfyUI Integration Layer** (`test.py`)
   - Interfaces with ComfyUI API (127.0.0.1:8188)
   - Loads workflow from `flow.json` and injects generated prompts into nodes "3" (positive) and "4" (negative)
   - Polls `/history/{prompt_id}` endpoint until generation completes
   - Retrieves generated images via `/view` endpoint
   - Key function: `generate_image_with_comfyui(positive_prompt, negative_prompt, workflow_path="flow.json")`

3. **Web Application Layer** (`app.py`)
   - Flask server with flask-socketio for real-time WebSocket communication
   - Background worker thread for async image generation
   - Manages generation queue and state in global `current_generation` dict
   - Images saved to `static/generated/` with UUID-based filenames

## Key Data Flow

```
User Input → Ollama Prompt Generation → ComfyUI Workflow Execution → WebSocket Push → Frontend Display
```

1. User submits requirement via `/api/start`
2. `generate_prompt()` enhances user input into detailed prompts
3. `worker_thread()` loops, calling `generate_image_with_comfyui()` for each image
4. Each generated image triggers `socketio.emit('new_image')` to frontend
5. Progress updates sent via `socketio.emit('progress')`
6. Frontend auto-triggers more generations when scrolled to 1/2 of current images via `/api/add_more`

## Running the Application

**Prerequisites:**
- ComfyUI server running on 127.0.0.1:8188
- Ollama server running on localhost:11434 with model `huihui_ai/qwen3-abliterated:30b`

**Start the application:**
```bash
python app.py
```
Access at: http://localhost:5000 (or http://0.0.0.0:5000)

**Test API endpoints:**
```bash
python test_api.py
```

**Test standalone generation:**
```bash
python test.py
```

## API Endpoints

- `POST /api/start` - Start/continue generation (params: `prompt`, `count`)
- `POST /api/stop` - Stop current generation
- `GET /api/status` - Get current state (is_running, generated_count, images, etc.)
- `POST /api/add_more` - Increase total_count and resume generation (params: `count`)

## WebSocket Events

**Outgoing (server → client):**
- `new_image` - Emitted when image generated (data: filename, current, total)
- `progress` - Progress update (data: current, total, status)
- `generation_complete` - All images generated (data: total)
- `error` - Generation error (data: message)

## Critical Implementation Notes

1. **SocketIO Compatibility**: Do NOT use `broadcast=True` parameter in `socketio.emit()` calls - it's not supported by this version of flask-socketio. Emit without broadcast parameter.

2. **Thread Safety**: `current_generation` dict is accessed by both Flask routes and worker thread. Use `stop_flag` for graceful shutdown.

3. **Progress Bar Display**: Frontend progress bar requires explicit `progressBar.style.display = 'block'` in addition to `classList.add('active')` to ensure visibility.

4. **Workflow Node IDs**: The workflow JSON uses nodes "3" and "4" for positive/negative prompts. Verify these IDs if workflow is modified.

5. **Auto-trigger Logic**: Intersection Observer monitors `scrollTrigger` element. When user scrolls to 1/2 of generated images, `autoTriggerEnabled` flag prevents duplicate triggers until generation completes.

## File Structure

- `app.py` - Flask server with WebSocket and worker thread
- `test.py` - ComfyUI API integration
- `generator_prompt.py` - Ollama prompt generation
- `flow.json` - ComfyUI workflow definition
- `templates/index.html` - Mobile-optimized frontend UI
- `test_api.py` - API endpoint tests
- `static/generated/` - Generated images directory (auto-created)

## Dependencies

Install via: `pip install -r requirements.txt`
- flask==3.0.0
- flask-socketio==5.3.5
- requests==2.31.0
- websocket-client==1.7.0
- python-socketio==5.10.0
