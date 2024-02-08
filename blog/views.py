from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag


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

def category_page(request,slug):
    if slug=='no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category=Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)


    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
        }
    )

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'tag': tag,
        }
    )

class PostCreate(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user #웹사이트의 방문자
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):    #로그인 된 경우
            form.instance.author = current_user
            return super(PostCreate, self).form_valid(form) #새로 작성한 포스트의 author필드에 현재 방문자 담기
        else:
            return redirect('/blog/') #로그인 안된 경우는 원래 블로그 페이지로 돌려 보내기



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
