from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
    )
from .models import Post, Comment
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .forms import CommentForm
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.db.models import Q
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

    def get_queryset(self):
        queryset = super(PostListView, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = Post.objects.filter(
                Q(title__icontains=query) |
                Q(author__username=query) |
                Q(content__icontains=query)).order_by('-date_posted')
            return queryset
        else:
            return Post.objects.all().order_by('-date_posted')


class UserFavouriteListView(ListView):
    model = Post
    template_name = 'tweet/user_favourites.html'
    context_object_name = 'posts'
    paginate_by = 5

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     user = self.request.user
    #     context['favourite_posts'] = user.favourite.all().order_by('-id')
    #     return context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favourite_page'] = "active"
        return context

    def get_queryset(self):
        return Post.objects.filter(favourite=self.request.user).order_by('-date_posted')


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


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


#
# class CommentListView(ListView):
#     model = Comment
#     fields = ['content']
#     template_name = 'tweet/post_comments.html'
#     comments = Comment.objects.all()
#     #
#     # def get_queryset(self):
#     #     post = get_object_or_404(Post, id=self.kwargs.get('id'))
#     #     return Comment.objects.filter(post__in=post).order_by('-id')


def PostDetailView(request, pk):
    post = get_object_or_404(Post, id=pk)
    comments = Comment.objects.filter(post=post).order_by('-id')
    is_favourite = False
    is_liked = False
    if post.favourite.filter(id=request.user.id).exists():
        is_favourite = True
    if post.likes.filter(id=request.user.id).exists():
        is_liked = True
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            content = request.POST.get('content')
            comment = Comment.objects.create(post=post, user=request.user, content=content)
            comment.save()
            messages.success(request, 'Your comment has been posted')
            return HttpResponseRedirect(post.get_absolute_url())
        else:
            comment_form = CommentForm()

    context = {
        'is_liked': is_liked,
        'is_favourite': is_favourite,
        'post': post,
        'total_likes': post.total_likes(),
        'comments': comments,
        'comment_form': CommentForm,
    }

    return render(request, 'tweet/post_detail.html', context)


# class PostDetailView(FormMixin, DetailView):
#     model = Post
#     form_class = CommentForm
#
#     def get_success_url(self):
#         return reverse('tweet-detail', kwargs={'pk': self.object.id})
#
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         MyObject = self.object  # for accesing the current object
#         context['total_likes'] = MyObject.total_likes()
#         context['comments'] = Comment.objects.filter(post=MyObject)
#         if self.request == 'POST':
#             comment_form = CommentForm(self.request.POST)
#             if comment_form.is_valid():
#                 comment_form.save()
#         else:
#             comment_form = CommentForm()
#         context['comment_form'] = comment_form
#         return context


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


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.user:
            return True
        else:
            return False

    def get_success_url(self, **kwargs):
        return reverse_lazy('tweet-detail', args=(self.object.post.id,))


def about(request):
    return render(request, 'tweet/about.html', context={'title': "about", "about_page": "active"})


def contact(request):
    if request.method == "POST":
        message_name = request.POST['message-name']
        message_email = request.POST['message-email']
        message = request.POST['message-email']

        # send an Email
        send_mail(
            f'Query by {message_name}',  # subject
            message,  # message
            message_email,  # from
            ['bahadur.romith@gmail.com', 'bahadur.rochan@gmail.com'],  # To Email
        )

        messages.success(request, f'Thanks {message_name} \n We recieved your email and will respong shortly...')
        return render(request, 'tweet/contact.html', {'message_name': message_name})

    else:
        return render(request, 'tweet/contact.html')


def like_post(request):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(post.get_absolute_url())


def favourite_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
    else:
        post.favourite.add(request.user)
    return HttpResponseRedirect(post.get_absolute_url())
