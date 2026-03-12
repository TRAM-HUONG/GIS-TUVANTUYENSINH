from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("truong/", views.truong_list, name="truong_list"), 

    path("truong/<str:matruong>/", views.truong_detail, name="truong_detail"),
    path("nganh/<str:manganh>/", views.nganh_detail, name="nganh_detail"),

    path("gioi-thieu/", views.gioithieu, name="gioithieu"),
    path("tra-cuu/", views.tracuu, name="tracuu"),
    path("khao-sat/", views.khao_sat_view, name="khao_sat"),
    path("ket-qua-khao-sat/", views.ketqua_khao_sat_view, name="ketqua_khaosat"),
    path("dang-nhap/", views.login_view, name="login"),
    path("dang-ky/", views.register_view, name="register"),

]