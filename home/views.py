
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.contrib import messages

from .models import (
    TruongDaiHoc,
    KhaoSat,
    LuaChonKhaoSat,
    KetQuaKhaoSat,
)



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
        .filter(matruong_id=OuterRef("matruong"))
        .values("tenfile")[:1]
    )

    truong_list = (
        TruongDaiHoc.objects
        .all()
        .order_by("matruong")
        .annotate(anh=Coalesce(Subquery(anh_sq), Value("default.png")))
    )

  
    nganh_list = NganhHoc.objects.all().order_by("tennganh")

    return render(
        request,
        "truongdaihoc/truongdaihoc.html",
        {
            "truong_list": truong_list,
            "nganh_list": nganh_list,   # ✅ add
        },
    )
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



def gioithieu(request):
    return render(request, "gioithieu/gioithieu.html")


def tracuu(request):
    return render(request, "tracuu/tracuu.html")


def khao_sat_view(request):
    questions = KhaoSat.objects.prefetch_related("luachons").order_by("maks")

    if request.method == "POST":
        total = 0

        for question in questions:
            selected_malc = request.POST.get(question.maks)

            if not selected_malc:
                messages.error(request, "Vui lòng trả lời đầy đủ tất cả câu hỏi.")
                return render(
                    request,
                    "khaosat/khaosat.html",
                    {"questions": questions},
                )

            try:
                luachon = LuaChonKhaoSat.objects.get(
                    malc=selected_malc,
                    maks=question
                )
                total += luachon.diem
            except LuaChonKhaoSat.DoesNotExist:
                messages.error(request, "Có dữ liệu lựa chọn không hợp lệ.")
                return render(
                    request,
                    "khaosat/khaosat.html",
                    {"questions": questions},
                )

        ketqua = (
            KetQuaKhaoSat.objects.select_related("manganh")
            .filter(diemtu__lte=total, diemden__gte=total)
            .first()
        )

        if ketqua:
            level = ketqua.manganh.tennganh
            summary = ketqua.mota or ketqua.manganh.mota or ""
        else:
            level = "Chưa có kết quả"
            summary = "Chưa tìm thấy nhóm ngành phù hợp."

        request.session["khao_sat_total"] = total
        request.session["khao_sat_level"] = level
        request.session["khao_sat_summary"] = summary

        return redirect("ketqua_khaosat")

    return render(
        request,
        "khaosat/khaosat.html",
        {"questions": questions},
    )


def ketqua_khao_sat_view(request):
    total = request.session.get("khao_sat_total")
    level = request.session.get("khao_sat_level")
    summary = request.session.get("khao_sat_summary")

    return render(
        request,
        "khaosat/ketqua.html",
        {
            "total": total,
            "level": level,
            "summary": summary,
        },
    )


def login_view(request):
    return render(request, "auth/dangnhap.html")


def register_view(request):
    return render(request, "auth/dangky.html")

