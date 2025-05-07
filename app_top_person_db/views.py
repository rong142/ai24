from django.shortcuts import render
import pandas as pd

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import redirect

'''
the format of data:
{'政治': [('韓國瑜', 6344),
  ('蔡英文', 2114),
  ('賴清德', 1480),
  ...
  }
'''

# YouTube API Key
YOUTUBE_API_KEY = "AIzaSyBH9M2nk7h1ghKHXC93l-Y09wJd9z13wKc"

def home(request):
    #return render(request, 'app_top_person_db/home.html')
    return render(request, 'app_top_person_db/home.html') # home.html是相同的

# csrf_exempt is used for POST
# 單獨指定這一支程式忽略csrf驗證
@csrf_exempt
def api_get_topPerson(request):

    cate = request.POST.get('news_category')
    topk = request.POST.get('topk')
    topk = int(topk)

    chart_data, wf_pairs = get_category_topPerson_db(cate, topk)
    #chart_data, wf_pairs = get_category_topPerson(cate, topk)

    print("wf_pairs:",wf_pairs)
    
    if not wf_pairs:
        # If no data is found, return an error message
        response = {'error': 'No data found for the specified category.'}
        return JsonResponse(response)
    # If data is found, return the chart data and word-frequency pairs
    response = {'chart_data':  chart_data,
                'wf_pairs': wf_pairs,
                }
    return JsonResponse(response)


import ast
from .models import TopPerson
# get charting data from database
def get_category_topPerson_db(cate, topk):

    # wf_pairs = data[cate][0:topk] # query from dataframe
    # statement = "SELECT top_keys FROM topperson where category='{}'".format(cate)
    # result = conn.execute(text(statement)).fetchone()
    # wf_pairs = eval(result[0])[0:topk]
    
    queryset = TopPerson.objects.filter(category=cate).values('top_keys')
    if queryset.exists():
        top_keys_str = queryset[0]['top_keys']
        wf_pairs = ast.literal_eval(top_keys_str)[0:topk]
    else:
        wf_pairs = []    
    
    words = [w for w, f in wf_pairs]
    freqs = [f for w, f in wf_pairs]
    chart_data = {
        "category": cate,
        "labels": words,
        "values": freqs}
    #print(chart_data)
    return chart_data, wf_pairs  # chart_data

### Functions for system management
# They can be performed by the system itself periodically.
# The system administrator can also perform them manually.
# This is for the calculation of top words in each category
from collections import Counter
from app_top_person_db.models import NewsData
from datetime import datetime, timedelta
from django.db.models import Q, Max, F

# get top words for each category
def calculate_top_person(request):
    
    # Get the latest date in the database
    latest_date = NewsData.objects.aggregate(max_date=Max('date'))['max_date']
    
    # Calculate start date
    start_date = latest_date - timedelta(weeks=4)  # 4 weeks ago
    
    top_cate_ner_words={}
    words_all=[]
    for category in news_categories:
        
        # Use Django's ORM to get entities for the given category
        entities_list = list(NewsData.objects.filter(category=category).filter(date__gte=start_date, date__lte=latest_date).values_list('entities', flat=True))
                
        # Process the retrieved entities
        words_group = []
        for entities in entities_list:
            if entities:  # Check if entities is not None
                words_group += eval(entities)

        # concatenate all terms
        words_all += words_group

        # Get top words by calling ne_word_frequency() function
        topwords = ne_word_frequency( words_group )
        top_cate_ner_words[category] = topwords

    topwords_all = ne_word_frequency(words_all)
    top_cate_ner_words['全部'] = topwords_all
    
    # save it to db
    # save it to db
    for category, top_ners in top_cate_ner_words.items():
        # Convert the list of tuples to string representation for storage
        top_keys_str = str(top_ners)
        
        # Check if an entry for this category already exists
        try:
            # Update existing record
            obj = TopPerson.objects.get(category=category)
            obj.top_keys = top_keys_str
            obj.save()
        except TopPerson.DoesNotExist:
            # Create new record
            TopPerson.objects.create(
                category=category,
                top_keys=top_keys_str
            )
    
    messages.success(request, "Top person calculated and saved successfully")
    return redirect("app_top_person_db:home")  # 你想導回的頁面
    # return render(request, "message.html",msg)  # 渲染訊息頁面
    
    # 只回傳訊息，不渲染網頁
    # Return success message
    # return JsonResponse({"status": "success", "message": "Top person calculated and saved successfully"})


allowedNE=['PERSON']
news_categories=['MLB','中職','日職','三級棒球']
def ne_word_frequency( a_news_ne ):
    filtered_words =[]
    for ner,word in a_news_ne:
        if (len(word) >= 2) & (ner in allowedNE):
            filtered_words.append(word)
    counter = Counter( filtered_words )
    return counter.most_common( 20 )

# NerToken(word='烏克蘭', ner='GPE', idx=(4, 7))  # call function NerToken with three parameters: word, ner, and idx
def NerToken(word, ner, idx):
    # print(ner,word)
    return ner,word

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

print("app_news_analysis--類別熱門人物db載入成功!")

