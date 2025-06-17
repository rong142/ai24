from django.db import models
from django.contrib.auth.models import User

class Dataset(models.Model):
    name = models.CharField(max_length=255)  # 資料集名稱
    file = models.FileField(upload_to='datasets/')  # 上傳的檔案
    uploaded_at = models.DateTimeField(auto_now_add=True)  # 上傳時間
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # 關聯到上傳的使用者

    def __str__(self):
        return self.name