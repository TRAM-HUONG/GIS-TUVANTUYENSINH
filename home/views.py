from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.http import HttpResponseForbidden

from .models import (
    NguoiDung, VaiTro,
    TruongDaiHoc, DonViHanhChinh, ChiTietTruong
)


# =========================================================
# HÀM HỖ TRỢ
# =========================================================

def generate_mand():
    last_user = NguoiDung.objects.order_by('-mand').first()
    if not last_user:
        return 'ND001'

    last_number = int(last_user.mand[2:])
    return f'ND{last_number + 1:03d}'


def generate_matruong():
    last = TruongDaiHoc.objects.order_by('-matruong').first()
    if not last:
        return 'MAT01'

    number = int(last.matruong[3:])
    return f"MAT{number + 1:02d}"


def generate_mactt():
    last = ChiTietTruong.objects.order_by('-mactt').first()
    if not last:
        return 'CTT01'

    number = int(last.mactt[3:])
    return f"CTT{number + 1:02d}"


def is_admin(request):
    return request.session.get("tenvaitro") == "ADMIN"


# =========================================================
# AUTH
# =========================================================

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirmation = request.POST.get('password_confirmation', '').strip()

        if not full_name or not email or not phone_number or not password or not password_confirmation:
            return render(request, 'auth/dangky.html', {
                'error': 'Vui lòng nhập đầy đủ thông tin.'
            })

        if password != password_confirmation:
            return render(request, 'auth/dangky.html', {
                'error': 'Mật khẩu xác nhận không khớp.'
            })

        if NguoiDung.objects.filter(email=email).exists():
            return render(request, 'auth/dangky.html', {
                'error': 'Email đã tồn tại.'
            })

        if NguoiDung.objects.filter(sodienthoai=phone_number).exists():
            return render(request, 'auth/dangky.html', {
                'error': 'Số điện thoại đã tồn tại.'
            })

        username = email.split('@')[0]
        base_username = username
        counter = 1

        while NguoiDung.objects.filter(tendangnhap=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        role_user = VaiTro.objects.get(mavaitro='VT002')

        NguoiDung.objects.create(
            mand=generate_mand(),
            hoten=full_name,
            email=email,
            sodienthoai=phone_number,
            tendangnhap=username,
            matkhau=make_password(password),
            mavaitro=role_user,
            trangthai='HOATDONG'
        )

        messages.success(request, 'Đăng ký thành công. Vui lòng đăng nhập.')
        return redirect('login')

    return render(request, 'auth/dangky.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = NguoiDung.objects.filter(
            Q(tendangnhap=username) | Q(email=username)
        ).first()

        if not user:
            return render(request, 'auth/dangnhap.html', {
                'error': 'Tài khoản không tồn tại.'
            })

        if user.trangthai != 'HOATDONG':
            return render(request, 'auth/dangnhap.html', {
                'error': 'Tài khoản đã bị khóa.'
            })

        if not check_password(password, user.matkhau):
            return render(request, 'auth/dangnhap.html', {
                'error': 'Sai mật khẩu.'
            })

        request.session['mand'] = user.mand
        request.session['hoten'] = user.hoten
        request.session['email'] = user.email
        request.session['tendangnhap'] = user.tendangnhap
        request.session['mavaitro'] = user.mavaitro_id
        request.session['tenvaitro'] = user.mavaitro.tenvaitro

        return redirect('home')

    return render(request, 'auth/dangnhap.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


# =========================================================
# USER PAGE
# =========================================================

def home_page(request):
    return render(request, "home/home.html")


def map_view(request):
    return render(request, "map/map.html")


def truong_list(request):
    truongs = TruongDaiHoc.objects.select_related("madvhc").all().order_by("matruong")
    return render(request, "truongdaihoc/truongdaihoc.html", {
        "truongs": truongs
    })


def truong_detail(request, matruong):
    truong = get_object_or_404(
        TruongDaiHoc.objects.select_related("madvhc"),
        pk=matruong
    )
    chitiet = ChiTietTruong.objects.filter(matruong=truong).first()

    return render(request, "truongdaihoc/truong_detail.html", {
        "truong": truong,
        "chitiet": chitiet
    })


def nganh_detail(request, manganh):
    return render(request, "truongdaihoc/nganhhoc.html", {"manganh": manganh})


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard(request):
    if not is_admin(request):
        return HttpResponseForbidden("Bạn không có quyền truy cập trang quản trị.")

    return render(request, "admin/dashboard.html")


# =========================================================
# ADMIN - TRƯỜNG ĐẠI HỌC
# =========================================================

def admin_truong_list(request):
    if not is_admin(request):
        return HttpResponseForbidden("Bạn không có quyền truy cập.")

    truongs = TruongDaiHoc.objects.select_related("madvhc").all().order_by("matruong")
    return render(request, "admin/truongdaihoc/list.html", {
        "truongs": truongs
    })


def admin_truong_insert(request):
    if not is_admin(request):
        return HttpResponseForbidden("Bạn không có quyền truy cập.")

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
            return render(request, "admin/truongdaihoc/insert.html", {"dshc": dshc})

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
                ghichu=ghichu or None
            )

        messages.success(request, "Thêm trường đại học thành công.")
        return redirect("admin_truong_list")

    return render(request, "admin/truongdaihoc/insert.html", {
        "dshc": dshc
    })


def admin_truong_detail(request, matruong):
    if not is_admin(request):
        return HttpResponseForbidden("Bạn không có quyền truy cập.")

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
    if not is_admin(request):
        return HttpResponseForbidden("Bạn không có quyền truy cập.")

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

        lat = request.POST.get("lat", "").strip()
        lng = request.POST.get("lng", "").strip()
        truong.lat = float(lat) if lat else None
        truong.lng = float(lng) if lng else None

        truong.save()

        mota = request.POST.get("mota", "").strip()
        ghichu = request.POST.get("ghichu", "").strip()

        if chitiet:
            chitiet.mota = mota or None
            chitiet.ghichu = ghichu or None
            chitiet.save()
        else:
            if mota or ghichu:
                ChiTietTruong.objects.create(
                    mactt=generate_mactt(),
                    matruong=truong,
                    mota=mota or None,
                    ghichu=ghichu or None
                )

        messages.success(request, "Cập nhật trường đại học thành công.")
        return redirect("admin_truong_list")

    return render(request, "admin/truongdaihoc/edit.html", {
        "truong": truong,
        "chitiet": chitiet,
        "dshc": dshc
    })


def admin_truong_delete(request, matruong):
    if not is_admin(request):
        return HttpResponseForbidden("Bạn không có quyền truy cập.")

    truong = get_object_or_404(TruongDaiHoc, pk=matruong)

    if request.method == "POST":
        truong.delete()
        messages.success(request, "Xóa trường đại học thành công.")
        return redirect("admin_truong_list")

    return render(request, "admin/truongdaihoc/delete.html", {
        "truong": truong
    })