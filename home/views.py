from django.shortcuts import render, get_object_or_404

from .models import TruongDaiHoc, HinhAnh, CHITIETTRUONG, ChiTietNganh, NganhHoc

# Home page view to display a list of top 3 universities
def home_page(request):
    truong_noi_bat = TruongDaiHoc.objects.all().order_by("matruong")[:3]
    return render(request, "home/home.html", {"truong_noi_bat": truong_noi_bat})


def truong_detail(request, matruong):
    truong = TruongDaiHoc.objects.get(matruong=matruong)  # Lấy trường theo mã

    # Lấy ảnh của trường từ bảng HinhAnh
    hinh_truong = HinhAnh.objects.filter(loai="TRUONG", madoituong=matruong).first()

    # Lấy mô tả từ bảng CHITIETTRUONG
    ctt = CHITIETTRUONG.objects.filter(matruong=matruong).first()

    # Lấy tất cả chi tiết ngành học của trường đó
    # Sử dụng `matruong` và `manganh` làm khóa chính, không cần cột `id`
    ct_nganh = ChiTietNganh.objects.filter(matruong=truong)

    return render(request, "home/truong_detail.html", {
        "truong": truong,
        "hinh_truong": hinh_truong,
        "ctt": ctt,  # Truyền mô tả trường vào template
        "ct_nganh": ct_nganh,  # Truyền chi tiết ngành học vào template
    })

def nganh_detail(request, id):
    try:
        chi_tiet_nganh = ChiTietNganh.objects.get(MACTN=id)  # Lấy chi tiết ngành theo MACTN
    except ChiTietNganh.DoesNotExist:
        chi_tiet_nganh = None

    return render(request, 'nganh_detail.html', {'chi_tiet_nganh': chi_tiet_nganh})
