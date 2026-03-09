from django.db import models

class TruongDaiHoc(models.Model):
    matruong = models.CharField(db_column="MATRUONG", max_length=5, primary_key=True)
    tentruong = models.CharField(db_column="TENTRUONG", max_length=200)
    loaitruong = models.CharField(db_column="LOAITRUONG", max_length=50, null=True, blank=True)
    logo = models.CharField(db_column="LOGO", max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "TRUONGDAIHOC"
from django.db import models


class VaiTro(models.Model):
    mavaitro = models.CharField(db_column='MAVAITRO', max_length=5, primary_key=True)
    tenvaitro = models.CharField(db_column='TENVAITRO', max_length=50, unique=True)
    mota = models.CharField(db_column='MOTA', max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'VAITRO'
        managed = False

    def __str__(self):
        return self.tenvaitro


class NguoiDung(models.Model):
    mand = models.CharField(db_column='MAND', max_length=5, primary_key=True)
    hoten = models.CharField(db_column='HOTEN', max_length=150)
    email = models.EmailField(db_column='EMAIL', max_length=100, unique=True)
    sodienthoai = models.CharField(db_column='SODIENTHOAI', max_length=15, unique=True)
    tendangnhap = models.CharField(db_column='TENDANGNHAP', max_length=50, unique=True)
    matkhau = models.CharField(db_column='MATKHAU', max_length=255)
    mavaitro = models.ForeignKey(VaiTro, db_column='MAVAITRO', on_delete=models.RESTRICT)
    trangthai = models.CharField(db_column='TRANGTHAI', max_length=20, default='HOATDONG')
    ngaytao = models.DateTimeField(db_column='NGAYTAO', blank=True, null=True)

    class Meta:
        db_table = 'NGUOIDUNG'
        managed = False

    def __str__(self):
        return self.hoten