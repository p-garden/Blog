from django.db import models
import os
# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    head_image = models.ImageField(upload_to ='blog/images/%Y/%m/%d', blank = True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank = True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #author:

    def __str__(self):
        return f'[{self.pk}]{self.title}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)  #파일명 반환

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]  #파일 확장자명 반환