from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # =========================
    # AUTH
    # =========================
    path("dang-nhap/", views.login_view, name="login"),
    path("dang-ky/", views.register_view, name="register"),
    path("dang-xuat/", views.logout_view, name="logout"),
    path("quen-mat-khau/", views.forgot_password_view, name="forgot_password"),
    path("dat-lai-mat-khau/", views.reset_password_view, name="reset_password"),

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

    path("khao-sat/", views.khao_sat_view, name="khao_sat"),
    path("ket-qua-khao-sat/", views.ketqua_khao_sat_view, name="ketqua_khaosat"),
    path("chat-ai/", views.chat_with_ai, name="chat_ai"),

    # =========================
    # ADMIN DASHBOARD
    # =========================
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # =========================
    # ADMIN - CHI TIẾT TRƯỜNG
    # =========================
    path("admin/chi-tiet-truong/", views.admin_chitiettruong_list, name="admin_chitiettruong_list"),
    path("admin/chi-tiet-truong/them/", views.admin_chitiettruong_insert, name="admin_chitiettruong_insert"),
    path("admin/chi-tiet-truong/chi-tiet/<str:mactt>/", views.admin_chitiettruong_detail, name="admin_chitiettruong_detail"),
    path("admin/chi-tiet-truong/sua/<str:mactt>/", views.admin_chitiettruong_edit, name="admin_chitiettruong_edit"),
    path("admin/chi-tiet-truong/xoa/<str:mactt>/", views.admin_chitiettruong_delete, name="admin_chitiettruong_delete"),

    # =========================
    # ADMIN - TRƯỜNG ĐẠI HỌC
    # =========================
    path("admin/truong/", views.admin_truong_list, name="admin_truong_list"),
    path("admin/truong/them/", views.admin_truong_insert, name="admin_truong_insert"),
    path("admin/truong/chi-tiet/<str:matruong>/", views.admin_truong_detail, name="admin_truong_detail"),
    path("admin/truong/sua/<str:matruong>/", views.admin_truong_edit, name="admin_truong_edit"),
    path("admin/truong/xoa/<str:matruong>/", views.admin_truong_delete, name="admin_truong_delete"),

    # =========================
    # ADMIN - NGÀNH HỌC
    # =========================
    path("admin/nganh/", views.admin_nganh_list, name="admin_nganh_list"),
    path("admin/nganh/them/", views.admin_nganh_insert, name="admin_nganh_insert"),
    path("admin/nganh/chi-tiet/<str:manganh>/", views.admin_nganh_detail, name="admin_nganh_detail"),
    path("admin/nganh/sua/<str:manganh>/", views.admin_nganh_edit, name="admin_nganh_edit"),
    path("admin/nganh/xoa/<str:manganh>/", views.admin_nganh_delete, name="admin_nganh_delete"),

    # =========================
    # ADMIN - HÌNH ẢNH TRƯỜNG
    # =========================
    path('admin/hinhanh/', views.admin_hinhanh_list, name='admin_hinhanh_list'),
    path('admin/hinhanh/insert/', views.admin_hinhanh_insert, name='admin_hinhanh_insert'),
    path('admin/hinhanh/detail/<str:mahinh>/', views.admin_hinhanh_detail, name='admin_hinhanh_detail'),
    path('admin/hinhanh/edit/<str:mahinh>/', views.admin_hinhanh_edit, name='admin_hinhanh_edit'),
    path('admin/hinhanh/delete/<str:mahinh>/', views.admin_hinhanh_delete, name='admin_hinhanh_delete'),

    # =========================
    # ADMIN - ĐIỂM CHUẨN & KHÁC
    # =========================
    path("admin/diemchuan/", views.admin_diemchuan_list, name="admin_diemchuan_list"),
    path("admin/khaosat/", views.admin_khaosat_list, name="admin_khaosat_list"),
    path("admin/nguoidung/", views.admin_nguoidung_list, name="admin_nguoidung_list"),
    path("api/map-data/", views.map_data_api, name="map_data_api"),
]
# =========================
# ADMIN - CHI TIẾT NGÀNH
# =========================
path("admin/chi-tiet-nganh/", views.admin_chitietnganh_list, name="admin_chitietnganh_list"),
path("admin/chi-tiet-nganh/them/", views.admin_chitietnganh_insert, name="admin_chitietnganh_insert"),
path("admin/chi-tiet-nganh/sua/<str:mactn>/", views.admin_chitietnganh_edit, name="admin_chitietnganh_edit"),
path("admin/chi-tiet-nganh/xoa/<str:mactn>/", views.admin_chitietnganh_delete, name="admin_chitietnganh_delete"),

# Cấu hình để hiển thị file media (hình ảnh) trong quá trình phát triển
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)