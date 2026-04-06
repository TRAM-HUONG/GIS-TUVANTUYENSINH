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

from django.core.paginator import Paginator
from django.db.models import Q, Subquery, OuterRef, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
# Import các model của bạn vào đây

def truong_list(request):
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page') # Lấy số trang từ URL
    
    # Lấy ảnh đầu tiên của mỗi trường làm subquery
    anh_sq = HinhAnhTruong.objects.filter(matruong_id=OuterRef("matruong")).values("tenfile")[:1]
    
    # Query cơ bản
    truong_qs = TruongDaiHoc.objects.select_related("madvhc").all()

    # Nếu có từ khóa, lọc theo Tên trường HOẶC Tên ngành liên quan
    if keyword:
        truong_qs = truong_qs.filter(
            Q(tentruong__icontains=keyword) | 
            Q(ctn_nganhs__manganh__tennganh__icontains=keyword)
        ).distinct()

    # Sắp xếp và lấy ảnh đại diện
    truong_list_data = truong_qs.order_by("matruong").annotate(
        anh=Coalesce(Subquery(anh_sq), Value("default.png"))
    )
    
    # --- LOGIC PHÂN TRANG ---
    paginator = Paginator(truong_list_data, 6) # Hiển thị 6 trường trên 1 trang
    page_obj = paginator.get_page(page_number)
    
    nganh_list_data = NganhHoc.objects.all().order_by("tennganh")
    
    return render(request, "truongdaihoc/truongdaihoc.html", {
        "truong_list": page_obj,      # Gửi đối tượng đã phân trang (page_obj) đi
        "nganh_list": nganh_list_data,
        "keyword": keyword            # Gửi lại keyword để giữ giá trị trong ô search
    })

def nganh_detail(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)

    # ảnh ngành (nếu có)
    hinh_nganh = HinhAnhNganh.objects.filter(manganh_id=manganh)

    # (tuỳ em) nếu muốn hiện các trường có ngành này:
    ds_truong = (
        ChiTietNganh.objects
        .filter(manganh_id=manganh)
        .select_related("matruong")
    )

    return render(
        request,
        "truongdaihoc/nganhhoc.html",
        {"nganh": nganh, "hinh_nganh": hinh_nganh, "ds_truong": ds_truong},
    )