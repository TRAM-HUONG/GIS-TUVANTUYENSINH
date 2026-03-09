from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path("", views.home_page, name="home"),
    path("truong/", views.truong_list, name="truong_list"), 
    path("truong/<str:matruong>/", views.truong_detail, name="truong_detail"),
    path("nganh/<str:manganh>/", views.nganh_detail, name="nganh_detail"),
    path("admin/", admin.site.urls),
    path("", map_view, name="map"),
    
]
