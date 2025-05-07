from django.contrib import admin
from .models import TopPerson

# Register your models here.
@admin.register(TopPerson)
class TopPersonAdmin(admin.ModelAdmin):
    list_display = ('category', 'top_keys', 'created_at')
