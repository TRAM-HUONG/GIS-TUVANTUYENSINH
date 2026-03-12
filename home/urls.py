from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("gioi-thieu/", views.gioithieu, name="gioithieu"),
    path("tra-cuu/", views.tracuu, name="tracuu"),
    path("khao-sat/", views.khao_sat_view, name="khao_sat"),
    path("ket-qua-khao-sat/", views.ketqua_khao_sat_view, name="ketqua_khaosat"),
    path("dang-nhap/", views.login_view, name="login"),
    path("dang-ky/", views.register_view, name="register"),
]