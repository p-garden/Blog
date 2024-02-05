from django.test import TestCase, Client
from bs4 import BeautifulSoup #html요소 다루는 라이브러리
from django.contrib.auth.models import User
from .models import Post, Category

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_PG = User.objects.create_user(username='PG', password='wjddnjs0418')
        self.user_SC = User.objects.create_user(username='SC', password='wjddnjs0418')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.post_001= Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world.',
            category=self.category_programming,
            author = self.user_PG
        )
        self.post_002= Post.objects.create(
            title='두 번째 포스트입니다.',
            content='Hello World. We are the world.',
            category=self.category_music,
            author=self.user_SC
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='category가 없음',
            author=self.user_SC
        )

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})',
                          categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)


    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django') #Do It Django라는 문구를 가진 a요소(<a>)를 찾아 변수에 담기
        self.assertEqual(logo_btn.attrs['href'], '/')  #변수의 href경로가 '/'인지 확인

        home_btn = navbar.find('a', text ='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn=navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')



    def test_post_list(self):
        #포스트가 있는 경우
        self.assertEqual(Post.objects.count(),3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)

        self.assertIn(self.user_PG.username.upper(), main_area.text)
        self.assertIn(self.user_SC.username.upper(), main_area.text)

        #포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)
        response = self.client.get('/blog/')
        soup=BeautifulSoup(response.content, 'html.parser')

        main_area=soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

    def test_post_detail(self):
        #1-1 포스트가 하나 있다.
        post_001 = Post.objects.create( #포스트 하나 만들기기
            title = '첫 번째 포스트 입니다.',
            content = 'Hello World. We are the world.',
            author = self.user_PG,
        )

        #1-2 그 포스트의 url은 'blog/1/'이다.
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        #2 첫 번째 포스트의 상세 페이지 테스트
        #2.1 첫번째 포스트의 url로 접근하면 정상적으로 작동한다.(status code: 200).
        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content, 'html.parser')

        #2-2 포스트 목록 페이지와 똑같은 내베게이션 바가 있다.
        #navbar= soup.nav
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('About Me', navbar.text)
        self.navbar_test(soup)

        #2-3 첫번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        self.assertIn(post_001.title, soup.title.text)

        #2-4 첫번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id = 'main-area')
        post_area =main_area.find('div', id = 'post-area')
        self.assertIn(post_001.title, post_area.text)

        #2-5 첫번째 포스트의 작성자가 포스트 영역에있다.
        self.assertIn(self.user_PG.username.upper(), post_area.text)

        #2-6 첫번째 포스트의 내용이 포스트 영역에 있다.
        self.assertIn(post_001.content, post_area.text)