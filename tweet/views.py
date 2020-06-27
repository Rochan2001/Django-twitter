from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
# Create your views here.


# def home(request):
#     context = {'posts': Post.objects.all(), "home_page": "active"}
#     return render(request, 'tweet/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'tweet/home.html'
    context_object_name = 'posts'
    extra_context = {"home_page": "active"}
    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.extra_context)
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'tweet/user_posts.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_tweets"] = "active"
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        MyObject = self.object  # for accesing the current object
        context['total_likes'] = MyObject.total_likes()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        else:
            return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        else:
            return False


def about(request):
    return render(request, 'tweet/about.html', context={'title': "about", "about_page": "active"})


def like_post(request):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(post.get_absolute_url())
