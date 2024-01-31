from django.test import TestCase, Client
from bs4 import BeautifulSoup #html요소 다루는 라이브러리
from .models import Post

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

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
        #1.1포스트 목록 페이지 가져오기
        response = self.client.get('/blog/')   #client는 가상의 사용자 / '~/blog/'에 접속했을 때 웹페이지 정보 response에 저장

        #1.2 정상적으로 페이지가 로드됨
        self.assertEqual(response.status_code, 200) #정상적으로 웹페이지 로드되면 200반환 / 로드X면 404오류 반환

        #1.3 페이지 타이틀은 'Blog'이다.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog') #title을 뽑아서 Blog 맞는 지 확인

        #1.4 내비게이션 바가있다.
        #navbar = soup.nav #soup의 nav만 가져와 navbar에 저장

        #1.5 Blog, About Me라는 문구가 내비게이션 바에 있다.
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('About Me', navbar.text) #텍스트 중에 'Blog'와 'About Me가 있는 지 확인'
        self.navbar_test(soup)

        #2.1 메인 영역에 게시물이 하나도 없다면
        self.assertEqual(Post.objects.count(),0) #작성된 포스트가 0개인지 확인

        #2-2 '아직 게시물이 없습니다'라는 문구 보인다.
        main_area = soup.find('div', id='main-area') #id가 'main-area'인 div를 찾아 main_area에 저장
        self.assertIn('아직 게시물이 없습니다.', main_area.text) #게시물 없다는 문구 나오는지 확인

        #3-1 게시물이 2개있다면
        post_001= Post.objects.create(   #포스트2개가 잘 생성되었는지 확인
            title = '첫 번째 포스트입니다. ',
            content = 'Hello World, We are the world.',
        )
        post_002 = Post.objects.create(
            title = '두번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
        )
        self.assertEqual(Post.objects.count(), 2)

        #3-2 포스트 목록 페이지를 새로고침했을 때
        response=self.client.get('/blog/') #새로고침 하기위해 1-1 ~ 1-3 반복
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code,200)

        #3-3 메인 영역에 포스트 2개의 타이틀이 존재
        main_area = soup.find('div', id='main-area') #두 포스트의 타이틀이 id가 main-area인 요소에 있는 지 확인
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)

        #3-4 '아직 게시물이 없습니다'라는 문구는 더이상 보이지 않음
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text) #포스트 생성되었으면 해당문구는 없어야함\

    def test_post_detail(self):
        #1-1 포스트가 하나 있다.
        post_001 = Post.objects.create( #포스트 하나 만들기기
            title = '첫 번째 포스트 입니다.',
            content = 'Hello World. We are the world.',
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
        #2-5 첫번째 포스트의 작성자가 포스트 영역에있다.(아직X)

        #2-6 첫번째 포스트의 내용이 포스트 영역에 있다.
        self.assertIn(post_001.content, post_area.text)