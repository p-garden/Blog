from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os
# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=50, unique=True) #카테고리 이름 중복X
    slug=models.SlugField(max_length=200, unique=True, allow_unicode=True) #텍스트로된 URL 한글도 가능하게 설정

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories' #복수형 이름 'categorys' -> 'categories'로 수정하기

class Tag(models.Model):
    name=models.CharField(max_length=50)
    slug=models.SlugField(max_length=200, unique=True, allow_unicode=True) #텍스트로된 URL 한글도 가능하게 설정

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'

class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = MarkdownxField()

    head_image = models.ImageField(upload_to ='blog/images/%Y/%m/%d', blank = True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank = True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author= models.ForeignKey(User,null=True, on_delete=models.SET_NULL)  #해당 유저 삭제되면 게시물의 작성자는 빈칸
    category = models.ForeignKey(Category, null=True,blank=True, on_delete=models.SET_NULL)
    tags= models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)  #파일명 반환

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]  #파일 확장자명 반환

    def get_content_markdown(self):
        return markdown(self.content)

class Comment(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'