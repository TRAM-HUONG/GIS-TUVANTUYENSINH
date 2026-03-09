from django.contrib import admin
from .models import (
    TinhThanh,
    DonViHanhChinh,
    TruongDaiHoc,
    ChiTietTruong,
    NganhHoc,
    ChiTietNganh,
    HinhAnhTruong,
    HinhAnhNganh,
)


@admin.register(TinhThanh)
class TinhThanhAdmin(admin.ModelAdmin):
    list_display = ("matinh", "tentinh")
    search_fields = ("matinh", "tentinh")


@admin.register(DonViHanhChinh)
class DonViHanhChinhAdmin(admin.ModelAdmin):
    list_display = ("madvhc", "tendvhc", "loai", "matinh")
    search_fields = ("madvhc", "tendvhc", "loai", "matinh__tentinh")
    list_filter = ("loai", "matinh")


@admin.register(TruongDaiHoc)
class TruongDaiHocAdmin(admin.ModelAdmin):
    list_display = (
        "matruong",
        "tentruong",
        "loaitruong",
        "madvhc",
        "website",
        "email",
        "dienthoai",
        "lat",
        "lng",
    )
    search_fields = (
        "matruong",
        "tentruong",
        "loaitruong",
        "diachi",
        "website",
        "email",
        "dienthoai",
        "madvhc__tendvhc",
    )
    list_filter = ("loaitruong", "madvhc")
    list_per_page = 20


@admin.register(ChiTietTruong)
class ChiTietTruongAdmin(admin.ModelAdmin):
    list_display = ("mactt", "matruong", "ghichu")
    search_fields = ("mactt", "matruong__tentruong", "ghichu", "mota")


@admin.register(NganhHoc)
class NganhHocAdmin(admin.ModelAdmin):
    list_display = ("manganh", "tennganh", "linhvuc")
    search_fields = ("manganh", "tennganh", "linhvuc", "mota")
    list_filter = ("linhvuc",)


@admin.register(ChiTietNganh)
class ChiTietNganhAdmin(admin.ModelAdmin):
    list_display = ("mactn", "matruong", "manganh", "hocphi", "thoigianhoc")
    search_fields = (
        "mactn",
        "matruong__tentruong",
        "manganh__tennganh",
    )
    list_filter = ("matruong", "manganh")


@admin.register(HinhAnhTruong)
class HinhAnhTruongAdmin(admin.ModelAdmin):
    list_display = ("mahinh_truong", "matruong", "tenfile", "tieude", "ngaytao")
    search_fields = (
        "mahinh_truong",
        "matruong__tentruong",
        "tenfile",
        "tieude",
        "mota",
    )
    list_filter = ("matruong",)


@admin.register(HinhAnhNganh)
class HinhAnhNganhAdmin(admin.ModelAdmin):
    list_display = ("mahinh_nganh", "manganh", "tenfile", "tieude", "ngaytao")
    search_fields = (
        "mahinh_nganh",
        "manganh__tennganh",
        "tenfile",
        "tieude",
        "mota",
    )
    list_filter = ("manganh",)