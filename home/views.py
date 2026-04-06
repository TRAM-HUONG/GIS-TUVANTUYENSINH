from django.shortcuts import render, redirect
from django.contrib import messages

from .models import (
    TruongDaiHoc,
    KhaoSat,
    LuaChonKhaoSat,
    KetQuaKhaoSat,
)


def home_page(request):
    truong_noi_bat = TruongDaiHoc.objects.all().order_by("matruong")[:3]
    return render(request, "home/home.html", {"truong_noi_bat": truong_noi_bat})


def gioithieu(request):
    return render(request, "gioithieu/gioithieu.html")


def tracuu(request):
    return render(request, "tracuu/tracuu.html")

def khao_sat_view(request):
    questions = KhaoSat.objects.prefetch_related("luachons").order_by("maks")

    if request.method == "POST":
        total_score = 0
        counts = {}  # Lưu tổng ĐIỂM cho từng ngành { 'Tên Ngành': tổng_điểm_ngành }
        max_possible_score = 0 # Để tính phần trăm chính xác

        for question in questions:
            selected_malc = request.POST.get(question.maks)
            if not selected_malc:
                messages.error(request, "Vui lòng trả lời đầy đủ tất cả câu hỏi.")
                return redirect("khao_sat")

            try:
                luachon = LuaChonKhaoSat.objects.select_related("manganhgoiy").get(
                    malc=selected_malc,
                    maks=question
                )
                
                score = luachon.diem
                total_score += score
                
                if luachon.manganhgoiy:
                    ten_nganh = luachon.manganhgoiy.tennganh
                    # CỘNG DỒN ĐIỂM thay vì cộng 1
                    counts[ten_nganh] = counts.get(ten_nganh, 0) + score
                
                # Giả sử điểm tối đa mỗi câu là 5, dùng để tính tỷ lệ % trên thang 100
                max_possible_score += 5 

            except LuaChonKhaoSat.DoesNotExist:
                continue

        # Trong views.py

        # Giả sử mỗi ngành chỉ xuất hiện trong đúng 1 câu hỏi và điểm max là 5
        # Nếu ngành đó xuất hiện trong N câu hỏi, max_nganh_score phải là N * 5
        results_percent = []
        for nganh, nganh_score in counts.items():
            # Tính điểm tối đa dựa trên số câu hỏi liên quan đến ngành này
            # Ở đây ta tạm thời dùng 5 làm chuẩn cho 1 câu hỏi
            max_score_for_this_nganh = 5 
            
            # Tính phần trăm và dùng min() để chặn không cho vượt 100
            raw_percent = (nganh_score / max_score_for_this_nganh) * 100
            percent = min(round(raw_percent, 1), 100.0)
            
            results_percent.append({
                'name': nganh,
                'percent': percent
            })

        # 1. Sắp xếp ngành phù hợp nhất lên đầu (reverse=True)
        results_percent = sorted(results_percent, key=lambda x: x['percent'], reverse=True)

        # 2. CHỈ LẤY 3 NGÀNH ĐẦU TIÊN
        top_3_results = results_percent[:3]

        # 3. Lưu 3 ngành này vào session
        request.session["khao_sat_total"] = total_score
        request.session["khao_sat_results"] = top_3_results 
        
        return redirect("ketqua_khaosat")

    return render(request, "khaosat/khaosat.html", {"questions": questions})
def ketqua_khao_sat_view(request):
    total = request.session.get("khao_sat_total")
    results = request.session.get("khao_sat_results", [])

    return render(
        request,
        "khaosat/ketqua.html",
        {
            "total": total,
            "results": results, # Danh sách các ngành và %
        },
    )
def login_view(request):
    return render(request, "auth/dangnhap.html")


def register_view(request):
    return render(request, "auth/dangky.html")