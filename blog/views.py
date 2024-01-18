from django.shortcuts import render
from .models import Post

# Create your views here.
def index(request):
    posts = Post.objects.all().order_by('-pk')
    return render(
        request,
        'blog/index.html', #blog 폴더의 템플릿중 index파일을 반환
        {'posts': posts

        }
    )
