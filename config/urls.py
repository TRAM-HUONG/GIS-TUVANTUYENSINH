from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def gioithieu(request):
    return render(request, "gioithieu/gioithieu.html")

def tracuu(request):
    return render(request, "map/map.html")

def khaosat(request):
    return render(request, "khaosat/khaosat.html")

def login_view(request):
    return render(request, "auth/dang-nhap.html")

def register_view(request):
    return render(request, "auth/dang-ky.html")
def register_view(request):
    return render(request, "khoahoc/khoahoc.html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
    path("gioi-thieu/", gioithieu, name="gioithieu"),
    path("tra-cuu/", tracuu, name="tracuu"),
    path("khao-sat/", khaosat, name="khaosat"),
    path("dang-nhap/", login_view, name="login"),
    path("dang-ky/", register_view, name="register"),
     path("khoahoc/", register_view, name="khoahoc"),
]
