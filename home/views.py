from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q

from .models import NguoiDung, VaiTro


def home_page(request):
    return render(request, "home/home.html")

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