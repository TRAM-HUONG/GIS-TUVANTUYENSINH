from django.db import models


class TruongDaiHoc(models.Model):
    matruong = models.CharField(db_column="MATRUONG", max_length=5, primary_key=True)
    tentruong = models.CharField(db_column="TENTRUONG", max_length=200)
    loaitruong = models.CharField(db_column="LOAITRUONG", max_length=50, null=True, blank=True)
    madvhc = models.CharField(db_column="MADVHC", max_length=5)
    diachi = models.TextField(db_column="DIACHI", null=True, blank=True)
    website = models.CharField(db_column="WEBSITE", max_length=255, null=True, blank=True)
    email = models.CharField(db_column="EMAIL", max_length=100, null=True, blank=True)
    dienthoai = models.CharField(db_column="DIENTHOAI", max_length=30, null=True, blank=True)
    lat = models.FloatField(db_column="LAT", null=True, blank=True)
    lng = models.FloatField(db_column="LNG", null=True, blank=True)

    class Meta:
        managed = False
        db_table = "TRUONGDAIHOC"

    def __str__(self):
        return self.tentruong


class NganhHoc(models.Model):
    manganh = models.CharField(db_column="MANGANH", max_length=5, primary_key=True)
    tennganh = models.CharField(db_column="TENNGANH", max_length=200)
    linhvuc = models.CharField(db_column="LINHVUC", max_length=100, null=True, blank=True)
    mota = models.TextField(db_column="MOTA", null=True, blank=True)

    class Meta:
        managed = False
        db_table = "NGANHHOC"

    def __str__(self):
        return self.tennganh


class KhaoSat(models.Model):
    maks = models.CharField(db_column="MAKS", max_length=5, primary_key=True)
    cauhoi = models.CharField(db_column="CAUHOI", max_length=400)
    hinhanh = models.CharField(db_column="HINHANH", max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "KHAOSAT"

    def __str__(self):
        return self.cauhoi


class LuaChonKhaoSat(models.Model):
    malc = models.CharField(db_column="MALC", max_length=5, primary_key=True)
    maks = models.ForeignKey(
        KhaoSat,
        db_column="MAKS",
        on_delete=models.CASCADE,
        related_name="luachons"
    )
    noidung = models.CharField(db_column="NOIDUNG", max_length=300)
    diem = models.IntegerField(db_column="DIEM")
    manganhgoiy = models.ForeignKey(
        NganhHoc,
        db_column="MANGANHGOIY",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="luachon_goiy"
    )

    class Meta:
        managed = False
        db_table = "LUACHONKHAOSAT"

    def __str__(self):
        return self.noidung


class KetQuaKhaoSat(models.Model):
    makq = models.CharField(db_column="MAKQ", max_length=5, primary_key=True)
    diemtu = models.IntegerField(db_column="DIEMTU")
    diemden = models.IntegerField(db_column="DIEMDEN")
    manganh = models.ForeignKey(
        NganhHoc,
        db_column="MANGANH",
        on_delete=models.CASCADE,
        related_name="ketqua_goiy"
    )
    mota = models.CharField(db_column="MOTA", max_length=200, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "KETQUAKHAOSAT"

    def __str__(self):
        return f"{self.diemtu} - {self.diemden}"