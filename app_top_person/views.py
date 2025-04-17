from django.shortcuts import render
import pandas as pd
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# YouTube API Key
YOUTUBE_API_KEY = "AIzaSyBH9M2nk7h1ghKHXC93l-Y09wJd9z13wKc"

# load data
def load_data_topPerson():
    # read df
    df_topPerson = pd.read_csv(
        'dataset/sportsv_baseball_top_person.csv')
    # refresh data
    global data
    data = {}
    for idx, row in df_topPerson.iterrows():
        data[row['category']] = eval(row['top_keys'])


# Load data first when starting server.
load_data_topPerson()

def home(request):
    return render(request, 'app_top_person/home.html')

# csrf_exempt is used for POST
# 單獨指定這一支程式忽略csrf驗證
@csrf_exempt
def api_get_topPerson(request):

    # chart_data, wf_pairs = get_category_topkey("科技", 10) #先做簡單的測試

    cate = request.POST.get('news_category')
    topk = request.POST.get('topk')
    topk = int(topk)
    #print(cate, topk)

    chart_data, wf_pairs = get_category_topPerson(cate, topk)

    # print(chart_data)
    response = {'chart_data':  chart_data,
                'wf_pairs': wf_pairs,
                }
    return JsonResponse(response)


def get_category_topPerson(cate, topk):
    wf_pairs = data[cate][0:topk]
    words = [w for w, f in wf_pairs]
    freqs = [f for w, f in wf_pairs]
    chart_data = {
        "category": cate,
        "labels": words,
        "values": freqs}
    return chart_data, wf_pairs  # chart_data is for charting

# YouTube search view
@csrf_exempt
def search_youtube(request):
    if request.method == "POST":
        keyword = request.POST.get('keyword', '')

        if not keyword:
            return JsonResponse({'error': 'Missing keyword'}, status=400)

        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': f"{keyword} 棒球",
            'type': 'video',
            'maxResults': 5,
            'key': YOUTUBE_API_KEY
        }

        response = requests.get(search_url, params=params)
        data = response.json()

        results = []
        if 'items' in data:
            for item in data['items']:
                video_id = item['id']['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                title = item['snippet']['title']
                thumbnail = item['snippet']['thumbnails']['default']['url']
                results.append({
                    'url': video_url,
                    'title': title,
                    'thumbnail': thumbnail
                })

        return JsonResponse({'results': results})

    return JsonResponse({'error': 'Invalid request'}, status=405)


print("app_news_analysis--類別熱門人物載入成功!")