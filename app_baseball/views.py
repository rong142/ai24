from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Dataset

def hello(request):
    return HttpResponse('<h2>Hello World!</h2>')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # 登入成功後跳轉到首頁
        else:
            messages.error(request, '使用者名稱或密碼錯誤')
    return render(request, 'login.html')

@login_required
def home(request):
    return render(request, 'app_user_keyword/home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # 檢查密碼是否一致
        if password != password_confirm:
            messages.error(request, '密碼不一致，請重新輸入')
            return render(request, 'register.html')

        # 檢查使用者名稱是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, '使用者名稱已存在，請選擇其他名稱')
            return render(request, 'register.html')

        # 建立新使用者
        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            messages.success(request, '註冊成功，請重新登入')
            return render(request, 'register.html')
        except Exception as e:
            messages.error(request, f'註冊失敗: {e}')
            return render(request, 'register.html')

    return render(request, 'register.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    # 過濾出當前登入使用者的資料集
    datasets = Dataset.objects.filter(user=request.user)
    return render(request, 'home.html', {'datasets': datasets})

@login_required
def upload_dataset(request):
    if request.method == 'POST':
        dataset_name = request.POST.get('dataset_name')  # 獲取資料集名稱
        uploaded_file = request.FILES.get('dataset')  # 獲取上傳的檔案

        if dataset_name and uploaded_file:
            # 儲存到 Dataset 模型，並關聯到當前登入的使用者
            dataset = Dataset.objects.create(
                name=dataset_name,
                file=uploaded_file,
                user=request.user  # 關聯到當前登入的使用者
            )
            dataset.save()
            messages.success(request, f'資料集 "{dataset_name}" 上傳成功')
            return redirect('home')
        else:
            messages.error(request, '上傳失敗，請填寫所有欄位')
    return redirect('home')

def select_dataset(request):
    dataset_id = request.GET.get('dataset_id')
    if dataset_id:
        # 確保資料集屬於當前登入的使用者
        dataset = Dataset.objects.filter(id=dataset_id, user=request.user).first()
        if dataset:
            messages.success(request, f'已選擇資料集：{dataset.name}')
            return redirect('home')
        else:
            messages.error(request, '您無權訪問該資料集')
            return redirect('home')
    else:
        messages.error(request, '請選擇資料集')
        return redirect('home')