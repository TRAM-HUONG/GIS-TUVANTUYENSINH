from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from functools import wraps
import re

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
    if not last_user:
        return "ND001"
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
    if not last:
        return "MAT01"
    number = int(last.matruong[3:])
    return f"MAT{number + 1:02d}"


def generate_mactt():
    last = ChiTietTruong.objects.order_by("-mactt").first()
    if not last:
        return "CTT01"
    number = int(last.mactt[3:])
    return f"CTT{number + 1:02d}"

def generate_manganh():
    last = NganhHoc.objects.order_by("-manganh").first()
    if not last:
        return "NGH01"
    # Logic giả định mã ngành có dạng NGHxx, bạn có thể chỉnh lại cho đúng model
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

        if NguoiDung.objects.filter(sodienthoai=phone_number).exists():
            messages.error(request, "Số điện thoại đã tồn tại.")
            return render(request, "auth/dang-ky.html")

        if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            messages.error(request, "Mật khẩu phải ít nhất 8 ký tự, bao gồm cả chữ và số.")
            return render(request, "auth/dang-ky.html")

        role_user = get_role_user()
        if not role_user:
            messages.error(request, "Hệ thống chưa có vai trò USER.")
            return render(request, "auth/dang-ky.html")

        username = generate_username_from_email(email)
        NguoiDung.objects.create(
            mand=generate_mand(),
            hoten=full_name,
            email=email,
            sodienthoai=phone_number,
            tendangnhap=username,
            matkhau=password,
            mavaitro=role_user,
            trangthai="HOATDONG",
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

        if user.trangthai != "HOATDONG":
            messages.error(request, "Tài khoản đã bị khóa.")
            return render(request, "auth/dang-nhap.html")

        request.session.flush()
        request.session["mand"] = user.mand
        request.session["hoten"] = user.hoten
        request.session["email"] = user.email
        request.session["tendangnhap"] = user.tendangnhap
        request.session["mavaitro"] = user.mavaitro.mavaitro
        request.session["tenvaitro"] = user.mavaitro.tenvaitro

        if user.mavaitro.tenvaitro.upper() == "ADMIN":
            messages.success(request, f"Xin chào quản trị viên {user.hoten}!")
            return redirect("admin_dashboard")

        messages.success(request, f"Xin chào {user.hoten}!")
        return redirect("home")
    return render(request, "auth/dang-nhap.html")


def logout_view(request):
    request.session.flush()
    messages.success(request, "Đăng xuất thành công.")
    return redirect("login")


# =========================================================
# USER PAGE
# =========================================================

def home_page(request):
    truong_noi_bat = list(TruongDaiHoc.objects.all().order_by("matruong")[:3])
    img_map = dict(
        HinhAnhTruong.objects.filter(
            matruong_id__in=[t.matruong for t in truong_noi_bat]
        ).values_list("matruong_id", "tenfile")
    )
    for t in truong_noi_bat:
        t.anh = img_map.get(t.matruong, "default.png")
    return render(request, "home/home.html", {"truong_noi_bat": truong_noi_bat})


def truong_list(request):
    keyword = request.GET.get('keyword', '').strip()
    
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

    truong_list_data = truong_qs.order_by("matruong").annotate(
        anh=Coalesce(Subquery(anh_sq), Value("default.png"))
    )
    
    nganh_list_data = NganhHoc.objects.all().order_by("tennganh")
    
    return render(request, "truongdaihoc/truongdaihoc.html", {
        "truong_list": truong_list_data,
        "nganh_list": nganh_list_data,
        "keyword": keyword # Gửi lại keyword để hiển thị trên ô nhập liệu
    })

def truong_detail(request, matruong):
    truong = get_object_or_404(
        TruongDaiHoc.objects.select_related("madvhc"),
        pk=matruong
    )

    ds_hinh_truong = HinhAnhTruong.objects.filter(
        matruong_id=matruong
    ).order_by("mahinh_truong")

    ctt = ChiTietTruong.objects.filter(matruong_id=matruong).first()
    ct_nganh = ChiTietNganh.objects.filter(
        matruong_id=matruong
    ).select_related("manganh")

    return render(request, "home/truong_detail.html", {
        "truong": truong,
        "ds_hinh_truong": ds_hinh_truong,
        "ctt": ctt,
        "ct_nganh": ct_nganh,
    })

def nganh_detail(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)
    hinh_nganh = HinhAnhNganh.objects.filter(manganh_id=manganh)
    ds_truong = ChiTietNganh.objects.filter(manganh_id=manganh).select_related("matruong")
    return render(request, "truongdaihoc/nganhhoc.html", {
        "nganh": nganh, "hinh_nganh": hinh_nganh, "ds_truong": ds_truong
    })


def gioithieu(request):
    return render(request, "gioithieu/gioithieu.html")

def map_view(request):
    return render(request, "map/map.html")

def tracuu(request):
    return render(request, "map/map.html")

from django.http import JsonResponse
from django.db.models import Prefetch
import math

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def map_data_api(request):
    truongs = (
        TruongDaiHoc.objects
        .select_related("madvhc", "madvhc__matinh")
        .prefetch_related(
            "hinh_anh_truong",
            Prefetch(
                "ctn_nganhs",
                queryset=ChiTietNganh.objects.select_related("manganh").prefetch_related("diem_chuans")
            )
        )
        .all()
        .order_by("tentruong")
    )

    schools = []
    cities = set()
    majors = set()
    blocks = set()

    for truong in truongs:
        if truong.lat is None or truong.lng is None:
            continue

        tinh_thanh = ""
        if truong.madvhc and truong.madvhc.matinh:
            tinh_thanh = truong.madvhc.matinh.tentinh
            cities.add(tinh_thanh)

        image_obj = truong.hinh_anh_truong.first()
        image_url = ""
        if image_obj and image_obj.tenfile:
            image_url = f"/static/img/TDH/{image_obj.tenfile}"

        nganh_list = []
        diem_chuan_list = []
        khoi_list = set()

        for ctn in truong.ctn_nganhs.all():
            ten_nganh = ctn.manganh.tennganh if ctn.manganh else ""
            if ten_nganh:
                nganh_list.append(ten_nganh)
                majors.add(ten_nganh)

            for dc in ctn.diem_chuans.all():
                khoi = (getattr(dc, "khoixt", "") or "").strip()
                if khoi:
                    khoi_list.add(khoi)
                    blocks.add(khoi)

                diem_chuan_list.append({
                    "mactn": ctn.mactn,
                    "manganh": ctn.manganh.manganh if ctn.manganh else "",
                    "tennganh": ten_nganh,
                    "nam": dc.nam,
                    "diem": dc.diem,
                    "khoixt": khoi,
                    "ghichu": dc.ghichu or "",
                })

        schools.append({
            "matruong": truong.matruong,
            "tentruong": truong.tentruong,
            "lat": truong.lat,
            "lng": truong.lng,
            "diachi": truong.diachi or "",
            "website": truong.website or "",
            "email": truong.email or "",
            "dienthoai": truong.dienthoai or "",
            "tinh_thanh": tinh_thanh,
            "image_url": image_url,
            "nganh_hoc": sorted(list(set(nganh_list))),
            "khoi_xet_tuyen": sorted(list(khoi_list)),
            "diem_chuan": diem_chuan_list,
        })

    return JsonResponse({
        "schools": schools,
        "cities": sorted(list(cities)),
        "majors": sorted(list(majors)),
        "blocks": sorted(list(blocks)),
    })

# =========================================================
# KHẢO SÁT
# =========================================================

def khao_sat_view(request):
    questions = KhaoSat.objects.prefetch_related("luachons").order_by("maks")
    if request.method == "POST":
        total = 0
        for question in questions:
            selected_malc = request.POST.get(question.maks)
            if not selected_malc:
                messages.error(request, "Vui lòng trả lời đầy đủ tất cả câu hỏi.")
                return render(request, "khaosat/khaosat.html", {"questions": questions})
            try:
                luachon = LuaChonKhaoSat.objects.get(malc=selected_malc, maks=question)
                total += luachon.diem
            except LuaChonKhaoSat.DoesNotExist:
                messages.error(request, "Có dữ liệu không hợp lệ.")
                return render(request, "khaosat/khaosat.html", {"questions": questions})

        ketqua = KetQuaKhaoSat.objects.select_related("manganh").filter(
            diemtu__lte=total, diemden__gte=total
        ).first()

        request.session["khao_sat_total"] = total
        request.session["khao_sat_level"] = ketqua.manganh.tennganh if ketqua else "Chưa có kết quả"
        request.session["khao_sat_summary"] = (ketqua.mota or ketqua.manganh.mota) if ketqua else "Không tìm thấy nhóm phù hợp."
        return redirect("ketqua_khaosat")

    return render(request, "khaosat/khaosat.html", {"questions": questions})


def ketqua_khao_sat_view(request):
    return render(request, "khaosat/ketqua.html", {
        "total": request.session.get("khao_sat_total"),
        "level": request.session.get("khao_sat_level"),
        "summary": request.session.get("khao_sat_summary"),
    })
import json
from django.http import JsonResponse
from .services import get_ai_response

def chat_with_ai(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            # Gọi hàm xử lý AI
            reply = get_ai_response(message)
            return JsonResponse({"reply": reply})
        except Exception as e:
            return JsonResponse({"reply": "Hệ thống đang bận một chút, bạn thử lại nhé!"})
    return JsonResponse({"error": "Invalid request"}, status=400)
# =========================================================
# ADMIN - DASHBOARD & MANAGEMENT
# =========================================================

@admin_required
def admin_dashboard(request):
    return render(request, "admin/dashboard.html")

@admin_required
def admin_nguoidung_list(request):
    nguoidungs = NguoiDung.objects.select_related("mavaitro").all().order_by("mand")
    return render(request, "admin/nguoidung/list.html", {"nguoidungs": nguoidungs})

# --- ADMIN - CHI TIẾT TRƯỜNG ---
@admin_required
def admin_chitiettruong_list(request):
    keyword = request.GET.get('keyword', '')
    chitiets = ChiTietTruong.objects.all().order_by('mactt')
    if keyword:
        chitiets = chitiets.filter(Q(matruong__matruong__icontains=keyword) | Q(mota__icontains=keyword))
    
    paginator = Paginator(chitiets, 10)
    page_number = request.GET.get('page')
    chitiets = paginator.get_page(page_number)
    return render(request, "admin/chitiettruong/list.html", {"chitiets": chitiets, "keyword": keyword})

@admin_required
def admin_chitiettruong_insert(request):
    truongs = TruongDaiHoc.objects.all().order_by("tentruong")
    if request.method == "POST":
        matruong = request.POST.get("matruong", "").strip()
        if not matruong or ChiTietTruong.objects.filter(matruong_id=matruong).exists():
            messages.error(request, "Trường chưa chọn hoặc đã có chi tiết.")
        else:
            ChiTietTruong.objects.create(
                mactt=generate_mactt(), matruong_id=matruong,
                mota=request.POST.get("mota"), ghichu=request.POST.get("ghichu")
            )
            messages.success(request, "Thêm thành công.")
            return redirect("admin_chitiettruong_list")
    return render(request, "admin/chitiettruong/insert.html", {"truongs": truongs})

@admin_required
def admin_chitiettruong_edit(request, mactt):
    chitiet = get_object_or_404(ChiTietTruong, pk=mactt)
    truongs = TruongDaiHoc.objects.all().order_by("tentruong")
    if request.method == "POST":
        chitiet.matruong_id = request.POST.get("matruong")
        chitiet.mota = request.POST.get("mota")
        chitiet.ghichu = request.POST.get("ghichu")
        chitiet.save()
        messages.success(request, "Cập nhật thành công.")
        return redirect("admin_chitiettruong_list")
    return render(request, "admin/chitiettruong/edit.html", {"chitiet": chitiet, "truongs": truongs})

@admin_required
def admin_chitiettruong_delete(request, mactt):
    chitiet = get_object_or_404(ChiTietTruong, pk=mactt)
    if request.method == "POST":
        chitiet.delete()
        messages.success(request, "Xóa thành công.")
        return redirect("admin_chitiettruong_list")
    return render(request, "admin/chitiettruong/delete.html", {"chitiet": chitiet})

@admin_required
def admin_chitiettruong_detail(request, mactt):
    chitiet = get_object_or_404(ChiTietTruong.objects.select_related("matruong"), pk=mactt)
    return render(request, "admin/chitiettruong/detail.html", {"chitiet": chitiet})

# --- ADMIN - TRƯỜNG ĐẠI HỌC ---
@admin_required
def admin_truong_list(request):
    keyword = request.GET.get('keyword', '')
    truongs = TruongDaiHoc.objects.all().order_by('matruong')
    if keyword:
        truongs = truongs.filter(Q(matruong__icontains=keyword) | Q(tentruong__icontains=keyword))
    
    paginator = Paginator(truongs, 10)
    page_number = request.GET.get('page')
    truongs = paginator.get_page(page_number)
    return render(request, "admin/truongdaihoc/list.html", {'truongs': truongs, 'keyword': keyword})

@admin_required
def admin_truong_insert(request):
    dshc = DonViHanhChinh.objects.all().order_by("tendvhc")
    if request.method == "POST":
        tentruong = request.POST.get("tentruong", "").strip()
        madvhc = request.POST.get("madvhc", "").strip()
        if not tentruong or not madvhc:
            messages.error(request, "Vui lòng nhập đủ thông tin bắt buộc.")
        else:
            truong = TruongDaiHoc.objects.create(
                matruong=generate_matruong(), tentruong=tentruong,
                loaitruong=request.POST.get("loaitruong"), madvhc_id=madvhc,
                diachi=request.POST.get("diachi"), website=request.POST.get("website"),
                email=request.POST.get("email"), dienthoai=request.POST.get("dienthoai"),
                lat=request.POST.get("lat") or None, lng=request.POST.get("lng") or None
            )
            if request.POST.get("mota"):
                ChiTietTruong.objects.create(mactt=generate_mactt(), matruong=truong, mota=request.POST.get("mota"))
            messages.success(request, "Thêm trường thành công.")
            return redirect("admin_truong_list")
    return render(request, "admin/truongdaihoc/insert.html", {"dshc": dshc})

@admin_required
def admin_truong_edit(request, matruong):
    truong = get_object_or_404(TruongDaiHoc, pk=matruong)
    chitiet = ChiTietTruong.objects.filter(matruong=truong).first()
    dshc = DonViHanhChinh.objects.all().order_by("tendvhc")
    if request.method == "POST":
        truong.tentruong = request.POST.get("tentruong")
        truong.madvhc_id = request.POST.get("madvhc")
        truong.diachi = request.POST.get("diachi")
        truong.save()
        messages.success(request, "Cập nhật thành công.")
        return redirect("admin_truong_list")
    return render(request, "admin/truongdaihoc/edit.html", {"truong": truong, "chitiet": chitiet, "dshc": dshc})

@admin_required
def admin_truong_delete(request, matruong):
    truong = get_object_or_404(TruongDaiHoc, pk=matruong)
    if request.method == "POST":
        truong.delete()
        messages.success(request, "Xóa trường thành công.")
        return redirect("admin_truong_list")
    return render(request, "admin/truongdaihoc/delete.html", {"truong": truong})

@admin_required
def admin_truong_detail(request, matruong):
    truong = get_object_or_404(TruongDaiHoc.objects.select_related("madvhc"), pk=matruong)
    chitiet = ChiTietTruong.objects.filter(matruong=truong).first()
    return render(request, "admin/truongdaihoc/detail.html", {"truong": truong, "chitiet": chitiet})

# --- ADMIN - NGÀNH HỌC ---
@admin_required
def admin_nganh_list(request):
    nganhs = NganhHoc.objects.all().order_by("manganh")
    keyword = request.GET.get('keyword', '')
    if keyword:
        nganhs = nganhs.filter(Q(manganh__icontains=keyword) | Q(tennganh__icontains=keyword))
    return render(request, "admin/nganhhoc/list.html", {"nganhs": nganhs, "keyword": keyword})

@admin_required
def admin_nganh_insert(request):
    if request.method == "POST":
        tennganh = request.POST.get("tennganh", "").strip()
        if tennganh:
            NganhHoc.objects.create(
                manganh=generate_manganh(), tennganh=tennganh,
                linhvuc=request.POST.get("linhvuc"), mota=request.POST.get("mota")
            )
            messages.success(request, "Thêm ngành thành công.")
            return redirect("admin_nganh_list")
    return render(request, "admin/nganhhoc/insert.html")

@admin_required
def admin_nganh_edit(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)
    if request.method == "POST":
        nganh.tennganh = request.POST.get("tennganh")
        nganh.linhvuc = request.POST.get("linhvuc")
        nganh.mota = request.POST.get("mota")
        nganh.save()
        return redirect("admin_nganh_list")
    return render(request, "admin/nganhhoc/edit.html", {"nganh": nganh})

@admin_required
def admin_nganh_delete(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)
    if request.method == "POST":
        nganh.delete()
        return redirect("admin_nganh_list")
    return render(request, "admin/nganhhoc/delete.html", {"nganh": nganh})

@admin_required
def admin_nganh_detail(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)

    return render(request, "admin/nganhhoc/detail.html", {"nganh": nganh})

# --- ADMIN - KHÁC ---
@admin_required
def admin_diemchuan_list(request):
    return render(request, "admin/diemchuan/list.html")




# =========================================================
# ADMIN - HÌNH ẢNH 
# =========================================================
import os
import uuid
from pathlib import Path
from django.conf import settings
from django.utils import timezone

def generate_mahinh_truong():
    last = HinhAnhTruong.objects.order_by("-mahinh_truong").first()
    if not last:
        return "HA001"

    try:
        number = int(last.mahinh_truong[2:])
    except:
        number = 0

    return f"HA{number + 1:03d}"


def save_uploaded_image(file_obj):
    """
    Lưu file upload vào thư mục static/img/TDH
    và trả về tên file đã lưu.
    """
    upload_dir = Path(settings.BASE_DIR) / "static" / "img" / "TDH"
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = file_obj.name
    ext = os.path.splitext(original_name)[1].lower()

    # Tạo tên file duy nhất để tránh trùng
    new_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_dir / new_filename

    with open(file_path, "wb+") as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)

    return new_filename


def delete_image_file(filename):
    """
    Xóa file ảnh khỏi static/img/TDH nếu tồn tại.
    """
    if not filename:
        return

    file_path = Path(settings.BASE_DIR) / "static" / "img" / "TDH" / filename
    if file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
        except:
            pass


# 1. Danh sách hình ảnh
def admin_hinhanh_list(request):
    hinhanhs = HinhAnhTruong.objects.select_related("matruong").all().order_by("-mahinh_truong")
    keyword = request.GET.get("keyword", "").strip()

    if keyword:
        hinhanhs = hinhanhs.filter(
            Q(tenfile__icontains=keyword) |
            Q(matruong__tentruong__icontains=keyword)
        )

    return render(request, "admin/hinhanh/list.html", {
        "hinhanhs": hinhanhs,
        "keyword": keyword,
    })


# 2. Thêm mới hình ảnh
def admin_hinhanh_insert(request):
    if request.method == "POST":
        matruong_id = request.POST.get("matruong", "").strip()
        tenfile_text = request.POST.get("tenfile", "").strip()
        file_anh = request.FILES.get("hinhanh")

        if not matruong_id:
            messages.error(request, "Vui lòng chọn trường.")
        elif not file_anh:
            messages.error(request, "Vui lòng chọn file ảnh.")
        else:
            truong = get_object_or_404(TruongDaiHoc, pk=matruong_id)

            # Lưu file thật vào thư mục static/img/TDH
            saved_filename = save_uploaded_image(file_anh)

            # Nếu muốn người dùng nhập mô tả thì vẫn lưu tên file thật để hiển thị ảnh
            # vì template đang dùng ha.tenfile để build đường dẫn ảnh
            HinhAnhTruong.objects.create(
                mahinh_truong=generate_mahinh_truong(),
                matruong=truong,
                tenfile=saved_filename,
                tieude=tenfile_text or None,
                ngaytao=timezone.now()
            )

            messages.success(request, "Tải lên hình ảnh thành công.")
            return redirect("admin_hinhanh_list")

    dstruong = TruongDaiHoc.objects.all().order_by("tentruong")
    return render(request, "admin/hinhanh/insert.html", {"dstruong": dstruong})


# 3. Sửa thông tin hình ảnh
def admin_hinhanh_edit(request, mahinh):
    hinhanh = get_object_or_404(HinhAnhTruong, pk=mahinh)

    if request.method == "POST":
        matruong_id = request.POST.get("matruong", "").strip()
        tenfile_text = request.POST.get("tenfile", "").strip()
        moi_anh = request.FILES.get("hinhanh")

        truong = get_object_or_404(TruongDaiHoc, pk=matruong_id)
        hinhanh.matruong = truong
        hinhanh.tieude = tenfile_text or None

        # Nếu có chọn ảnh mới thì xóa ảnh cũ và lưu ảnh mới
        if moi_anh:
            old_filename = hinhanh.tenfile
            new_filename = save_uploaded_image(moi_anh)
            hinhanh.tenfile = new_filename
            delete_image_file(old_filename)

        hinhanh.save()

        messages.success(request, "Cập nhật hình ảnh thành công.")
        return redirect("admin_hinhanh_list")

    dstruong = TruongDaiHoc.objects.all().order_by("tentruong")
    return render(request, "admin/hinhanh/edit.html", {
        "hinhanh": hinhanh,
        "dstruong": dstruong
    })


# 4. Xóa hình ảnh
def admin_hinhanh_delete(request, mahinh):
    hinhanh = get_object_or_404(HinhAnhTruong, pk=mahinh)

    if request.method == "POST":
        old_filename = hinhanh.tenfile
        hinhanh.delete()
        delete_image_file(old_filename)

        messages.success(request, "Xóa hình ảnh thành công.")
        return redirect("admin_hinhanh_list")

    return render(request, "admin/hinhanh/delete.html", {
        "hinhanh": hinhanh
    })


# 5. Chi tiết hình ảnh
def admin_hinhanh_detail(request, mahinh):
    hinhanh = get_object_or_404(HinhAnhTruong.objects.select_related("matruong"), pk=mahinh)
    return render(request, "admin/hinhanh/detail.html", {
        "hinhanh": hinhanh
    })
# =========================================================
# ADMIN - KHẢO SÁT
# =========================================================
def admin_khaosat_list(request):
    return render(request, "admin/khaosat/list.html")