from django.core.files.storage import FileSystemStorage
from django.db import models

fs = FileSystemStorage(location='images/cameras/')


class Camera(models.Model):
    id = models.AutoField(primary_key=True)
    hostname = models.CharField(max_length=50,verbose_name='IP адрес')
    is_active = models.BooleanField(default=False, db_index=True,verbose_name='Активная/неактивная камера')
    last_activities = models.DateTimeField(auto_now_add=True)
