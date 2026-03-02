from django.shortcuts import render, get_object_or_404

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


def nganh_detail(request, mactn):
    # Lấy chi tiết ngành theo MACTN
    chi_tiet_nganh = get_object_or_404(ChiTietNganh, pk=mactn)

    # Lấy ảnh ngành (bảng HINHANH_NGANH) theo MANGANH của CTN
    hinh_nganh = HinhAnhNganh.objects.filter(manganh_id=chi_tiet_nganh.manganh_id).first()

    return render(
        request,
        "home/nganh_detail.html",
        {
            "chi_tiet_nganh": chi_tiet_nganh,
            "hinh_nganh": hinh_nganh,
        },
    )