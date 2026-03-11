from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path("", views.home_page, name="home"),
    path("truong/", views.truong_list, name="truong_list"), 
    path("truong/<str:matruong>/", views.truong_detail, name="truong_detail"),
    path("nganh/<str:manganh>/", views.nganh_detail, name="nganh_detail"),
    path("admin/", admin.site.urls),
    path('admin/truong-dai-hoc/', views.admin_truong_list, name='admin_truong_list'),
    path('admin/truong-dai-hoc/them/', views.admin_truong_insert, name='admin_truong_insert'),
    path('admin/truong-dai-hoc/chi-tiet/<str:matruong>/', views.admin_truong_detail, name='admin_truong_detail'),
    path('admin/truong-dai-hoc/sua/<str:matruong>/', views.admin_truong_edit, name='admin_truong_edit'),
    path('admin/truong-dai-hoc/xoa/<str:matruong>/', views.admin_truong_delete, name='admin_truong_delete'),
    
]
