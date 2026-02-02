from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("truong/<str:matruong>/", views.truong_detail, name="truong_detail"),
    path('nganh/<str:id>/', views.nganh_detail, name='nganh_detail'),
]
