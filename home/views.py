from django.shortcuts import render, get_object_or_404
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models import Value

from .models import (
    TruongDaiHoc,
    ChiTietTruong,
    ChiTietNganh,
    NganhHoc,
    HinhAnhTruong,
    HinhAnhNganh,
)
def home_page(request):
    truong_noi_bat = list(TruongDaiHoc.objects.all().order_by("matruong")[:3])

    # Lấy map MATRUONG -> TENFILE
    img_map = dict(
        HinhAnhTruong.objects.filter(
            matruong_id__in=[t.matruong for t in truong_noi_bat]
        ).values_list("matruong_id", "tenfile")
    )

    # gán thuộc tính tạm cho template dùng
    for t in truong_noi_bat:
        t.anh = img_map.get(t.matruong, "default.png")  # fallback nếu thiếu

    return render(request, "home/home.html", {"truong_noi_bat": truong_noi_bat}
    )

def truong_detail(request, matruong):
    # Lấy trường theo mã
    truong = get_object_or_404(TruongDaiHoc, pk=matruong)

    # Lấy 1 ảnh đại diện của trường (bảng HINHANH_TRUONG)
    hinh_truong = HinhAnhTruong.objects.filter(matruong_id=matruong).first()

    # Lấy mô tả từ bảng CHITIETTRUONG (model: ChiTietTruong)
    ctt = ChiTietTruong.objects.filter(matruong_id=matruong).first()

    # Lấy tất cả ngành của trường (bảng CHITIETNGANH)
    ct_nganh = ChiTietNganh.objects.filter(matruong_id=matruong)

    return render(
        request,
        "home/truong_detail.html",
        {
            "truong": truong,
            "hinh_truong": hinh_truong,
            "ctt": ctt,
            "ct_nganh": ct_nganh,
        },
    )
def truong_list(request):
    anh_sq = (
        HinhAnhTruong.objects
        .filter(matruong_id=OuterRef("matruong"))   # ✅ sửa field ở đây
        .values("tenfile")[:1]
    )

    truong_list = (
        TruongDaiHoc.objects
        .all()
        .order_by("matruong")
        .annotate(anh=Coalesce(Subquery(anh_sq), Value("default.png")))  # ✅ fallback
    )

    return render(request, "truongdaihoc/truongdaihoc.html", {"truong_list": truong_list})