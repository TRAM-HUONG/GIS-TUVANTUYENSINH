from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, OuterRef, Subquery, Value, Prefetch
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from functools import wraps
import re
import os
import uuid
import math
from pathlib import Path

from .models import (
    NguoiDung,
    VaiTro,
    TruongDaiHoc,
    DonViHanhChinh,
    ChiTietTruong,
    ChiTietNganh,
    NganhHoc,
    HinhAnhTruong,
    HinhAnhNganh,
    DiemChuan,
    KhaoSat,
    LuaChonKhaoSat,
    KetQuaKhaoSat,
)
from .services import get_ai_response

# =========================================================
# DECORATORS / PHÂN QUYỀN
# =========================================================

def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("mand"):
            messages.error(request, "Bạn cần đăng nhập trước.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("mand"):
            messages.error(request, "Bạn cần đăng nhập trước.")
            return redirect("login")
        if request.session.get("tenvaitro") != "ADMIN":
            messages.error(request, "Bạn không có quyền truy cập trang quản trị.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper

# =========================================================
# HÀM HỖ TRỢ
# =========================================================

def generate_mand():
    last_user = NguoiDung.objects.order_by("-mand").first()
    if not last_user: return "ND001"
    last_number = int(last_user.mand[2:])
    return f"ND{last_number + 1:03d}"

def generate_username_from_email(email):
    base_username = email.split("@")[0].strip().lower()
    username = base_username
    counter = 1
    while NguoiDung.objects.filter(tendangnhap=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username

def generate_matruong():
    last = TruongDaiHoc.objects.order_by("-matruong").first()
    if not last: return "MAT01"
    number = int(last.matruong[3:])
    return f"MAT{number + 1:02d}"

def generate_mactt():
    last = ChiTietTruong.objects.order_by("-mactt").first()
    if not last: return "CTT01"
    number = int(last.mactt[3:])
    return f"CTT{number + 1:02d}"

def generate_manganh():
    last = NganhHoc.objects.order_by("-manganh").first()
    if not last: return "NGH01"
    try:
        number = int(re.search(r'\d+', last.manganh).group())
        return f"NGH{number + 1:02d}"
    except:
        return "NGH01_NEW"

def get_role_user():
    return VaiTro.objects.filter(tenvaitro__iexact="USER").first()

# =========================================================
# AUTH
# =========================================================

def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone_number = request.POST.get("phone_number", "").strip()
        password = request.POST.get("password", "").strip()
        password_confirmation = request.POST.get("password_confirmation", "").strip()

        if not all([full_name, email, phone_number, password, password_confirmation]):
            messages.error(request, "Vui lòng nhập đầy đủ thông tin.")
            return render(request, "auth/dang-ky.html")

        if password != password_confirmation:
            messages.error(request, "Mật khẩu xác nhận không khớp.")
            return render(request, "auth/dang-ky.html")

        if NguoiDung.objects.filter(email=email).exists():
            messages.error(request, "Email đã tồn tại.")
            return render(request, "auth/dang-ky.html")

        if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            messages.error(request, "Mật khẩu phải ít nhất 8 ký tự, bao gồm cả chữ và số.")
            return render(request, "auth/dang-ky.html")

        role_user = get_role_user()
        NguoiDung.objects.create(
            mand=generate_mand(), hoten=full_name, email=email,
            sodienthoai=phone_number, tendangnhap=generate_username_from_email(email),
            matkhau=password, mavaitro=role_user, trangthai="HOATDONG",
        )
        messages.success(request, "Đăng ký thành công. Vui lòng đăng nhập.")
        return redirect("login")
    return render(request, "auth/dang-ky.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = NguoiDung.objects.select_related("mavaitro").filter(
            Q(tendangnhap=username) | Q(email=username)
        ).first()

        if not user or user.matkhau != password:
            messages.error(request, "Tài khoản hoặc mật khẩu không chính xác.")
            return render(request, "auth/dang-nhap.html")

        request.session.flush()
        request.session["mand"] = user.mand
        request.session["hoten"] = user.hoten
        request.session["tenvaitro"] = user.mavaitro.tenvaitro
        return redirect("admin_dashboard" if user.mavaitro.tenvaitro == "ADMIN" else "home")
    return render(request, "auth/dang-nhap.html")

def logout_view(request):
    request.session.flush()
    return redirect("login")

# =========================================================
# USER PAGE
# =========================================================

def home_page(request):
    truong_noi_bat = list(TruongDaiHoc.objects.all().order_by("matruong")[:3])
    img_map = dict(HinhAnhTruong.objects.filter(matruong_id__in=[t.matruong for t in truong_noi_bat]).values_list("matruong_id", "tenfile"))
    for t in truong_noi_bat:
        t.anh = img_map.get(t.matruong, "default.png")
    return render(request, "home/home.html", {"truong_noi_bat": truong_noi_bat})

def truong_list(request):
    keyword = request.GET.get('keyword', '').strip()
    anh_sq = HinhAnhTruong.objects.filter(matruong_id=OuterRef("matruong")).values("tenfile")[:1]
    truong_qs = TruongDaiHoc.objects.select_related("madvhc").all()
    if keyword:
        truong_qs = truong_qs.filter(Q(tentruong__icontains=keyword) | Q(ctn_nganhs__manganh__tennganh__icontains=keyword)).distinct()
    truong_list_data = truong_qs.order_by("matruong").annotate(anh=Coalesce(Subquery(anh_sq), Value("default.png")))
    return render(request, "truongdaihoc/truongdaihoc.html", {"truong_list": truong_list_data, "keyword": keyword})

def truong_detail(request, matruong):
    truong = get_object_or_404(TruongDaiHoc.objects.select_related("madvhc"), pk=matruong)
    ds_hinh_truong = HinhAnhTruong.objects.filter(matruong_id=matruong).order_by("mahinh_truong")
    hinh_truong_chinh = ds_hinh_truong.first()
    ctt = ChiTietTruong.objects.filter(matruong_id=matruong).first()
    ct_nganh = ChiTietNganh.objects.filter(matruong_id=matruong).select_related("manganh")
    
    return render(request, "home/truong_detail.html", {
        "truong": truong,
        "hinh_truong_chinh": hinh_truong_chinh,
        "ds_hinh_truong": ds_hinh_truong,
        "ctt": ctt,
        "ct_nganh": ct_nganh,
        "lat": truong.lat,
        "lng": truong.lng,
    })

def nganh_detail(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)
    hinh_nganh = HinhAnhNganh.objects.filter(manganh_id=manganh)
    ds_truong = ChiTietNganh.objects.filter(manganh_id=manganh).select_related("matruong")
    return render(request, "truongdaihoc/nganhhoc.html", {"nganh": nganh, "hinh_nganh": hinh_nganh, "ds_truong": ds_truong})

# =========================================================
# MAP & AI API
# =========================================================

def map_view(request): return render(request, "map/map.html")

def map_data_api(request):
    truongs = TruongDaiHoc.objects.select_related("madvhc__matinh").prefetch_related("hinh_anh_truong", Prefetch("ctn_nganhs", queryset=ChiTietNganh.objects.select_related("manganh").prefetch_related("diem_chuans"))).all()
    schools = []
    for t in truongs:
        if t.lat and t.lng:
            img = t.hinh_anh_truong.first()
            schools.append({
                "matruong": t.matruong, "tentruong": t.tentruong, "lat": t.lat, "lng": t.lng,
                "image_url": f"/static/img/TDH/{img.tenfile}" if img else "",
                "nganh_hoc": list(t.ctn_nganhs.values_list("manganh__tennganh", flat=True))
            })
    return JsonResponse({"schools": schools})

def chat_with_ai(request):
    if request.method == "POST":
        data = json.loads(request.body)
        reply = get_ai_response(data.get("message", ""))
        return JsonResponse({"reply": reply})
    return JsonResponse({"error": "Invalid"}, status=400)

# =========================================================
# ADMIN - HÌNH ẢNH (LOGIC XỬ LÝ FILE)
# =========================================================

def generate_mahinh_truong():
    last = HinhAnhTruong.objects.order_by("-mahinh_truong").first()
    num = int(last.mahinh_truong[2:]) if last else 0
    return f"HA{num + 1:03d}"

def save_uploaded_image(file_obj):
    upload_dir = Path(settings.BASE_DIR) / "static" / "img" / "TDH"
    upload_dir.mkdir(parents=True, exist_ok=True)
    new_filename = f"{uuid.uuid4().hex}{os.path.splitext(file_obj.name)[1].lower()}"
    with open(upload_dir / new_filename, "wb+") as dest:
        for chunk in file_obj.chunks(): dest.write(chunk)
    return new_filename

def delete_image_file(filename):
    if not filename: return
    file_path = Path(settings.BASE_DIR) / "static" / "img" / "TDH" / filename
    if file_path.exists(): file_path.unlink()

@admin_required
def admin_hinhanh_list(request):
    hinhanhs = HinhAnhTruong.objects.select_related("matruong").all().order_by("-mahinh_truong")
    keyword = request.GET.get("keyword", "").strip()
    if keyword:
        hinhanhs = hinhanhs.filter(Q(tenfile__icontains=keyword) | Q(matruong__tentruong__icontains=keyword))
    return render(request, "admin/hinhanh/list.html", {"hinhanhs": hinhanhs, "keyword": keyword})

@admin_required
def admin_hinhanh_insert(request):
    if request.method == "POST":
        file_anh = request.FILES.get("hinhanh")
        matruong_id = request.POST.get("matruong")
        if file_anh and matruong_id:
            HinhAnhTruong.objects.create(
                mahinh_truong=generate_mahinh_truong(),
                matruong_id=matruong_id,
                tenfile=save_uploaded_image(file_anh),
                tieude=request.POST.get("tenfile"),
                ngaytao=timezone.now()
            )
            return redirect("admin_hinhanh_list")
    return render(request, "admin/hinhanh/insert.html", {"dstruong": TruongDaiHoc.objects.all()})

@admin_required
def admin_hinhanh_delete(request, mahinh):
    hinhanh = get_object_or_404(HinhAnhTruong, pk=mahinh)
    if request.method == "POST":
        delete_image_file(hinhanh.tenfile)
        hinhanh.delete()
        return redirect("admin_hinhanh_list")
    return render(request, "admin/hinhanh/delete.html", {"hinhanh": hinhanh})

# --- Các hàm Admin khác giữ nguyên logic cơ bản ---
@admin_required
def admin_dashboard(request): return render(request, "admin/dashboard.html")

@admin_required
def admin_truong_list(request):
    truongs = TruongDaiHoc.objects.all().order_by('matruong')
    paginator = Paginator(truongs, 10)
    return render(request, "admin/truongdaihoc/list.html", {'truongs': paginator.get_page(request.GET.get('page'))})

@admin_required
def admin_nganh_list(request):
    nganhs = NganhHoc.objects.all().order_by("manganh")
    return render(request, "admin/nganhhoc/list.html", {"nganhs": nganhs})

@admin_required
def admin_khaosat_list(request):
    return render(request, "admin/khaosat/list.html")