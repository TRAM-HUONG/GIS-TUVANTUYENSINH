from django.db import models # TruongDaiHoc (University) model 
class TruongDaiHoc(models.Model): 
    matruong = models.CharField(db_column="MATRUONG", max_length=5, primary_key=True) 
    tentruong = models.CharField(db_column="TENTRUONG", max_length=200) 
    loaitruong = models.CharField(db_column="LOAITRUONG", max_length=50, null=True, blank=True) 
    logo = models.CharField(db_column="LOGO", max_length=255, null=True, blank=True) 
    # Additional details for the university 
    madvhc = models.CharField(db_column="MADVHC", max_length=5, null=True, blank=True) 
    diachi = models.TextField(db_column="DIACHI", null=True, blank=True) 
    website = models.CharField(db_column="WEBSITE", max_length=255, null=True, blank=True) 
    email = models.CharField(db_column="EMAIL", max_length=100, null=True, blank=True) 
    dienthoai = models.CharField(db_column="DIENTHOAI", max_length=30, null=True, blank=True) 
    class Meta: 
        managed = False 
        db_table = "TRUONGDAIHOC" # Table name in the database 
    def __str__(self): 
        return f"{self.matruong} - {self.tentruong}"

# TruongDaiHoc (University) model
class TruongDaiHoc(models.Model): 
    matruong = models.CharField(db_column="MATRUONG", max_length=5, primary_key=True) 
    tentruong = models.CharField(db_column="TENTRUONG", max_length=200) 
    loaitruong = models.CharField(db_column="LOAITRUONG", max_length=50, null=True, blank=True) 
    logo = models.CharField(db_column="LOGO", max_length=255, null=True, blank=True) 
    # Additional details for the university 
    madvhc = models.CharField(db_column="MADVHC", max_length=5, null=True, blank=True) 
    diachi = models.TextField(db_column="DIACHI", null=True, blank=True) 
    website = models.CharField(db_column="WEBSITE", max_length=255, null=True, blank=True) 
    email = models.CharField(db_column="EMAIL", max_length=100, null=True, blank=True) 
    dienthoai = models.CharField(db_column="DIENTHOAI", max_length=30, null=True, blank=True) 

    class Meta: 
        managed = False 
        db_table = "TRUONGDAIHOC" # Table name in the database 

    def __str__(self): 
        return f"{self.matruong} - {self.tentruong}"
<<<<<<< HEAD
=======


>>>>>>> feature/home
# HinhAnh (Image) model to store images related to universities
class HinhAnh(models.Model):
    mahinh = models.CharField(db_column="MAHINH", primary_key=True, max_length=5)
    tenfile = models.CharField(db_column="TENFILE", max_length=255)
    loai = models.CharField(db_column="LOAI", max_length=30)
    madoituong = models.CharField(db_column="MADOITUONG", max_length=5)
    mota = models.CharField(db_column="MOTA", max_length=200, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "HINHANH"  # Table name in the database

    def __str__(self):
        return self.tenfile

<<<<<<< HEAD

# CHITIETTRUONG (University Detail) model

=======
# CHITIETTRUONG (University Detail) model
>>>>>>> feature/home
class CHITIETTRUONG(models.Model):
    matruong = models.CharField(db_column="MATRUONG", max_length=5, primary_key=True)
    mota = models.TextField(db_column="MOTA", null=True, blank=True)
    ghichu = models.CharField(db_column="GHICHU", max_length=300, null=True, blank=True)

    class Meta:
        managed = False
<<<<<<< HEAD

        db_table = "CHITIETTRUONG"  # Tên bảng trong cơ sở dữ liệu

        db_table = "CHITIETTRUONG"  # Table name in the database


    def __str__(self):
        return f"{self.matruong} - {self.mota}"
    

# NganhHoc (Major) model

=======
        db_table = "CHITIETTRUONG"  # Table name in the database

    def __str__(self):
        return f"{self.matruong} - {self.mota}"
    
# NganhHoc (Major) model
>>>>>>> feature/home
class NganhHoc(models.Model):
    manganh = models.CharField(db_column="MANGANH", primary_key=True, max_length=5)
    tennganh = models.CharField(db_column="TENNGANH", max_length=200)
    linhvuc = models.CharField(db_column="LINHVUC", max_length=100)
    mota = models.TextField(db_column="MOTA", null=True, blank=True)

    class Meta:
        managed = False
<<<<<<< HEAD

        db_table = "NGANHHOC"  # Tên bảng trong cơ sở dữ liệu

    def __str__(self):
        return f"{self.manganh} - {self.tennganh}"

=======
>>>>>>> feature/home
        db_table = "NGANHHOC"  # Table name in the database

    def __str__(self):
        return f"{self.manganh} - {self.tennganh}"

# ChiTietNganh (Major Details) model
<<<<<<< HEAD

=======
>>>>>>> feature/home
class ChiTietNganh(models.Model):
    MACTN = models.CharField(db_column="MACTN", primary_key=True, max_length=5)  # Thay id bằng MACTN làm khóa chính
    matruong = models.ForeignKey('TruongDaiHoc', on_delete=models.CASCADE, db_column="MATRUONG")
    manganh = models.ForeignKey('NganhHoc', on_delete=models.CASCADE, db_column="MANGANH")
    # Các trường khác như học phí, thời gian học

    class Meta:
        managed = False
        db_table = "CHITIETNGANH"

    def __str__(self):
<<<<<<< HEAD

        return f"{self.matruong.tentruong}"

=======
>>>>>>> feature/home
        return f"{self.matruong.tentruong}"
