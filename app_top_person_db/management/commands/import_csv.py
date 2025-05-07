import csv
from django.core.management.base import BaseCommand
from app_top_person_db.models import TopPerson

class Command(BaseCommand):
    help = '匯入 sportsv_baseball_top_person.csv 資料到資料庫'

    def handle(self, *args, **kwargs):
        file_path = '/Users/xuminrong/Desktop/django/HW/w04/web_baseball/dataset/sportsv_baseball_top_person.csv'

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                category = row['category']
                top_keys = row['top_keys']

                # 檢查是否已存在相同的 category
                obj, created = TopPerson.objects.update_or_create(
                    category=category,  # 根據 category 查找資料
                    defaults={'top_keys': top_keys}  # 如果存在，更新 top_keys
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'新增資料: {category}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'更新資料: {category}'))

        self.stdout.write(self.style.SUCCESS('資料匯入完成！'))