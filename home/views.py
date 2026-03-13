from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator

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

def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone_number = request.POST.get("phone_number", "").strip()
        password = request.POST.get("password", "").strip()
        password_confirmation = request.POST.get("password_confirmation", "").strip()

        if not full_name or not email or not phone_number or not password or not password_confirmation:
            return render(request, "auth/dang-ky.html", {
                "error": "Vui lòng nhập đầy đủ thông tin."
            })

        if password != password_confirmation:
            return render(request, "auth/dang-ky.html", {
                "error": "Mật khẩu xác nhận không khớp."
            })

        if NguoiDung.objects.filter(email=email).exists():
            return render(request, "auth/dang-ky.html", {
                "error": "Email đã tồn tại."
            })

        if NguoiDung.objects.filter(sodienthoai=phone_number).exists():
            return render(request, "auth/dang-ky.html", {
                "error": "Số điện thoại đã tồn tại."
            })

        role_user = VaiTro.objects.filter(tenvaitro="USER").first()
        if not role_user:
            return render(request, "auth/dang-ky.html", {
                "error": "Chưa có vai trò USER trong cơ sở dữ liệu."
            })

        username = generate_username_from_email(email)

        NguoiDung.objects.create(
            mand=generate_mand(),
            hoten=full_name,
            email=email,
            sodienthoai=phone_number,
            tendangnhap=username,
            matkhau=make_password(password),
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

        if not username or not password:
            return render(request, "auth/dang-nhap.html", {
                "error": "Vui lòng nhập đầy đủ thông tin đăng nhập."
            })

        user = NguoiDung.objects.filter(
            Q(tendangnhap=username) | Q(email=username)
        ).select_related("mavaitro").first()

        if not user:
            return render(request, "auth/dang-nhap.html", {
                "error": "Tài khoản không tồn tại."
            })

        if user.trangthai != "HOATDONG":
            return render(request, "auth/dang-nhap.html", {
                "error": "Tài khoản đã bị khóa."
            })

        if password != user.matkhau:
            return render(request, "auth/dang-nhap.html", {
                "error": "Mật khẩu không đúng."
            })

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

    return render(request, "truongdaihoc/nganhhoc.html", {
        "nganh": nganh,
        "hinh_nganh": hinh_nganh,
        "ds_truong": ds_truong,
    })


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard(request):
    return render(request, "admin/dashboard.html")

# =========================================================
# ADMIN - CHI TIẾT TRƯỜNG
# =========================================================

def admin_chitiettruong_list(request):
    keyword = request.GET.get('keyword', '')  # Get search keyword from GET request

    # Filter ChiTietTruong by the search keyword (matruong or description)
    if keyword:
        chitiets = ChiTietTruong.objects.filter(
            Q(matruong__matruong__icontains=keyword) | Q(mota__icontains=keyword)
        ).order_by('mactt')
    else:
        chitiets = ChiTietTruong.objects.all().order_by('mactt')

    # Pagination
    paginator = Paginator(chitiets, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    chitiets = paginator.get_page(page_number)

    return render(request, "admin/chitiettruong/list.html", {
        "chitiets": chitiets,
        "keyword": keyword,  # Pass the search keyword to keep it in the search input field
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
    keyword = request.GET.get('keyword', '')  # Lấy từ khóa tìm kiếm từ GET

    # Lọc danh sách trường theo từ khóa tìm kiếm
    if keyword:
        truongs = TruongDaiHoc.objects.filter(
            Q(matruong__icontains=keyword) | Q(tentruong__icontains=keyword)
        )
    else:
        truongs = TruongDaiHoc.objects.all()

    # Phân trang
    paginator = Paginator(truongs, 10)  # Hiển thị 10 trường mỗi trang
    page_number = request.GET.get('page')
    truongs = paginator.get_page(page_number)

    return render(request, "admin/truongdaihoc/list.html", {
        'truongs': truongs,
        'keyword': keyword,  # Truyền từ khóa tìm kiếm để hiển thị trong ô tìm kiếm
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
    keyword = request.GET.get('keyword', '')  # For searching
    if keyword:
        nganhs = nganhs.filter(manganh__icontains=keyword) | nganhs.filter(tennganh__icontains=keyword)
    return render(request, "admin/nganhhoc/list.html", {
        "nganhs": nganhs,
        "keyword": keyword,
    })

# View to add a new major
def admin_nganh_insert(request):
    if request.method == "POST":
        tennganh = request.POST.get("tennganh", "").strip()
        linhvuc = request.POST.get("linhvuc", "").strip()
        mota = request.POST.get("mota", "").strip()

        if not tennganh or not linhvuc:
            messages.error(request, "Tên ngành và lĩnh vực không được để trống.")
            return render(request, "admin/nganhhoc/insert.html")

        NganhHoc.objects.create(
            manganh=generate_manganh(),  # Assuming you have a similar function for generating Mã ngành
            tennganh=tennganh,
            linhvuc=linhvuc,
            mota=mota or None,
        )

        messages.success(request, "Thêm ngành học thành công.")
        return redirect("admin_nganh_list")

    return render(request, "admin/nganhhoc/insert.html")

# View to edit a major
def admin_nganh_edit(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)

    if request.method == "POST":
        nganh.tennganh = request.POST.get("tennganh", "").strip()
        nganh.linhvuc = request.POST.get("linhvuc", "").strip()
        nganh.mota = request.POST.get("mota", "").strip() or None
        nganh.save()

        messages.success(request, "Cập nhật ngành học thành công.")
        return redirect("admin_nganh_list")

    return render(request, "admin/nganhhoc/edit.html", {
        "nganh": nganh
    })

# View to delete a major
def admin_nganh_delete(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)

    if request.method == "POST":
        nganh.delete()
        messages.success(request, "Xóa ngành học thành công.")
        return redirect("admin_nganh_list")

    return render(request, "admin/nganhhoc/delete.html", {
        "nganh": nganh
    })

# View to display details of a major
def admin_nganh_detail(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)
    return render(request, "admin/nganhhoc/detail.html", {
        "nganh": nganh
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