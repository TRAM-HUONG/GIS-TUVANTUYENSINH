from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce

from .models import (
    TruongDaiHoc,
    ChiTietTruong,
    ChiTietNganh,
    NganhHoc,
    HinhAnhTruong,
    HinhAnhNganh,
    NguoiDung,
    VaiTro,
)


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


def truong_detail(request, matruong):
    truong = get_object_or_404(TruongDaiHoc, pk=matruong)
    hinh_truong = HinhAnhTruong.objects.filter(matruong_id=matruong).first()
    ctt = ChiTietTruong.objects.filter(matruong_id=matruong).first()
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
            "nganh_list": nganh_list,
        },
    )


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
        {
            "nganh": nganh,
            "hinh_nganh": hinh_nganh,
            "ds_truong": ds_truong
        },
    )


def generate_mand():
    last_user = NguoiDung.objects.order_by('-mand').first()
    if not last_user:
        return 'ND001'

    last_number = int(last_user.mand[2:])
    new_number = last_number + 1
    return f'ND{new_number:03d}'


def generate_username_from_email(email):
    base_username = email.split('@')[0].strip().lower()
    username = base_username
    counter = 1

    while NguoiDung.objects.filter(tendangnhap=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    return username


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

        role_user = VaiTro.objects.filter(tenvaitro='USER').first()

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
            trangthai='HOATDONG'
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
        ).select_related('mavaitro').first()

        if not user:
            return render(request, "auth/dang-nhap.html", {
                "error": "Tài khoản không tồn tại."
            })

        if user.trangthai != "HOATDONG":
            return render(request, "auth/dang-nhap.html", {
                "error": "Tài khoản đã bị khóa."
            })

        if not check_password(password, user.matkhau):
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