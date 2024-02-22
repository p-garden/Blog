from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from django.db.models import Q

class PostList(ListView):
    model = Post
    ordering = '-pk' #게시물 최신 순으로 보기 설정
    paginate_by = 5
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
        context['comment_form'] = CommentForm
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
            response = super(PostCreate, self).form_valid(form)  #from_valid결과값을 임시 저장

            tags_str = self.request.POST.get('tags_str') #post_form.html에서 tags_str의 input값 가져오기
            if tags_str:               #태그가 존재한다면  처리해줘야함
                tags_str = tags_str.strip() #태그 각자 분리후 , ; 모두 구분자로 처리

                tags_str =tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()  #각 태그의 앞뒤 공백 제거
                    tag, is_tag_created = Tag.objects.get_or_create(name=t) #tag에 tag모델의 인스턴스 is~에 인스턴스 생성되었는지 부울값 저장
                    if is_tag_created:  #새로 생성하였다면 slug값 생성
                        tag.slug = slugify(t, allow_unicode=True) #한글도 허용
                        tag.save()
                    self.object.tags.add(tag) #새로운 포스트에 태그 추가
            return response

        else:
            return redirect('/blog/') #로그인 안된 경우는 원래 블로그 페이지로 돌려 보내기


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default']= '; '.join(tags_str_list)
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:               #태그가 존재한다면  처리해줘야함
            tags_str = tags_str.strip() #태그 각자 분리후 , ; 모두 구분자로 처리

            tags_str  =tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()  #각 태그의 앞뒤 공백 제거
                tag, is_tag_created = Tag.objects.get_or_create(name=t) #tag에 tag모델의 인스턴스 is~에 인스턴스 생성되었는지 부울값 저장
                if is_tag_created:  #새로 생성하였다면 slug값 생성
                    tag.slug = slugify(t, allow_unicode=True) #한글도 허용
                    tag.save()
                self.object.tags.add(tag) #새로운 포스트에 태그 추가
        return response

def new_comment(request, pk):
    if request.user.is_authenticated:
        post=get_object_or_404(Post, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post=post
                comment.author=request.user
                comment.save()
                return redirect(comment.get_absolute_url())

        else:
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

class PostSearch(PostList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q) #타이틀에 q를포함했거나 태그에q를포함한 경우
        ).distinct()
        return post_list

    def get_context_data(self, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'

        return context
# Create your views here
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
