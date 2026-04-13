# urls.py
from django.conf.urls import handler404

# Trỏ lỗi 404 về một view hoặc trực tiếp template
handler404 = 'your_app_name.views.error_404_view'