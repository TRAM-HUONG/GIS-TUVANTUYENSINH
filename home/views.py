from django.shortcuts import render
from .models import TruongDaiHoc

def home_page(request):
    truong_noi_bat = TruongDaiHoc.objects.all().order_by("matruong")[:3]
    return render(request, "home/home.html", {"truong_noi_bat": truong_noi_bat})
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import NguoiDung, VaiTro


def generate_mand():
    last_user = NguoiDung.objects.order_by('-mand').first()
    if not last_user:
        return 'ND001'

    last_number = int(last_user.mand[2:])
    return f'ND{last_number + 1:03d}'


def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirmation = request.POST.get('password_confirmation', '').strip()

        if not full_name or not email or not phone_number or not password or not password_confirmation:
            return render(request, 'register.html', {
                'error': 'Vui lòng nhập đầy đủ thông tin.'
            })

        if password != password_confirmation:
            return render(request, 'register.html', {
                'error': 'Mật khẩu xác nhận không khớp.'
            })

        if NguoiDung.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'Email đã tồn tại.'
            })

        if NguoiDung.objects.filter(sodienthoai=phone_number).exists():
            return render(request, 'register.html', {
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

    return render(request, 'register.html')
from django.db.models import Q


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = NguoiDung.objects.filter(
            Q(tendangnhap=username) | Q(email=username)
        ).first()

        if not user:
            return render(request, 'login.html', {
                'error': 'Tài khoản không tồn tại.'
            })

        if user.trangthai != 'HOATDONG':
            return render(request, 'login.html', {
                'error': 'Tài khoản đã bị khóa.'
            })

        if not check_password(password, user.matkhau):
            return render(request, 'login.html', {
                'error': 'Sai mật khẩu.'
            })

        request.session['mand'] = user.mand
        request.session['hoten'] = user.hoten
        request.session['email'] = user.email
        request.session['tendangnhap'] = user.tendangnhap
        request.session['vaitro'] = user.mavaitro.tenvaitro

        return redirect('home')

    return render(request, 'login.html')
def logout_view(request):
    request.session.flush()
    return redirect('login')