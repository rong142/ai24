from django.shortcuts import render
from django.http import  JsonResponse
import pandas as pd

# render渲染網頁
def home(request):
    return render(request, 'app_top_keyword/home.html')

# read df
df_topkey = pd.read_csv('dataset/sport_baseball_topkey.csv', sep=',')

# prepare data
data={}
for idx, row in df_topkey.iterrows():
    data[row['category']] = eval(row['top_keys'])

# We don't use it anymore, so delete it to save memory.
del df_topkey

# POST: csrf_exempt should be used
# 指定這一支程式忽略csrf驗證
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def api_get_cate_topword(request):
    cate = request.POST.get('news_category')
    #cate = request.GET['news_category'] # this command also works.
    topk = request.POST.get('topk')
    topk = int(topk)
    print(cate, topk)

    chart_data, wf_pairs = get_category_topword(cate, topk)
    response = {'chart_data': chart_data,
         'wf_pairs': wf_pairs,
         }
    print(response)
    return JsonResponse(response)

def get_category_topword(cate, topk=10):
    wf_pairs = data[cate][0:topk]
    words = [w for w, f in wf_pairs]
    freqs = [f for w, f in wf_pairs]
    chart_data = {
        "category": cate,
        "labels": words,
        "values": freqs}
    return chart_data, wf_pairs

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

print("app_top_keywords--類別熱門關鍵字載入成功!")


