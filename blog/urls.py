from django.urls import path
from . import views   #이 폴더내의 views.py 파일 참조
urlpatterns= [
    #path('<int:pk>/', views.single_post_page), FBV로 개별 게시물 상세 페이지 들어가는 url
    #path('', views.index),    #views파일의 index 함수 참조
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),
]
