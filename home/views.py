from django.shortcuts import render
from .models import TruongDaiHoc

def home_page(request):
    truong_noi_bat = TruongDaiHoc.objects.all().order_by("matruong")[:3]
    return render(request, "home/home.html", {"truong_noi_bat": truong_noi_bat})
