from django.db import models

class TruongDaiHoc(models.Model):
    matruong = models.CharField(db_column="MATRUONG", max_length=5, primary_key=True)
    tentruong = models.CharField(db_column="TENTRUONG", max_length=200)
    loaitruong = models.CharField(db_column="LOAITRUONG", max_length=50, null=True, blank=True)
    logo = models.CharField(db_column="LOGO", max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "TRUONGDAIHOC"
