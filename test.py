import requests
import json
import uuid
import websocket
import time
from generator_prompt import generate_prompt

def chat_with_ollama(model_name, prompt, stream=False):
    """
    Call Ollama API to chat with a model

    Args:
        model_name: Name of the model
        prompt: The prompt/question to send to the model
        stream: Whether to stream the response

    Returns:
        The model's response
    """
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": stream
    }

    response = requests.post(url, json=payload)

    if stream:
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if 'response' in json_response:
                    chunk = json_response['response']
                    print(chunk, end='', flush=True)
                    full_response += chunk
        print()
        return full_response
    else:
        result = response.json()
        return result.get('response', '')


def queue_prompt(prompt_workflow, server_address="127.0.0.1:8188"):
    """
    Submit a workflow to ComfyUI queue

    Args:
        prompt_workflow: The workflow JSON object
        server_address: ComfyUI server address

    Returns:
        prompt_id and other response data
    """
    p = {"prompt": prompt_workflow, "client_id": str(uuid.uuid4())}
    data = json.dumps(p).encode('utf-8')

    url = f"http://{server_address}/prompt"
    response = requests.post(url, data=data, headers={'Content-Type': 'application/json'})

    return response.json()


def get_image(filename, subfolder, folder_type, server_address="127.0.0.1:8188"):
    """
    Get generated image from ComfyUI

    Args:
        filename: Name of the image file
        subfolder: Subfolder path
        folder_type: Type of folder
        server_address: ComfyUI server address

    Returns:
        Image data
    """
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url = f"http://{server_address}/view"
    response = requests.get(url, params=data)
    return response.content


def get_history(prompt_id, server_address="127.0.0.1:8188"):
    """
    Get generation history

    Args:
        prompt_id: The prompt ID
        server_address: ComfyUI server address

    Returns:
        History data
    """
    url = f"http://{server_address}/history/{prompt_id}"
    response = requests.get(url)
    return response.json()


def generate_image_with_comfyui(positive_prompt, negative_prompt, workflow_path="flowv1.json", server_address="127.0.0.1:8188"):
    """
    Generate image using ComfyUI workflow

    Args:
        positive_prompt: Positive prompt text
        negative_prompt: Negative prompt text
        workflow_path: Path to workflow JSON file
        server_address: ComfyUI server address

    Returns:
        Generated image data
    """
    import random

    # Load workflow
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    # Update prompts in workflow
    if "3" in workflow:
        workflow["3"]["inputs"]["text"] = positive_prompt
    if "4" in workflow:
        workflow["4"]["inputs"]["text"] = negative_prompt

    # Update all seeds to random values
    if "5" in workflow and "inputs" in workflow["5"] and "seed" in workflow["5"]["inputs"]:
        new_seed_5 = random.randint(0, 999999999999999)
        workflow["5"]["inputs"]["seed"] = new_seed_5
        print(f"🎲 随机种子(节点5): {new_seed_5}", flush=True)

    if "11" in workflow and "inputs" in workflow["11"] and "seed" in workflow["11"]["inputs"]:
        new_seed_11 = random.randint(0, 999999999999999)
        workflow["11"]["inputs"]["seed"] = new_seed_11
        print(f"🎲 随机种子(节点11): {new_seed_11}", flush=True)

    # Queue the prompt
    response = queue_prompt(workflow, server_address)
    prompt_id = response['prompt_id']

    print(f"Queued prompt with ID: {prompt_id}")

    # Wait for completion
    while True:
        history = get_history(prompt_id, server_address)
        if prompt_id in history:
            break
        time.sleep(1)

    # Get the generated images
    history_data = history[prompt_id]
    images = []

    for node_id in history_data['outputs']:
        node_output = history_data['outputs'][node_id]
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(
                    image['filename'],
                    image['subfolder'],
                    image['type'],
                    server_address
                )
                images.append(image_data)

    return images


if __name__ == "__main__":
    positive_prompt, negative_prompt = generate_prompt("一个韩国精致面容老师在教室中穿着丝袜，站起来能看到高跟鞋，穿着骚气的情趣内衣，精美饰品装饰了脸部，特写阴唇，美腿，9头身")
    print(positive_prompt)
    print(negative_prompt)
    # Generate image
    images = generate_image_with_comfyui(positive_prompt, negative_prompt)
    # Save images
    for idx, image_data in enumerate(images):
        with open(f"output_{idx}.png", "wb") as f:
            f.write(image_data)
        print(f"Saved output_{idx}.png")
