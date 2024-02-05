from django.db import models
from django.contrib.auth.models import User
import os
# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to ='blog/images/%Y/%m/%d', blank = True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank = True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author= models.ForeignKey(User,null=True, on_delete=models.SET_NULL)  #해당 유저 삭제되면 게시물의 작성자는 빈칸

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)  #파일명 반환

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]  #파일 확장자명 반환