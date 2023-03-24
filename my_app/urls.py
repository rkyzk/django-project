from . import views
from django.urls import path

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('about/', views.About.as_view(), name='about'),
    path('add_story/', views.AddStory.as_view(), name='add_story'),
    path('search/', views.Search.as_view(), name='search'),
    path('<int:id>/', views.MyPage.as_view(), name='my_page'),
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    #path('like/<slug:slug>', views.PostLike.as_view(), name='post_like'),
    # path('bookmark/<slug:slug>', views.Bookmark.as_view(), name='bookmark')   
]