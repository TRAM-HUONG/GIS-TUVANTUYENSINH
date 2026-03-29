from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # AUTH
    # =========================
    path("dang-nhap/", views.login_view, name="login"),
    path("dang-ky/", views.register_view, name="register"),
    path("dang-xuat/", views.logout_view, name="logout"),

    # =========================
    # USER PAGE
    # =========================
    path("", views.home_page, name="home"),
    path("gioi-thieu/", views.gioithieu, name="gioithieu"),
    path("tra-cuu/", views.tracuu, name="tracuu"),
    path("map/", views.map_view, name="map"),

    path("truong/", views.truong_list, name="truong_list"),
    path("truong/<str:matruong>/", views.truong_detail, name="truong_detail"),
    path("nganh/<str:manganh>/", views.nganh_detail, name="nganh_detail"),

    path("khao-sat/", views.khao_sat_view, name="khaosat"),
    path("ket-qua-khao-sat/", views.ketqua_khao_sat_view, name="ketqua_khaosat"),

    # =========================
    # ADMIN DASHBOARD
    # =========================
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # =========================
    # ADMIN - CHI TIẾT TRƯỜNG
    # =========================
    path("admin/chitiettruong/", views.admin_chitiettruong_list, name="admin_chitiettruong_list"),
    path("admin/chitiettruong/insert/", views.admin_chitiettruong_insert, name="admin_chitiettruong_insert"),
    path("admin/chitiettruong/detail/<str:mactt>/", views.admin_chitiettruong_detail, name="admin_chitiettruong_detail"),
    path("admin/chitiettruong/edit/<str:mactt>/", views.admin_chitiettruong_edit, name="admin_chitiettruong_edit"),
    path("admin/chitiettruong/delete/<str:mactt>/", views.admin_chitiettruong_delete, name="admin_chitiettruong_delete"),

    # =========================
    # ADMIN - TRƯỜNG ĐẠI HỌC
    # =========================
    path("admin/truong/", views.admin_truong_list, name="admin_truong_list"),
    path("admin/truong/insert/", views.admin_truong_insert, name="admin_truong_insert"),
    path("admin/truong/detail/<str:matruong>/", views.admin_truong_detail, name="admin_truong_detail"),
    path("admin/truong/edit/<str:matruong>/", views.admin_truong_edit, name="admin_truong_edit"),
    path("admin/truong/delete/<str:matruong>/", views.admin_truong_delete, name="admin_truong_delete"),

    # =========================
    # ADMIN - NGÀNH HỌC
    # =========================
    path("admin/nganh/", views.admin_nganh_list, name="admin_nganh_list"),

    # =========================
    # ADMIN - ĐIỂM CHUẨN
    # =========================
    path("admin/diemchuan/", views.admin_diemchuan_list, name="admin_diemchuan_list"),

    # =========================
    # ADMIN - KHẢO SÁT
    # =========================
    path("admin/khaosat/", views.admin_khaosat_list, name="admin_khaosat_list"),

    # =========================
    # ADMIN - NGƯỜI DÙNG
    # =========================
    path("admin/nguoidung/", views.admin_nguoidung_list, name="admin_nguoidung_list"),
]