from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from datetime import datetime, timedelta
import pandas as pd
import math
import re
from collections import Counter

from app_user_keyword.views import filter_dataFrame, api_get_top_userkey
from app_user_keyword_sentiment.views import api_get_userkey_sentiment
import markdown
import json
import requests

# YouTube API Key
YOUTUBE_API_KEY = "AIzaSyBH9M2nk7h1ghKHXC93l-Y09wJd9z13wKc"

# 設置遠程 Ollama 模型的基礎 URL
REMOTE_OLLAMA_URL = "http://163.18.22.32:11435"
url = f"{REMOTE_OLLAMA_URL}/api/generate"
model_name = "gemma3:4b"  # 默認模型名稱

# 檢查可用模型
print(f"正在連接 {REMOTE_OLLAMA_URL} 檢查可用模型...")
response = requests.get(f"{REMOTE_OLLAMA_URL}/api/tags")
models = response.json()
print("\n可用的模型:")
available_models = [model['name'] for model in models['models']]
for model in available_models:
    print(f"- {model}")
if model_name in available_models:
    print(f"\n✅ 模型 '{model_name}' 已可用")

# 加載資料
def load_data_topPerson():
    df_topPerson = pd.read_csv('dataset/sportsv_baseball_top_person.csv')
    global data
    data = {}
    for idx, row in df_topPerson.iterrows():
        data[row['category']] = eval(row['top_keys'])

# 啟動伺服器時加載資料
load_data_topPerson()

# 首頁
def home(request):
    return render(request, 'app_user_keyword_ai/home.html')

# 獲取使用者關鍵字資料
def get_userkey_data(request):
    userkey = request.POST.get('userkey')
    cate = request.POST['cate']
    cond = request.POST.get('cond')
    weeks = int(request.POST.get('weeks'))
    key = userkey.split()

    df_query = filter_dataFrame(key, cond, cate, weeks)

    if len(df_query) == 0:
        return {'error': 'No results found for the given keywords.'}

    try:
        response_from_sentiment = api_get_userkey_sentiment(request)
        response_from_sentiment = json.loads(response_from_sentiment.content.decode('utf-8'))
    except Exception as e:
        print(f"Error calling api_get_userkey_sentiment: {e}")
        return {'error': 'Failed to get sentiment data.'}

    try:
        response_from_userkeyword = api_get_top_userkey(request)
        response_from_userkeyword = json.loads(response_from_userkeyword.content.decode('utf-8'))
    except Exception as e:
        print(f"Error calling api_get_top_userkey: {e}")
        return {'error': 'Failed to get keyword frequency data.'}

    return response_from_userkeyword, response_from_sentiment

# API: 獲取使用者關鍵字資料
@csrf_exempt
def api_get_userkey_data(request):
    result = get_userkey_data(request)

    if isinstance(result, dict) and 'error' in result:
        return JsonResponse(result)

    response_from_userkeyword, response_from_sentiment = result
    combined_response = {**response_from_userkeyword, **response_from_sentiment}
    return JsonResponse(combined_response)

# API: 獲取 LLM 報告
@csrf_exempt
def api_get_userkey_llm_report(request):
    
    result = get_userkey_data(request)    

    # Check if result is an error dictionary
    if isinstance(result, dict) and 'error' in result:
        return JsonResponse(result)
    
    response_from_userkeyword, response_from_sentiment = result
    
    userkey = request.POST.get('userkey')
    key_occurrence_cat = response_from_userkeyword['key_occurrence_cat']
    key_time_freq = response_from_userkeyword['key_time_freq']
    key_freq_cat = response_from_userkeyword['key_freq_cat']    
    
    sentiCount = response_from_sentiment['sentiCount']
    line_data_pos = response_from_sentiment['data_pos']
    line_data_neg = response_from_sentiment['data_neg']
        
    # print(response1_data)
    # 系統提示指令
    system_prompt = f"以下是有關於[{userkey}]的網路聲量資訊，請做一份至少500字的詳細的專業分析報告。請使用繁體中文，並使用Markdown語法。"

    # 都出所有的輸入提示詞
    prompt = f'''{system_prompt}\n\n
(1)聲量分析: 根據以下資料，幫我撰寫一份至少500字的詳細的專業分析報告
以下是熱門程度，有多篇新聞報導提到:\n\n{key_occurrence_cat}\n\n
以下是時間趨勢，這個關鍵字在過去幾天的報導數量變化:\n\n{key_time_freq}\n\n
(2)情緒分析: 請根據以下資料，幫我撰寫一份至少500字的詳細的專業分析報告
以下是情緒分析比率，正面負面的分布情況:\n\n{sentiCount}\n\n
以下是情緒變化的時間趨勢，在過去幾天的報導情緒正負面的篇數數量變化:\n\n{line_data_pos}\n\n{line_data_neg}\n\n

(3)分析的內容包括但不限於以下幾個方面：
標題
摘要
關鍵字
內容
建議
總結:
'''
    print(prompt)
    
    
    # 這裡你可以呼叫ChatGPT的API來生成報告，或其他任何AI大型模型的API
    # 這裡使用requests來呼叫我用Ollama架設的遠端的API
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=100) # Add a timeout
        result = response.json()
        print(result['response'])
    except:
        print("Error:", response.status_code, response.text)
        return JsonResponse({'error': 'Failed to generate report. Please try again later.'})
    
    # 取得AI生成的報告
    response_report = {
        'report': result['response']
        #'report': markdown.markdown(result['response'])
    }
    
    # Combine dictionaries correctly
    return JsonResponse(response_report)

print("app_user_keyword_llm_report was loaded!")