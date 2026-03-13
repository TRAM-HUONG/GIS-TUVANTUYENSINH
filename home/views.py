

from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q  # Add this line

from .models import NguoiDung, VaiTro
import re 
# Your existing code...

from .models import (
    TruongDaiHoc,
    KhaoSat,
    LuaChonKhaoSat,
    KetQuaKhaoSat,
)


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
)


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


def is_admin(request):
    return request.session.get("tenvaitro") == "ADMIN"


# =========================================================
# AUTH
# =========================================================

def is_admin(request):
    return request.session.get("tenvaitro") == "ADMIN"

def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone_number = request.POST.get("phone_number", "").strip()
        password = request.POST.get("password", "").strip()
        password_confirmation = request.POST.get("password_confirmation", "").strip()

        # Kiểm tra rỗng
        if not full_name or not email or not phone_number or not password or not password_confirmation:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin.")
            return render(request, "auth/dang-ky.html")

        # Kiểm tra mật khẩu xác nhận
        if password != password_confirmation:
            messages.error(request, "Mật khẩu xác nhận không khớp.")
            return render(request, "auth/dang-ky.html")

        # Kiểm tra email đã tồn tại
        if NguoiDung.objects.filter(email=email).exists():
            messages.error(request, "Email đã tồn tại.")
            return render(request, "auth/dang-ky.html")

        # Kiểm tra số điện thoại đã tồn tại
        if NguoiDung.objects.filter(sodienthoai=phone_number).exists():
            messages.error(request, "Số điện thoại đã tồn tại.")
            return render(request, "auth/dang-ky.html")

        # Kiểm tra mật khẩu có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và số
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
            messages.error(request, "Mật khẩu phải có ít nhất 8 ký tự, bao gồm cả chữ và số.")
            return render(request, "auth/dang-ky.html")

        # Kiểm tra vai trò USER
        role_user = VaiTro.objects.filter(tenvaitro="USER").first()
        if not role_user:
            VaiTro.objects.create(mavaitro='USER', tenvaitro='USER', mota='Người dùng')
            role_user = VaiTro.objects.get(tenvaitro='USER')

        # Tạo username từ email
        username = generate_username_from_email(email)

        # Lưu người dùng mới vào database
        NguoiDung.objects.create(
            mand=generate_mand(),
            hoten=full_name,
            email=email,
            sodienthoai=phone_number,
            tendangnhap=username,
            matkhau=password,  # Lưu mật khẩu đã được mã hóa
            mavaitro=role_user,
            trangthai="HOATDONG"
        )

        messages.success(request, "Đăng ký thành công. Vui lòng đăng nhập.")
        return redirect("login")

    return render(request, "auth/dang-ky.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            return render(request, "auth/dang-nhap.html", {"error": "Vui lòng nhập đầy đủ thông tin đăng nhập."})

        user = NguoiDung.objects.filter(Q(tendangnhap=username) | Q(email=username)).first()

        if not user:
            return render(request, "auth/dang-nhap.html", {"error": "Tài khoản không tồn tại."})

        if password != user.matkhau:
            return render(request, "auth/dang-nhap.html", {"error": "Mật khẩu không đúng."})

        request.session["mand"] = user.mand
        request.session["hoten"] = user.hoten
        request.session["email"] = user.email
        request.session["tendangnhap"] = user.tendangnhap
        request.session["mavaitro"] = user.mavaitro.mavaitro
        request.session["tenvaitro"] = user.mavaitro.tenvaitro

        messages.success(request, f"Đăng nhập thành công. Xin chào {user.hoten}!")
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

    return render(request, "home/home.html", {
        "truong_noi_bat": truong_noi_bat
    })

def map_view(request):
    return render(request, "map/map.html")


def truong_list(request):
    anh_sq = (
        HinhAnhTruong.objects
        .filter(matruong_id=OuterRef("matruong"))
        .values("tenfile")[:1]
    )

    truong_list_data = (
        TruongDaiHoc.objects
        .select_related("madvhc")
        .all()
        .order_by("matruong")
        .annotate(anh=Coalesce(Subquery(anh_sq), Value("default.png")))
    )

    nganh_list_data = NganhHoc.objects.all().order_by("tennganh")

    return render(request, "truongdaihoc/truongdaihoc.html", {
        "truong_list": truong_list_data,
        "nganh_list": nganh_list_data,
    })


def truong_detail(request, matruong):
    truong = get_object_or_404(
        TruongDaiHoc.objects.select_related("madvhc"),
        pk=matruong
    )
    hinh_truong = HinhAnhTruong.objects.filter(matruong_id=matruong).first()
    ctt = ChiTietTruong.objects.filter(matruong_id=matruong).first()
    ct_nganh = ChiTietNganh.objects.filter(matruong_id=matruong).select_related("manganh")

    return render(request, "home/truong_detail.html", {
        "truong": truong,
        "hinh_truong": hinh_truong,
        "ctt": ctt,
        "ct_nganh": ct_nganh,
    })


def nganh_detail(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)
    hinh_nganh = HinhAnhNganh.objects.filter(manganh_id=manganh)

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
    return render(request, "map/map.html")


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
# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard(request):
    return render(request, "admin/dashboard.html")

# =========================================================
# ADMIN - CHI TIẾT TRƯỜNG
# =========================================================

def admin_chitiettruong_list(request):
    chitiets = ChiTietTruong.objects.select_related("matruong").all().order_by("mactt")
    return render(request, "admin/chitiettruong/list.html", {
        "chitiets": chitiets
    })


def admin_chitiettruong_insert(request):
    truongs = TruongDaiHoc.objects.all().order_by("tentruong")

    if request.method == "POST":
        matruong = request.POST.get("matruong", "").strip()
        mota = request.POST.get("mota", "").strip()
        ghichu = request.POST.get("ghichu", "").strip()

        if not matruong:
            messages.error(request, "Vui lòng chọn trường.")
            return render(request, "admin/chitiettruong/insert.html", {
                "truongs": truongs
            })

        truong = get_object_or_404(TruongDaiHoc, pk=matruong)

        if ChiTietTruong.objects.filter(matruong=truong).exists():
            messages.error(request, "Trường này đã có chi tiết.")
            return render(request, "admin/chitiettruong/insert.html", {
                "truongs": truongs
            })

        ChiTietTruong.objects.create(
            mactt=generate_mactt(),
            matruong=truong,
            mota=mota or None,
            ghichu=ghichu or None
        )

        messages.success(request, "Thêm chi tiết trường thành công.")
        return redirect("admin_chitiettruong_list")

    return render(request, "admin/chitiettruong/insert.html", {
        "truongs": truongs
    })


def admin_chitiettruong_detail(request, mactt):
    chitiet = get_object_or_404(ChiTietTruong.objects.select_related("matruong"), pk=mactt)
    return render(request, "admin/chitiettruong/detail.html", {
        "chitiet": chitiet
    })


def admin_chitiettruong_edit(request, mactt):
    chitiet = get_object_or_404(ChiTietTruong, pk=mactt)
    truongs = TruongDaiHoc.objects.all().order_by("tentruong")

    if request.method == "POST":
        matruong = request.POST.get("matruong", "").strip()
        chitiet.matruong = get_object_or_404(TruongDaiHoc, pk=matruong)
        chitiet.mota = request.POST.get("mota", "").strip() or None
        chitiet.ghichu = request.POST.get("ghichu", "").strip() or None
        chitiet.save()

        messages.success(request, "Cập nhật chi tiết trường thành công.")
        return redirect("admin_chitiettruong_list")

    return render(request, "admin/chitiettruong/edit.html", {
        "chitiet": chitiet,
        "truongs": truongs
    })


def admin_chitiettruong_delete(request, mactt):
    chitiet = get_object_or_404(ChiTietTruong, pk=mactt)

    if request.method == "POST":
        chitiet.delete()
        messages.success(request, "Xóa chi tiết trường thành công.")
        return redirect("admin_chitiettruong_list")

    return render(request, "admin/chitiettruong/delete.html", {
        "chitiet": chitiet
    })


# =========================================================
# ADMIN - TRƯỜNG ĐẠI HỌC
# =========================================================

def admin_truong_list(request):
    truongs = TruongDaiHoc.objects.select_related("madvhc").all().order_by("matruong")
    return render(request, "admin/truongdaihoc/list.html", {
        "truongs": truongs
    })


def admin_truong_insert(request):
    dshc = DonViHanhChinh.objects.all().order_by("tendvhc")

    if request.method == "POST":
        tentruong = request.POST.get("tentruong", "").strip()
        loaitruong = request.POST.get("loaitruong", "").strip()
        madvhc = request.POST.get("madvhc", "").strip()
        diachi = request.POST.get("diachi", "").strip()
        website = request.POST.get("website", "").strip()
        email = request.POST.get("email", "").strip()
        dienthoai = request.POST.get("dienthoai", "").strip()
        lat = request.POST.get("lat", "").strip()
        lng = request.POST.get("lng", "").strip()
        mota = request.POST.get("mota", "").strip()
        ghichu = request.POST.get("ghichu", "").strip()

        if not tentruong or not madvhc:
            messages.error(request, "Tên trường và đơn vị hành chính không được để trống.")
            return render(request, "admin/truongdaihoc/insert.html", {
                "dshc": dshc
            })

        dvhc = get_object_or_404(DonViHanhChinh, pk=madvhc)

        truong = TruongDaiHoc(
            matruong=generate_matruong(),
            tentruong=tentruong,
            loaitruong=loaitruong or None,
            madvhc=dvhc,
            diachi=diachi or None,
            website=website or None,
            email=email or None,
            dienthoai=dienthoai or None,
            lat=float(lat) if lat else None,
            lng=float(lng) if lng else None,
        )
        truong.save()

        if mota or ghichu:
            ChiTietTruong.objects.create(
                mactt=generate_mactt(),
                matruong=truong,
                mota=mota or None,
                ghichu=ghichu or None,
            )

        messages.success(request, "Thêm trường đại học thành công.")
        return redirect("admin_truong_list")

    return render(request, "admin/truongdaihoc/insert.html", {
        "dshc": dshc
    })


def admin_truong_detail(request, matruong):
    truong = get_object_or_404(
        TruongDaiHoc.objects.select_related("madvhc"),
        pk=matruong
    )
    chitiet = ChiTietTruong.objects.filter(matruong=truong).first()

    return render(request, "admin/truongdaihoc/detail.html", {
        "truong": truong,
        "chitiet": chitiet
    })


def admin_truong_edit(request, matruong):
    truong = get_object_or_404(TruongDaiHoc, pk=matruong)
    chitiet = ChiTietTruong.objects.filter(matruong=truong).first()
    dshc = DonViHanhChinh.objects.all().order_by("tendvhc")

    if request.method == "POST":
        truong.tentruong = request.POST.get("tentruong", "").strip()
        truong.loaitruong = request.POST.get("loaitruong", "").strip() or None

        madvhc = request.POST.get("madvhc", "").strip()
        truong.madvhc = get_object_or_404(DonViHanhChinh, pk=madvhc)

        truong.diachi = request.POST.get("diachi", "").strip() or None
        truong.website = request.POST.get("website", "").strip() or None
        truong.email = request.POST.get("email", "").strip() or None
        truong.dienthoai = request.POST.get("dienthoai", "").strip() or None

        lat = request.POST.get("lat")
        lng = request.POST.get("lng")

        truong.lat = float(lat) if lat not in [None, "", "None"] else None
        truong.lng = float(lng) if lng not in [None, "", "None"] else None

        truong.save()

        mota = request.POST.get("mota", "").strip()
        ghichu = request.POST.get("ghichu", "").strip()

        if chitiet:
            chitiet.mota = mota or None
            chitiet.ghichu = ghichu or None
            chitiet.save()
        elif mota or ghichu:
            ChiTietTruong.objects.create(
                mactt=generate_mactt(),
                matruong=truong,
                mota=mota or None,
                ghichu=ghichu or None,
            )

        messages.success(request, "Cập nhật trường đại học thành công.")
        return redirect("admin_truong_list")

    return render(request, "admin/truongdaihoc/edit.html", {
        "truong": truong,
        "chitiet": chitiet,
        "dshc": dshc,
    })


def admin_truong_delete(request, matruong):
    truong = get_object_or_404(TruongDaiHoc, pk=matruong)

    if request.method == "POST":
        truong.delete()
        messages.success(request, "Xóa trường đại học thành công.")
        return redirect("admin_truong_list")

    return render(request, "admin/truongdaihoc/delete.html", {
        "truong": truong
    })


# =========================================================
# ADMIN - NGÀNH HỌC
# =========================================================

def admin_nganh_list(request):
    nganhs = NganhHoc.objects.all().order_by("manganh")
    return render(request, "admin/nganhhoc/list.html", {
        "nganhs": nganhs
    })


# =========================================================
# ADMIN - ĐIỂM CHUẨN
# =========================================================

def admin_diemchuan_list(request):
    return render(request, "admin/diemchuan/list.html")


# =========================================================
# ADMIN - KHẢO SÁT
# =========================================================

def admin_khaosat_list(request):
    return render(request, "admin/khaosat/list.html")


# =========================================================
# ADMIN - NGƯỜI DÙNG
# =========================================================

def admin_nguoidung_list(request):
    nguoidungs = NguoiDung.objects.select_related("mavaitro").all().order_by("mand")
    return render(request, "admin/nguoidung/list.html", {
        "nguoidungs": nguoidungs
    })