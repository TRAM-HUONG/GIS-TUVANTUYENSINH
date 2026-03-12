from django.db import models

class TinhThanh(models.Model):
    matinh = models.CharField(db_column="MATINH", primary_key=True, max_length=5)
    tentinh = models.CharField(db_column="TENTINH", max_length=100)

    class Meta:
        managed = False
        db_table = "TINHTHANH"

    def __str__(self):
        return f"{self.matinh} - {self.tentinh}"


class DonViHanhChinh(models.Model):
    madvhc = models.CharField(db_column="MADVHC", primary_key=True, max_length=5)
    tendvhc = models.CharField(db_column="TENDVHC", max_length=100)
    loai = models.CharField(db_column="LOAI", max_length=30, null=True, blank=True)

    matinh = models.ForeignKey(
        TinhThanh,
        on_delete=models.RESTRICT,
        db_column="MATINH",
        related_name="donvihanhchinhs",
    )

    class Meta:
        managed = False
        db_table = "DONVIHANHCHINH"

    def __str__(self):
        return f"{self.madvhc} - {self.tendvhc}"



class TruongDaiHoc(models.Model):
    matruong = models.CharField(db_column="MATRUONG", primary_key=True, max_length=5)
    tentruong = models.CharField(db_column="TENTRUONG", max_length=200)
    loaitruong = models.CharField(
        db_column="LOAITRUONG", max_length=50, null=True, blank=True
    )



    madvhc = models.ForeignKey(
        DonViHanhChinh,
        on_delete=models.RESTRICT,
        db_column="MADVHC",
        related_name="truongs",
    )


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
        return f"{self.matruong} - {self.tentruong}"


class ChiTietTruong(models.Model):
    mactt = models.CharField(db_column="MACTT", primary_key=True, max_length=5)

    matruong = models.ForeignKey(
        TruongDaiHoc,
        on_delete=models.CASCADE,
        db_column="MATRUONG",
        related_name="chi_tiet",
    )

    mota = models.TextField(db_column="MOTA", null=True, blank=True)
    ghichu = models.CharField(db_column="GHICHU", max_length=300, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "CHITIETTRUONG"

    def __str__(self):
        return f"{self.mactt} - {self.matruong_id}"


class NganhHoc(models.Model):
    manganh = models.CharField(db_column="MANGANH", primary_key=True, max_length=5)
    tennganh = models.CharField(db_column="TENNGANH", max_length=200)
    linhvuc = models.CharField(db_column="LINHVUC", max_length=100, null=True, blank=True)

    mota = models.TextField(db_column="MOTA", null=True, blank=True)

    class Meta:
        managed = False
        db_table = "NGANHHOC"

    def __str__(self):

        return f"{self.manganh} - {self.tennganh}"


class ChiTietNganh(models.Model):
    mactn = models.CharField(db_column="MACTN", primary_key=True, max_length=5)

    matruong = models.ForeignKey(
        TruongDaiHoc,
        on_delete=models.CASCADE,
        db_column="MATRUONG",
        related_name="ctn_nganhs",
    )
    manganh = models.ForeignKey(
        NganhHoc,
        on_delete=models.CASCADE,
        db_column="MANGANH",
        related_name="ctn_truongs",
    )

    hocphi = models.IntegerField(db_column="HOCPHI", null=True, blank=True)
    thoigianhoc = models.IntegerField(db_column="THOIGIANHOC", null=True, blank=True)

    class Meta:
        managed = False
        db_table = "CHITIETNGANH"

    def __str__(self):
        return f"{self.mactn} - {self.matruong_id} - {self.manganh_id}"


# =========================================================
# ẢNH TRƯỜNG: HINHANH_TRUONG
# =========================================================
class HinhAnhTruong(models.Model):
    mahinh_truong = models.CharField(
        db_column="MAHINH_TRUONG", primary_key=True, max_length=5
    )

    matruong = models.ForeignKey(
        TruongDaiHoc,
        on_delete=models.CASCADE,  # DB: ON DELETE CASCADE
        db_column="MATRUONG",
        related_name="hinh_anh",
    )

    tenfile = models.CharField(db_column="TENFILE", max_length=255)
    tieude = models.CharField(db_column="TIEUDE", max_length=200, null=True, blank=True)
    mota = models.TextField(db_column="MOTA", null=True, blank=True)
    ngaytao = models.DateTimeField(db_column="NGAYTAO", null=True, blank=True)

    class Meta:
        managed = False
        db_table = "HINHANH_TRUONG"

    def __str__(self):
        return f"{self.mahinh_truong} - {self.matruong_id} - {self.tenfile}"


# =========================================================
# ẢNH NGÀNH: HINHANH_NGANH
# =========================================================
class HinhAnhNganh(models.Model):
    mahinh_nganh = models.CharField(
        db_column="MAHINH_NGANH", primary_key=True, max_length=5
    )

    manganh = models.ForeignKey(
        NganhHoc,
        on_delete=models.CASCADE,  # DB: ON DELETE CASCADE
        db_column="MANGANH",
        related_name="hinh_anh",
    )

    tenfile = models.CharField(db_column="TENFILE", max_length=255)
    tieude = models.CharField(db_column="TIEUDE", max_length=200, null=True, blank=True)
    mota = models.TextField(db_column="MOTA", null=True, blank=True)
    ngaytao = models.DateTimeField(db_column="NGAYTAO", null=True, blank=True)

    class Meta:
        managed = False
        db_table = "HINHANH_NGANH"

    def __str__(self):
        return f"{self.mahinh_nganh} - {self.manganh_id} - {self.tenfile}"

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

