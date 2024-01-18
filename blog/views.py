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

def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)   #해당 pk값을 만족하는 레코드를 가져옴

    return render(
        request,
        'blog/single_post_page.html', #해당 파일 반환
        {
            'post': post
        }
    )
