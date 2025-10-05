import requests
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def chat_with_ollama(model_name, prompt, stream=False):
    """
    Call Ollama API to chat with a model

    Args:
        model_name: Name of the model (e.g., 'huihui_ai/qwen3-abliterated:30b')
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
        # Handle streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if 'response' in json_response:
                    chunk = json_response['response']
                    print(chunk, end='', flush=True)
                    full_response += chunk
        print()  # New line at the end
        return full_response
    else:
        # Handle non-streaming response
        result = response.json()
        return result.get('response', '')


def chat_conversation(model_name, messages):
    """
    Have a conversation using the chat endpoint

    Args:
        model_name: Name of the model
        messages: List of message dicts with 'role' and 'content'

    Returns:
        The assistant's response
    """
    url = "http://localhost:11434/api/chat"

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False
    }

    response = requests.post(url, json=payload)
    result = response.json()

    return result.get('message', {}).get('content', '')


def chat_with_gemini(messages):
    """
    Have a conversation using Gemini API via OpenAI-compatible endpoint

    Args:
        messages: List of message dicts with 'role' and 'content'

    Returns:
        The assistant's response
    """
    api_key = os.getenv('GEMINI_API_KEY')
    model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.laozhang.ai/v1/"
    )

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Gemini API 错误: {str(e)}", flush=True)
        raise

# 提示词缓存
_prompt_cache = {}

def generate_prompt(user_req: str):
    """
    生成提示词，带缓存机制

    Args:
        user_req: 用户需求描述

    Returns:
        (positive_prompt, negative_prompt) 元组
    """
    # 检查缓存
    if user_req in _prompt_cache:
        print(f"✅ 使用缓存的提示词（用户需求: {user_req[:30]}...）", flush=True)
        return _prompt_cache[user_req]

    # 获取 AI Provider 配置
    provider = os.getenv('AI_PROVIDER', 'ollama').lower()
    print(f"🤖 使用 AI Provider: {provider}", flush=True)

    # 生成新的提示词
    print(f"🔄 生成新的提示词（用户需求: {user_req[:30]}...）", flush=True)

    messages = [
        {"role": "system", "content": """
# role
你是一个comfyui的提示词设计大师，专门帮助用户设计符合comfyui要求的提示词

# 正面-负面提示词样例
## group1
- (masterpiece,best quality,score_9, score_8_up, score_7_up:1),RAW,dynamic angle, sitting on a park bench,(night:1.5), 1girl,long hair,hair,make up,red lipstick,black eyes,air bangs,large breasts,bracelet,round earrings, blush,sexy,pose,posing,closeup,selfie, nipples,areolas,south korea idol,lace (see-through dress),necklace,jewelry,shoulder strap dress,breasts out,depth of field,bokeh
- (score_6,score_5,score_4,score_3, score_2, score_1:1),source_furry,source_pony,source_cartoon,female child dark-skinned female,day,(blurry:1.4),(blurred foreground)
## group2
- a asian woman wearing (hanfu:1.2), solo, nude,nipples, breasts, (chinese clothes:1.2), open clothes, breasts out,black hair, pale skin, hair ornament, bamboo, hair flower, flower, sitting, looking at viewer, long hair, long sleeves,nipples,areolas, bare shoulders, plant, lips, ass visible through thighs, sitting and spread legs,pussy,makeup,red lips,forest background
- female child, dark-skinned female, signature,username,text,watermark, illustration,3d,2d,painting,cartoons,sketch
## group3
- r/adorableporn, masterpiece, highres, best quality, highly detailed, 19yo petite girl lying, brunette, navel, (huge breasts:1.2), large vaginal penetration, missionary, man, veiny penis, side view, wild beach at night
- worst quality, low quality, 3d, 2d, painting, sketch, text, watermark, threesome, chubby, pov, blurry, latina
## group4
- she is giving a blowjob to a man's penis in a 69 position,face close-up,deepthroat,A 25-year-old cute Japanese woman,young, testicles close-up, a man, looking at viewer, male pubic hair, wide-eyed, testicles, eyelashes, female on top, oral, penis, from front, nude, breasts, solo focus, black hair, makeup, mascara, short hair,bangs
- pov crotch,pussy,full body,from side,sex,worst quality,low quality,lowres,illustration,3d,2d,painting,cartoons,anime,painting,CGI,3D render,bad anatomy,sketch,photoshop,airbrushed skin,overexposed,watermark,text,logo,label,blurry, blurry foreground
## group5
- score_7_up,Photo (from below:1.4),naked photo of an 18-year-old female korean idol ,pale skin,black eyes,small breasts, nipples, comfortable expression,solo, long hair, black hair, nude, navel, pussy, teeth,makeup,lipstick,(arms behind back:1.2), (peeing:1.4555),arms behind head, open mouth, red lips,blunt bangs,She squatted on the grass wearing high heels and peed, pee spurted from her pussy and (the floor was filled with her yellow urine), pee gushing out of her pussy,labia,clitoris,She urinates in front of the camera,knees up,m legs,looking at viewer, parted lips,collarbone,  teeth, open mouth, indoors,spread legs,ass visible through thighs,(pussy close-up:1.2),outdoors,park background, trees
- kneeling (score_6,score_5,score_4,score_3,score_2,score_1:1),dark-skinned female,source_furry,source_pony,source_cartoon,illustration,3d,2d,painting,cartoons,sketch,female child,signature,username,text,watermark,

# 任务
- 拓展描述，禁止出现模糊的概念，如美丽的脸部，这里需要清晰的描述脸部，鼻子眉毛耳朵等细节
- 你需要根据用户输入的描述，输出符合目标样例的提示词，提示词包含返回结果中必须包含正面提示词和负面提示词
- 生成的提示词必须满足用户的需求，不能超出用户的描述
- 先思考 思考过程放到<think></think>中
- 返回提示词包含正面和反面提示词<positive_prompt></positive_prompt><negative_prompt></negative_prompt>

# 返回样例
<positive_prompt>正面提示词</positive_prompt>
<negative_prompt>负面提示词</negative_prompt>
"""},
    ]
    messages.append({"role": "user", "content": user_req})

    # 根据 provider 调用不同的 API
    if provider == 'gemini':
        response = chat_with_gemini(messages)
    else:  # default to ollama
        model = os.getenv('OLLAMA_MODEL', 'huihui_ai/qwen3-abliterated:30b')
        response = chat_conversation(model, messages)

    positive_prompt = response.split("<positive_prompt>")[1].split("</positive_prompt>")[0]
    negative_prompt = response.split("<negative_prompt>")[1].split("</negative_prompt>")[0]

    # 缓存结果
    _prompt_cache[user_req] = (positive_prompt, negative_prompt)
    print(f"💾 提示词已缓存，缓存数量: {len(_prompt_cache)}", flush=True)

    return positive_prompt, negative_prompt

def clear_cache():
    """清空提示词缓存"""
    global _prompt_cache
    cache_size = len(_prompt_cache)
    _prompt_cache = {}
    print(f"🗑️ 已清空提示词缓存，清除了 {cache_size} 条记录", flush=True)
    return cache_size
if __name__ == "__main__":
    positive_prompt, negative_prompt = generate_prompt("一个精致面容美丽的韩国老师在教室中穿着丝袜，美丽的配饰，站起来能看到高跟鞋，穿着骚气的情趣内衣，精美饰品装饰了脸部，特写阴唇，美腿，9头身")
    print(positive_prompt)
    print(negative_prompt)
