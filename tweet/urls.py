from django.urls import path
from . import views
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, UserPostListView

urlpatterns = [
    path('', PostListView.as_view(), name='tweet-home'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-tweets'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='tweet-detail'),
    path('post/new/', PostCreateView.as_view(), name='tweet-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='tweet-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='tweet-delete'),
    path('about/', views.about, name='tweet-about')
]
