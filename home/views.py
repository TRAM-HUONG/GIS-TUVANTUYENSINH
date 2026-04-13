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

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
import uuid

# Trang nhập Email để nhận link
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = NguoiDung.objects.filter(email=email).first()
        
        if user:
            token = str(uuid.uuid4())
            request.session['reset_token'] = token
            request.session['reset_email'] = email
            
            # Tạo link reset
            reset_link = request.build_absolute_uri(f"/dat-lai-mat-khau/?token={token}")
            
            # --- PHẦN LÀM ĐẸP EMAIL ---
            subject = 'Yêu cầu đặt lại mật khẩu - GIS Tuyển Sinh'
            context = {
                'user_name': user.hoten, # Giả sử model bạn có trường hoten
                'reset_link': reset_link,
            }
            # Vẽ giao diện từ file html
            html_message = render_to_string('auth/email_template.html', context)
            plain_message = strip_tags(html_message) # Nội dung chữ nếu mail ko load đc html

            try:
                message = EmailMessage(
                    subject,
                    html_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )
                message.content_subtype = 'html' # Quan trọng: báo cho Mailtrap đây là HTML
                message.send()
                
                messages.success(request, "Vui lòng kiểm tra email để lấy lại mật khẩu!")
            except Exception as e:
                print(e)
                messages.error(request, "Lỗi gửi mail.")
        else:
            messages.error(request, "Email không tồn tại.")
            
    return render(request, "auth/forgot-password.html")
# Trang cập nhật mật khẩu mới (giống cái ảnh bạn gửi)
def reset_password_view(request):
    token_url = request.GET.get('token')
    token_session = request.session.get('reset_token')
    
    if not token_url or token_url != token_session:
        return redirect('login')

    if request.method == "POST":
        pw = request.POST.get("password")
        cpw = request.POST.get("confirm_password")
        if pw == cpw:
            email = request.session.get('reset_email')
            user = NguoiDung.objects.get(email=email)
            user.matkhau = make_password(pw) # Lưu mật khẩu đã mã hóa
            user.save()
            del request.session['reset_token']
            messages.success(request, "Đổi mật khẩu thành công!")
            return redirect('login')
        else:
            messages.error(request, "Mật khẩu không khớp!")
            
    return render(request, "auth/reset-password.html")
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
                "error": "Hệ thống chưa có vai trò USER."
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
        ).select_related("mavaitro").first()

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


def logout_view(request):
    request.session.flush()
    messages.success(request, "Đăng xuất thành công.")
    return redirect("login")
