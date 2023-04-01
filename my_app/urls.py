from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('about/', views.About.as_view(), name='about'),
    path('add_story/', views.AddStory.as_view(), name='add_story'),
    path('search/', views.Search.as_view(), name='search'),
    path('<int:id>/', views.MyPage.as_view(), name='my_page'),
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('<slug:slug>/like', views.PostLike.as_view(), name='post_like'),
    path('bookmark/<slug:slug>', views.Bookmark.as_view(), name='bookmark'),
    path('<slug:slug>/update', views.UpdatePost.as_view(), name='update_post'),
    path('<slug:slug>/delete', views.DeletePost.as_view(), name='delete_post'),
    path('more_stories', views.PostMoreStories.as_view(), name='more_stories'),
    path('<int:id>/delete_comment', views.DeleteComment.as_view(), name='delete_comment')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)