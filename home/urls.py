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
    path("map/", views.map_view, name="map"),
    path("dang-xuat/", views.logout_view, name="logout"),

    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    path("admin/truong-dai-hoc/", views.admin_truong_list, name="admin_truong_list"),
    path("admin/truong-dai-hoc/them/", views.admin_truong_insert, name="admin_truong_insert"),
    path("admin/truong-dai-hoc/chi-tiet/<str:matruong>/", views.admin_truong_detail, name="admin_truong_detail"),
    path("admin/truong-dai-hoc/sua/<str:matruong>/", views.admin_truong_edit, name="admin_truong_edit"),
    path("admin/truong-dai-hoc/xoa/<str:matruong>/", views.admin_truong_delete, name="admin_truong_delete"),

    path("admin/chi-tiet-truong/", views.admin_chitiettruong_list, name="admin_chitiettruong_list"),
    path("admin/chi-tiet-truong/them/", views.admin_chitiettruong_insert, name="admin_chitiettruong_insert"),
    path("admin/chi-tiet-truong/chi-tiet/<str:mactt>/", views.admin_chitiettruong_detail, name="admin_chitiettruong_detail"),
    path("admin/chi-tiet-truong/sua/<str:mactt>/", views.admin_chitiettruong_edit, name="admin_chitiettruong_edit"),
    path("admin/chi-tiet-truong/xoa/<str:mactt>/", views.admin_chitiettruong_delete, name="admin_chitiettruong_delete"),
    ]
