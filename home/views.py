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


def login_view(request):
    return render(request, "auth/dangnhap.html")


def register_view(request):
    return render(request, "auth/dangky.html")