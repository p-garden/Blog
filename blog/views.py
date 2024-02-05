
from django.views.generic import ListView, DetailView
from .models import Post, Category


class PostList(ListView):
    model = Post
    ordering = '-pk' #게시물 최신 순으로 보기 설정
    #template_name = 'blog/post_list.html'

    def get_context_data(self, **kwargs):
        context= super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count']=Post.objects.filter(category=None).count()
        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

# Create your views here.
"""def index(request):
    posts = Post.objects.all().order_by('-pk') #최신순으로 보기
    return render(
        request,
        'blog/post_list.html', #blog 폴더의 템플릿중 index파일을 반환
        {
            'posts': posts,

        }
    )"""


"""def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)   #해당 pk값을 만족하는 레코드를 가져옴

    return render(
        request,
        'blog/post_detail.html', #해당 파일 반환
        {
            'post': post
        }
    )"""
