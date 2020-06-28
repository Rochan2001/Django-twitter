from django.urls import path
from . import views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    CommentDeleteView,
    UserFavouriteListView)

urlpatterns = [
    path('', PostListView.as_view(), name='tweet-home'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-tweets'),
    path('post/<int:pk>/', PostDetailView, name='tweet-detail'),
    path('post/new/', PostCreateView.as_view(), name='tweet-create'),
    path('post/<int:pk>/favourite_post/', views.favourite_post, name='favourite-post'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='tweet-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='tweet-delete'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='tweet-comment-delete'),
    path('like/', views.like_post, name='like_post'),
    path('about/', views.about, name='tweet-about'),
    path('favourites/', UserFavouriteListView.as_view(), name='post-favourite-list'),
    path('contact/', views.contact, name='tweet-contact')
]
