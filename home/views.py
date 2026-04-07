from django.shortcuts import render
from .models import TruongDaiHoc

def home_page(request):
    truong_noi_bat = TruongDaiHoc.objects.all().order_by("matruong")[:3]
    return render(request, "home/home.html", {"truong_noi_bat": truong_noi_bat})
def gioithieu(request):
    # Lấy mã vai trò từ session (được lưu khi đăng nhập thành công)
    mavaitro = request.session.get('mavaitro')
    
    # Kiểm tra nếu mã vai trò khớp với mã Admin trong database của bạn
    is_admin = (mavaitro == 'VT001')
    
    return render(request, 'gioithieu/gioithieu.html', {'is_admin': is_admin})