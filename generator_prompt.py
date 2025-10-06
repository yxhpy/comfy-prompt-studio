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
- 提示词中，先一句英语描述主要内容，任务时间地点事件等，再分词描述细节，每个分词之间用逗号隔开

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
        "一个韩国空姐在客机上面和机长做爱，机长阴茎插入空姐的阴部。全景照，精致的配饰，卷发， 长发，穿着红底高跟，穿着丝袜，身材九头身，中等乳房大小。 ",
         stream=True)
    print(positive_prompt)
    print(negative_prompt)
