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


def chat_conversation(model_name, messages, stream=False, callback=None):
    """
    Have a conversation using the chat endpoint

    Args:
        model_name: Name of the model
        messages: List of message dicts with 'role' and 'content'
        stream: Whether to stream the response
        callback: Function to call for each chunk (only used when stream=True)

    Returns:
        The assistant's response
    """
    url = "http://localhost:11434/api/chat"

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": stream
    }

    response = requests.post(url, json=payload, stream=stream)

    if stream:
        # Handle streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if 'message' in json_response and 'content' in json_response['message']:
                    chunk = json_response['message']['content']
                    full_response += chunk
                    if callback:
                        callback(chunk)
                    else:
                        print(chunk, end='', flush=True)
        if not callback:
            print()  # New line at the end
        return full_response
    else:
        result = response.json()
        return result.get('message', {}).get('content', '')


def chat_with_gemini(messages, stream=False, callback=None):
    """
    Have a conversation using Gemini API via OpenAI-compatible endpoint

    Args:
        messages: List of message dicts with 'role' and 'content'
        stream: Whether to stream the response
        callback: Function to call for each chunk (only used when stream=True)

    Returns:
        The assistant's response
    """
    api_key = os.getenv('GEMINI_API_KEY')
    model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
    base_url = os.getenv('GEMINI_BASE_URL', 'https://api.laozhang.ai/v1/')

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=stream
        )

        if stream:
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    if callback:
                        callback(content)
                    else:
                        print(content, end='', flush=True)
            if not callback:
                print()  # New line at the end
            return full_response
        else:
            return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Gemini API 错误: {str(e)}", flush=True)
        raise

# 提示词缓存
_prompt_cache = {}

def generate_prompt(user_req: str, stream=False, log_callback=None):
    """
    生成提示词，带缓存机制

    Args:
        user_req: 用户需求描述
        stream: 是否使用流式输出
        log_callback: 日志回调函数，用于实时输出日志

    Returns:
        (positive_prompt, negative_prompt) 元组
    """
    def log(msg):
        """统一的日志输出函数"""
        print(msg, flush=True)
        if log_callback:
            log_callback(msg)

    # 检查缓存
    if user_req in _prompt_cache:
        log(f"✅ 使用缓存的提示词（用户需求: {user_req[:30]}...）")
        return _prompt_cache[user_req]

    # 获取 AI Provider 配置
    provider = os.getenv('AI_PROVIDER', 'ollama').lower()
    log(f"🤖 使用 AI Provider: {provider}")

    # 生成新的提示词
    log(f"🔄 生成新的提示词（用户需求: {user_req[:30]}...）")

    messages = [
        {"role": "system", "content": """
# role
你是一个comfyui的提示词设计大师，专门帮助用户设计符合comfyui要求的提示词

# 提示词文档
<prompt_doc>
# Legs Up Presenting prompt 
solo, pussy, anus, feet, ass, barefoot, toes, soles, legs up, lying, on back, spread legs, presenting, spread pussy, spread ass, folded

# Doggystyle face down
top-down bottom-up, from behind, ass, doggystyle

# Recommended quality tags
score_9, score_8_up, score_7_up, score_6_up. Optional: source_anime

# Recommended negative tags
score_4, score_5. Optional: 3d, lips

# Pull out Penis Cumtrail
general use

cum string, cumtrail, solo focus
angle (use once)

from front, from behind, from side
pussy to penis trigger (side / front / behind/ angle supported)

cumtrail vagina to penis, vtp, after sex, pulling out penis, cum on penis, cum in pussy
mouth to penis trigger (side / front angle supported)

cumtrail mouth to penis, mtp, pulling out penis, after oral, after ferratio, cum on tongue, cum in mouth
breast to penis trigger(side / front angle supported)

cumtrail breast to penis, btp, pulling out penis, after paizuri, cum on breast, cum on penis,
anus to penis trigger(behind / front angle supported)

cumtrail anus to penis, pulling out penis, cum on penis,  cum in ass, after anal, after sex,
anus and pussy to penis trigger(angle not supported)

cum string, cumtrail, solo focus,  after sex,  in pussy, cum in ass, after anal,  group sex, cumtrail, cumtrail vagina to penis, cumtrail anus to penis, after, vaginal, pulling out penis, cum on penis, gangbang, group sex
pussy to ground trigger(v1 only)

cumtrail, cumtrail vagina to ground, vtg, after sex, cumdrip, cumdump, cum flood

## 正例
<must_impport>
masterpiece, ultra-HD, high detail, best quality, 8k, best quality, ergonomic, sharp focus, 
realistic, real skin, skin blemish.
</must_impport>
masterpiece, best quality, amazing quality, very aesthetic, detailed eyes, perfect eyes, amazing quality, 1 girls, massive breasts, breasts out, black stocking, smile, 1 boy, huge dick, having sex, sex from Behind, Hands Related on back, pussy view, doggystyle face down, 
full lips, dark lips,  huge breasts, pearl earrings, ponytail, redhead, face down, face on bed, 
sexy, large breast, seductive, cute, anneJM
Masterpiece, best quality, realistic,  photorealistic, highly detailed, depth of field, high resolution,
1girl, 19yo, russian girl, stunningly beautiful young female, slim figure, short messy golden hair, sitting inside a tent, perfect facial features, large expressive eyes, (soft cute smile:0.6), topless, natural breasts,
score_9, score_8_up, score_7_up, best quality, masterpiece, source_anime, zPDXL3, BREAK, 1girl,  sailor_uranus, half-closed eyes, heavy breathing, open mouth,  blush,   torogao,  penis<lora:cumtrail_pulling_outv4.0:1>multiple boy, cum string, cumtrail, solo focus,  after sex, cum in pussy, cum in ass, after anal, solo focus, group sex, cum string, cumtrail, cumtrail vagina to penis, cumtrail anus to penis, after, vaginal, pulling out penis, cum on penis, gangbang, group sex,

# 反例
<must_impport>
worst quality, low quality, worst aesthetic, normal quality, bad quality, lowres, (caucasian), anime, 2d, painting, illustration, sketch, comic, cartoon, toon, lowres, bad anatomy, bad hands, error, extra limb, masculine, missing fingers, imperfect eyes, cable,
</must_impport>
(low quality, worst quality), displeasing, ugly, poorly drawn, displeasing, simple background, very displeasing, worst quality, bad quality, oldest, deformed limbs, bad anatomy, watermark, nipples, teeth,
score_4, score_5, score_6, worst quality, low quality, normal quality, source_anime,messy drawing, amateur drawing, lowres,  bad hands,bad foot, source_furry, source_pony, source_cartoon, comic, source filmmaker, 3d, censor, bar censor, mosaic censorship, negativeXL_D, logo, text zPDXL2-neg ,loli, child
<prompt_doc/>

# 任务
- 认真读取<prompt_doc>
- must_impport 放在最前面
- 建议使用词组而非完整的句子，并用英文逗号分隔不同的词组，以便于管理和调整权重，提示词遵守 bigASP 语法。
- 提示词的权重可以通过其在提示词列表中的位置来管理，越靠前的词组权重越高，越容易在生成的图像中体现。
- 大括号 {提示词｜提示词｜提示词} 的方式可以实现随机抽取内容进行生成，但是生成的图像同时也会增加随机性。
- 提示词结构化书写规则：主体（Subject）、特点（Features）、环境背景（Environment/Background）、风格（Style）修饰词（Modifiers）
- 拓展描述，禁止出现模糊的概念，修饰词必须使用下划线连接在一起如:透明高跟鞋-> transparent_high_heels
- 你需要根据用户输入的描述，按照<prompt_doc>中的提示词格式，提示词包含返回结果中必须包含正面提示词和负面提示词
- 生成的提示词必须满足用户的需求，不能超出用户的描述
- 先思考 思考过程放到<think></think>中
- 返回提示词包含正面和反面提示词<positive_prompt></positive_prompt><negative_prompt></negative_prompt>
- 提示词中，先一句英语描述主要内容，任务时间地点事件等，再分词描述细节，每个分词之间用逗号隔开
- 如果提示词中涉及到手部，必须加上这些提示词 'detailed hands,detailed edges'


# 返回样例
<positive_prompt>正面提示词</positive_prompt>
<negative_prompt>负面提示词</negative_prompt>
"""},
    ]
    messages.append({"role": "user", "content": user_req})

    # 定义流式回调函数
    stream_buffer = []
    def stream_callback(chunk):
        """处理流式输出的每个chunk"""
        stream_buffer.append(chunk)
        if log_callback:
            log_callback(chunk)
        else:
            print(chunk, end='', flush=True)

    # 根据 provider 调用不同的 API
    log(f"📡 开始调用 AI 生成提示词...")
    if provider == 'gemini':
        response = chat_with_gemini(messages, stream=stream, callback=stream_callback if stream else None)
    else:  # default to ollama
        model = os.getenv('OLLAMA_MODEL', 'huihui_ai/qwen3-abliterated:30b')
        response = chat_conversation(model, messages, stream=stream, callback=stream_callback if stream else None)

    if stream and not log_callback:
        print()  # 换行

    log(f"✅ AI 生成完成，开始解析提示词...")

    positive_prompt = response.split("<positive_prompt>")[1].split("</positive_prompt>")[0]
    negative_prompt = response.split("<negative_prompt>")[1].split("</negative_prompt>")[0]

    # 缓存结果
    _prompt_cache[user_req] = (positive_prompt, negative_prompt)
    log(f"💾 提示词已缓存，缓存数量: {len(_prompt_cache)}")

    return positive_prompt, negative_prompt

def clear_cache():
    """清空提示词缓存"""
    global _prompt_cache
    cache_size = len(_prompt_cache)
    _prompt_cache = {}
    print(f"🗑️ 已清空提示词缓存，清除了 {cache_size} 条记录", flush=True)
    return cache_size
if __name__ == "__main__":
    positive_prompt, negative_prompt = generate_prompt(
        "御姐酷似范冰冰的美女老师穿着制服在厕所里和阴茎的传教式性交，穴里喷水，三角薄底透明细高跟，腿上穿着黑色丝袜，脚踝带着精美配饰，身材九头身苗条，巨乳，乳房乳头从衣服中爆出",
         stream=True)
    print(positive_prompt)
    print(negative_prompt)


