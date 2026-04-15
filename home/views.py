from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from functools import wraps
import re
from django.conf import settings
from django.contrib.auth.hashers import make_password
import uuid
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import PermissionDenied # Thêm dòng này lên đầu file


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
        # Nếu chưa đăng nhập, vẫn có thể cho redirect về trang login
        if not request.session.get("mand"):
            return redirect("login")

        # NẾU ĐÃ ĐĂNG NHẬP NHƯNG KHÔNG PHẢI ADMIN -> HIỆN 403
        if request.session.get("tenvaitro") != "ADMIN":
            raise PermissionDenied # Dòng này sẽ kích hoạt trang 403.html của bạn
            
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
    page_number = request.GET.get('page') # Lấy số trang từ URL
    
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

    # Sắp xếp và lấy ảnh đại diện
    truong_list_data = truong_qs.order_by("matruong").annotate(
        anh=Coalesce(Subquery(anh_sq), Value("default.png"))
    )
    
    # --- LOGIC PHÂN TRANG ---
    paginator = Paginator(truong_list_data, 6) # Hiển thị 6 trường trên 1 trang
    page_obj = paginator.get_page(page_number)
    
    nganh_list_data = NganhHoc.objects.all().order_by("tennganh")
    
    return render(request, "truongdaihoc/truongdaihoc.html", {
        "truong_list": page_obj,      # Gửi đối tượng đã phân trang (page_obj) đi
        "nganh_list": nganh_list_data,
        "keyword": keyword            # Gửi lại keyword để giữ giá trị trong ô search
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

def truong_list(request):
    keyword = request.GET.get('keyword', '').strip()
    page_number = request.GET.get('page') # Lấy số trang từ URL
    
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

    # Sắp xếp và lấy ảnh đại diện
    truong_list_data = truong_qs.order_by("matruong").annotate(
        anh=Coalesce(Subquery(anh_sq), Value("default.png"))
    )
    
    # --- LOGIC PHÂN TRANG ---
    paginator = Paginator(truong_list_data, 6) # Hiển thị 6 trường trên 1 trang
    page_obj = paginator.get_page(page_number)
    
    nganh_list_data = NganhHoc.objects.all().order_by("tennganh")
    
    return render(request, "truongdaihoc/truongdaihoc.html", {
        "truong_list": page_obj,      # Gửi đối tượng đã phân trang (page_obj) đi
        "nganh_list": nganh_list_data,
        "keyword": keyword            # Gửi lại keyword để giữ giá trị trong ô search
    })

def nganh_detail(request, manganh):
    nganh = get_object_or_404(NganhHoc, pk=manganh)
    hinh_nganh = HinhAnhNganh.objects.filter(manganh_id=manganh)
    ds_truong = ChiTietNganh.objects.filter(manganh_id=manganh).select_related("matruong")
    return render(request, "truongdaihoc/nganhhoc.html", {
        "nganh": nganh, "hinh_nganh": hinh_nganh, "ds_truong": ds_truong
    })

def gioithieu(request):
    # Lấy mã vai trò từ session (được lưu khi đăng nhập thành công)
    mavaitro = request.session.get('mavaitro')
    
    # Kiểm tra nếu mã vai trò khớp với mã Admin trong database của bạn
    is_admin = (mavaitro == 'VT001')
    

    return render(request, 'gioithieu/gioithieu.html', {'is_admin': is_admin})

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
import json
import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import KhaoSat, LuaChonKhaoSat, KetQuaKhaoSat, NguoiDung


@login_required_custom
def khao_sat_view(request):
    # Lấy danh sách câu hỏi kèm theo các lựa chọn
    questions = KhaoSat.objects.prefetch_related("luachons").order_by("maks")

    if request.method == "POST":
        total_score = 0
        counts = {}          # Lưu điểm thực tế của từng ngành: { 'Tên Ngành': điểm_đạt_được }
        nganh_appearance = {} # Đếm số lần ngành xuất hiện để tính điểm tối đa

        for question in questions:
            selected_malc = request.POST.get(question.maks)
            
            if not selected_malc:
                messages.error(request, "Vui lòng trả lời đầy đủ tất cả câu hỏi.")
                return redirect("khao_sat") 

            try:
                # Lấy lựa chọn kèm theo thông tin ngành gợi ý
                luachon = LuaChonKhaoSat.objects.select_related("manganhgoiy").get(
                    malc=selected_malc,
                    maks=question
                )
                
                score = luachon.diem
                total_score += score
                
                if luachon.manganhgoiy:
                    ten_nganh = luachon.manganhgoiy.tennganh
                    # Cộng dồn điểm thực tế
                    counts[ten_nganh] = counts.get(ten_nganh, 0) + score
                    # Đếm số lần ngành này làm mục tiêu gợi ý (mỗi câu max là 5đ)
                    nganh_appearance[ten_nganh] = nganh_appearance.get(ten_nganh, 0) + 1
                
            except LuaChonKhaoSat.DoesNotExist:
                continue

        # Tính toán phần trăm dựa trên trọng số thực tế
        results_percent = []
        for nganh, nganh_score in counts.items():
            # Điểm tối đa của ngành đó = (Số lần xuất hiện trong các câu đã trả lời) * 5
            max_possible = nganh_appearance.get(nganh, 1) * 5
            percent = (nganh_score / max_possible) * 100
            
            results_percent.append({
                'name': nganh,
                'percent': min(round(percent, 1), 100.0)
            })

        # Sắp xếp và lấy Top 3
        results_percent = sorted(results_percent, key=lambda x: x['percent'], reverse=True)
        top_3_results = results_percent[:3]

        # --- LƯU VÀO DATABASE ---
        try:
            # Lấy thông tin user hiện tại từ session (giả định session lưu 'user_id')
            user_id = request.session.get('user_id')
            user_obj = NguoiDung.objects.get(mand=user_id)
            
            # Tạo mã kết quả mới (ví dụ dùng UUID ngắn hoặc format KQxxx)
            new_makq = "KQ" + str(uuid.uuid4()).upper()[:8]
            
            KetQuaKhaoSat.objects.create(
                makq=new_makq,
                mand=user_obj,
                tongdiem=total_score,
                ketqua=json.dumps(top_3_results, ensure_ascii=False) # Lưu dưới dạng chuỗi JSON
            )
        except Exception as e:
            print(f"Lỗi lưu database: {e}")

        # Lưu session để hiển thị ngay trang kết quả
        request.session["khao_sat_total"] = total_score
        request.session["khao_sat_results"] = top_3_results 
        
        return redirect("ketqua_khaosat")

    return render(request, "khaosat/khaosat.html", {"questions": questions})


def ketqua_khao_sat_view(request):
    # Lấy dữ liệu từ session sau khi redirect
    total = request.session.get("khao_sat_total", 0)
    results = request.session.get("khao_sat_results", [])

    if not results:
        # Nếu user truy cập trực tiếp mà chưa làm khảo sát
        return redirect("khao_sat")

    return render(
        request,
        "khaosat/ketqua.html",
        {
            "total": total,
            "results": results,
        },
    )
import json
from django.shortcuts import render
from .models import KetQuaKhaoSat

@login_required_custom # Sử dụng decorator phân quyền hiện có của bạn
def lich_su_khao_sat(request):
    mand = request.session.get("mand")
    # Lấy danh sách kết quả của người dùng hiện tại
    ds_ketqua = KetQuaKhaoSat.objects.filter(mand_id=mand).order_by('-makq')
    
    # Giải mã chuỗi JSON kết quả để template có thể đọc được
    for item in ds_ketqua:
        try:
            item.parsed_results = json.loads(item.ketqua)
        except:
            item.parsed_results = []
            
    return render(request, "khaosat/lichsu.html", {"ds_ketqua": ds_ketqua})
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
        # Lấy dữ liệu từ form
        tentruong = request.POST.get("tentruong", "").strip()
        madvhc = request.POST.get("madvhc", "").strip()
        loaitruong = request.POST.get("loaitruong", "").strip()
        dienthoai = request.POST.get("dienthoai", "").strip()
        diachi = request.POST.get("diachi", "").strip()
        lat = request.POST.get("lat", "").strip()
        lng = request.POST.get("lng", "").strip()
        mota = request.POST.get("mota", "").strip()

        # 1. Kiểm tra các trường bắt buộc
        if not tentruong or not madvhc or not lat or not lng:
            messages.error(request, "Vui lòng nhập đầy đủ tên trường, đơn vị hành chính và tọa độ.")
            return render(request, "admin/truongdaihoc/insert.html", {"dshc": dshc, "old_data": request.POST})

        # 2. Xử lý logic tọa độ
        try:
            lat_val = float(lat)
            lng_val = float(lng)
            
            # --- CHẶN TRÙNG TỌA ĐỘ TẠI ĐÂY ---
            # Kiểm tra xem có trường nào đã dùng tọa độ này chưa
            exists = TruongDaiHoc.objects.filter(lat=lat_val, lng=lng_val).exists()
            if exists:
                messages.error(request, f"Lỗi: Tọa độ ({lat_val}, {lng_val}) đã được sử dụng cho một trường khác!")
                return render(request, "admin/truongdaihoc/insert.html", {"dshc": dshc, "old_data": request.POST})
            # ---------------------------------

            if lat_val < 0 or lng_val < 0:
                messages.error(request, "Tọa độ không được là số âm.")
                return render(request, "admin/truongdaihoc/insert.html", {"dshc": dshc, "old_data": request.POST})
        except ValueError:
            messages.error(request, "Định dạng tọa độ không hợp lệ.")
            return render(request, "admin/truongdaihoc/insert.html", {"dshc": dshc, "old_data": request.POST})

        # 3. Lưu dữ liệu nếu mọi thứ hợp lệ
        try:
            truong = TruongDaiHoc.objects.create(
                matruong=generate_matruong(),
                tentruong=tentruong,
                loaitruong=loaitruong,
                madvhc_id=madvhc,
                diachi=diachi,
                dienthoai=dienthoai,
                lat=lat_val,
                lng=lng_val
            )

            if mota:
                ChiTietTruong.objects.create(
                    mactt=generate_mactt(), 
                    matruong=truong, 
                    mota=mota
                )

            messages.success(request, f"Thêm trường {tentruong} thành công.")
            return redirect("admin_truong_list")
        except Exception as e:
            messages.error(request, f"Lỗi hệ thống: {str(e)}")
            
    return render(request, "admin/truongdaihoc/insert.html", {"dshc": dshc})

@admin_required
def admin_truong_edit(request, matruong):
    truong = get_object_or_404(TruongDaiHoc, pk=matruong)
    chitiet = ChiTietTruong.objects.filter(matruong=truong).first()
    dshc = DonViHanhChinh.objects.all().order_by("tendvhc")
    
    if request.method == "POST":
        try:
            truong.tentruong = request.POST.get("tentruong")
            truong.loaitruong = request.POST.get("loaitruong")
            truong.madvhc_id = request.POST.get("madvhc")
            truong.diachi = request.POST.get("diachi")
            dienthoai = request.POST.get("dienthoai", "").strip()
            truong.lat = float(request.POST.get("lat")) if request.POST.get("lat") else None
            truong.lng = float(request.POST.get("lng")) if request.POST.get("lng") else None
            truong.save()

            mota = request.POST.get("mota")
            if chitiet:
                chitiet.mota = mota
                chitiet.save()
            elif mota:
                ChiTietTruong.objects.create(mactt=generate_mactt(), matruong=truong, mota=mota)

            messages.success(request, "Cập nhật thành công.")
            return redirect("admin_truong_list")
        except Exception as e:
            messages.error(request, f"Lỗi: {str(e)}")

    return render(request, "admin/truongdaihoc/edit.html", {
        "truong": truong, 
        "chitiet": chitiet, 
        "dshc": dshc
    })
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
    # Lấy danh sách trường và tất cả hình ảnh thuộc về từng trường
    truong_list = TruongDaiHoc.objects.prefetch_related('hinh_anh_truong').all().order_by("matruong")
    
    keyword = request.GET.get("keyword", "").strip()

    if keyword:
        truong_list = truong_list.filter(
            Q(tentruong__icontains=keyword) | 
            Q(matruong__icontains=keyword)
        )

    # Phân trang theo số lượng trường (ví dụ 5 trường mỗi trang)
    paginator = Paginator(truong_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "admin/hinhanh/list.html", {
        "page_obj": page_obj,
        "keyword": keyword,
    })

# 2. Thêm mới hình ảnh
def admin_hinhanh_insert(request):
    if request.method == "POST":
        matruong_id = request.POST.get("matruong", "").strip()
        tenfile_text = request.POST.get("tenfile", "").strip()
        # Lấy danh sách nhiều file (nếu HTML có thuộc tính multiple)
        files = request.FILES.getlist("hinhanh")

        if not matruong_id:
            messages.error(request, "Vui lòng chọn trường.")
        elif not files:
            messages.error(request, "Vui lòng chọn ít nhất một file ảnh.")
        else:
            truong = get_object_or_404(TruongDaiHoc, pk=matruong_id)
            
            # --- LOGIC TẠO MÃ ID AN TOÀN ---
            # Tìm mã số lớn nhất của riêng tiền tố "HA"
            last_ha_image = HinhAnhTruong.objects.filter(
                mahinh_truong__startswith="HA"
            ).order_by("-mahinh_truong").first()

            if last_ha_image:
                try:
                    # Tách số từ mã (ví dụ HA011 -> lấy 11)
                    current_number = int(last_ha_image.mahinh_truong[2:])
                except (ValueError, IndexError):
                    current_number = 0
            else:
                # Nếu chưa có HA nào, lấy số từ mã cuối cùng bất kỳ hoặc bắt đầu từ 0
                last_any = HinhAnhTruong.objects.order_by("-mahinh_truong").first()
                if last_any:
                    try:
                        current_number = int(last_any.mahinh_truong[2:])
                    except:
                        current_number = 0
                else:
                    current_number = 0

            count = 0
            for file_anh in files:
                # Tăng số thứ tự
                current_number += 1
                new_id = f"HA{current_number:03d}"
                
                # Vòng lặp kiểm tra: Nếu new_id đã tồn tại trong DB thì nhảy số tiếp
                # Điều này giúp vượt qua các mã "rác" như HA011 đang bị lỗi
                while HinhAnhTruong.objects.filter(mahinh_truong=new_id).exists():
                    current_number += 1
                    new_id = f"HA{current_number:03d}"

                # Lưu file vật lý (giữ nguyên hàm save_uploaded_image của bạn)
                saved_filename = save_uploaded_image(file_anh)

                # Tạo bản ghi trong Database
                HinhAnhTruong.objects.create(
                    mahinh_truong=new_id,
                    matruong=truong,
                    tenfile=saved_filename,
                    tieude=f"{tenfile_text} ({count+1})" if tenfile_text else None,
                    ngaytao=timezone.now()
                )
                count += 1

            messages.success(request, f"Đã tải lên thành công {count} hình ảnh.")
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
    # mahinh ở đây là mahinh_truong (theo models.py của bạn)
    hinhanh = get_object_or_404(HinhAnhTruong, pk=mahinh)
    truong = hinhanh.matruong
    
    # Kiểm tra xem người dùng nhấn từ nút "Xóa tất cả" (URL có ?scope=all)
    is_delete_all = request.GET.get('scope') == 'all'

    if request.method == "POST":
        # Kiểm tra giá trị từ hidden input trong form xác nhận
        mode = request.POST.get('mode')

        if mode == "all":
            # 1. XÓA TẤT CẢ DÒNG ẢNH CỦA TRƯỜNG NÀY
            danh_sach_anh = HinhAnhTruong.objects.filter(matruong=truong)
            count = danh_sach_anh.count()
            for anh in danh_sach_anh:
                delete_image_file(anh.tenfile) # Xóa file vật lý
                anh.delete() # Xóa dòng trong DB
            messages.success(request, f"Đã xóa toàn bộ {count} ảnh của trường {truong.tentruong}.")
        else:
            # 2. CHỈ XÓA 1 DÒNG ĐANG CHỌN
            old_filename = hinhanh.tenfile
            hinhanh.delete()
            delete_image_file(old_filename)
            messages.success(request, "Đã xóa 1 hình ảnh thành công.")

        return redirect("admin_hinhanh_list")

    return render(request, "admin/hinhanh/delete.html", {
        "hinhanh": hinhanh,
        "truong": truong,
        "is_delete_all": is_delete_all
    })


# 5. Chi tiết hình ảnh
def admin_hinhanh_detail(request, mahinh):
    hinhanh = get_object_or_404(HinhAnhTruong.objects.select_related("matruong"), pk=mahinh)
    return render(request, "admin/hinhanh/detail.html", {
        "hinhanh": hinhanh
    })
    
    
  # ============ADMIN ANH NGANH================
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from pathlib import Path
from .models import NganhHoc, HinhAnhNganh

def delete_nganh_image_file(filename):
    """Xóa file ảnh khỏi static/img/NGANHHOC"""
    if not filename:
        return
    file_path = Path(settings.BASE_DIR) / "static" / "img" / "NGANHHOC" / filename
    if file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
        except:
            pass

def save_uploaded_nganh_image(file_obj):
    """Hàm bổ trợ để lưu file vào thư mục NGANHHOC (Bạn cần đảm bảo hàm này đã được định nghĩa)"""
    folder = os.path.join(settings.BASE_DIR, 'static/img/NGANHHOC')
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, file_obj.name)
    with open(file_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)
    return file_obj.name

# 1. Danh sách hình ảnh ngành
def admin_hinhanh_nganh_list(request):
    nganh_list = NganhHoc.objects.prefetch_related('hinh_anh_nganh').all().order_by("manganh")
    
    keyword = request.GET.get("keyword", "").strip()
    if keyword:
        nganh_list = nganh_list.filter(
            Q(tennganh__icontains=keyword) | Q(manganh__icontains=keyword)
        )

    paginator = Paginator(nganh_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "admin/hinhanh_nganh/list.html", {
        "page_obj": page_obj,
        "keyword": keyword,
    })

# 2. Thêm mới hình ảnh ngành
def admin_hinhanh_nganh_insert(request):
    if request.method == "POST":
        manganh_id = request.POST.get("manganh", "").strip()
        files = request.FILES.getlist("hinhanh")

        if not manganh_id:
            messages.error(request, "Vui lòng chọn ngành.")
        elif not files:
            messages.error(request, "Vui lòng chọn ít nhất một file ảnh.")
        else:
            nganh = get_object_or_404(NganhHoc, pk=manganh_id)
            
            last_han_image = HinhAnhNganh.objects.filter(
                mahinh_nganh__startswith="HAN"
            ).order_by("-mahinh_nganh").first()

            try:
                current_number = int(''.join(filter(str.isdigit, last_han_image.mahinh_nganh))) if last_han_image else 0
            except:
                current_number = 0

            count = 0
            for file_anh in files:
                current_number += 1
                new_id = f"HAN{current_number:03d}"
                while HinhAnhNganh.objects.filter(mahinh_nganh=new_id).exists():
                    current_number += 1
                    new_id = f"HAN{current_number:03d}"

                saved_filename = save_uploaded_nganh_image(file_anh)
                HinhAnhNganh.objects.create(
                    mahinh_nganh=new_id,
                    manganh=nganh,
                    tenfile=saved_filename
                )
                count += 1

            messages.success(request, f"Đã tải lên {count} ảnh cho ngành {nganh.tennganh}.")
            return redirect("admin_hinhanh_nganh_list")

    ds_nganh = NganhHoc.objects.all().order_by("tennganh")
    return render(request, "admin/hinhanh_nganh/insert.html", {"ds_nganh": ds_nganh})

# 3. Sửa hình ảnh ngành
def admin_hinhanh_nganh_edit(request, mahinh):
    hinhanh = get_object_or_404(HinhAnhNganh, pk=mahinh)
    if request.method == "POST":
        manganh_id = request.POST.get("manganh", "").strip()
        moi_anh = request.FILES.get("hinhanh")
        
        nganh = get_object_or_404(NganhHoc, pk=manganh_id)
        hinhanh.manganh = nganh

        if moi_anh:
            delete_nganh_image_file(hinhanh.tenfile)
            hinhanh.tenfile = save_uploaded_nganh_image(moi_anh)

        hinhanh.save()
        messages.success(request, "Cập nhật thành công.")
        return redirect("admin_hinhanh_nganh_list")

    ds_nganh = NganhHoc.objects.all().order_by("tennganh")
    return render(request, "admin/hinhanh_nganh/edit.html", {"hinhanh": hinhanh, "ds_nganh": ds_nganh})

# 4. Xóa hình ảnh ngành
def admin_hinhanh_nganh_delete(request, mahinh):
    hinhanh = get_object_or_404(HinhAnhNganh, pk=mahinh)
    nganh = hinhanh.manganh
    is_delete_all = request.GET.get('scope') == 'all'

    if request.method == "POST":
        mode = request.POST.get('mode')
        if mode == "all":
            danh_sach_anh = HinhAnhNganh.objects.filter(manganh=nganh)
            for anh in danh_sach_anh:
                delete_nganh_image_file(anh.tenfile)
                anh.delete()
            messages.success(request, f"Đã xóa toàn bộ ảnh của ngành {nganh.tennganh}.")
        else:
            delete_nganh_image_file(hinhanh.tenfile)
            hinhanh.delete()
            messages.success(request, "Đã xóa ảnh thành công.")
        return redirect("admin_hinhanh_nganh_list")

    return render(request, "admin/hinhanh_nganh/delete.html", {
        "hinhanh": hinhanh, "nganh": nganh, "is_delete_all": is_delete_all
    })
    
    
def admin_khaosat_list(request):
    return render(request, "admin/khaosat/list.html")

