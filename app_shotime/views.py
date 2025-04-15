from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd

def load_data_scchen():
    # Read data from csv file
    df_data = pd.read_csv('dataset/sho_time.csv',sep=',')
    global response
    response = dict(list(df_data.values))
    del df_data

# load pk data
load_data_scchen()

def home(request):
    return render(request,'app_shotime/home.html', response)


print('app_scchen was loaded!')