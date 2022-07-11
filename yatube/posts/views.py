from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, TemplateView, UpdateView

from yatube.settings import POSTS_PER_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

CACHE_TIME = 20


def _get_page_obj(request, posts):
    """Функция получения объекта страницы"""
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


class HomePageView(TemplateView):
    model = Post
    template_name: str = 'posts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = _get_page_obj(self.request, Post.objects.all())

        return context


class GroupPageView(TemplateView):
    model = Group
    template_name: str = 'posts/group_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = get_object_or_404(Group, slug=self.kwargs['slug'])

        context['group'] = group
        context['page_obj'] = _get_page_obj(self.request, group.posts.all())

        return context


class ProfilePageView(TemplateView):
    model = Post
    template_name: str = 'posts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs['username'])

        context['username'] = user
        context['page_obj'] = _get_page_obj(self.request, user.posts.all())
        context['following'] = (
            self.request.user.is_authenticated and user.following.exists()
        )

        return context


class PostDetailPageView(TemplateView):
    model = Post
    template_name: str = 'posts/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        context['post'] = post
        context['form'] = CommentForm(self.request.POST or None)
        context['comments'] = post.comments.all()
        context['following'] = (
            self.request.user.is_authenticated
            and post.author.following.filter(user=self.request.user).exists()
        )
        return context


class PostEditPageView(UpdateView):
    model = Post
    form_class = PostForm
    template_name: str = 'posts/create_post.html'

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        if post.author != request.user:
            return HttpResponseRedirect(
                reverse('posts:post_detail', kwargs={'post_id': post.id})
            )

        form = self.form_class(
            request.POST or None,
            files=request.FILES or None,
            instance=post,
        )

        return render(
            request,
            self.template_name,
            {'form': form, 'is_edit': True, 'post_id': post.id},
        )

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        form = self.form_class(
            request.POST or None,
            files=request.FILES or None,
            instance=post,
        )

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('posts:post_detail', kwargs={'post_id': post.id})
            )

        return render(
            request,
            self.template_name,
            {'form': form, 'is_edit': True, 'post_id': post.id},
        )


class FollowPageView(TemplateView):
    template_name: str = 'posts/follow.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        authors: list = user.follower.values_list('author', flat=True)
        posts = Post.objects.filter(author__id__in=authors)

        context['page_obj'] = _get_page_obj(self.request, posts)

        return context


class PostCreatePageView(LoginRequiredMixin, CreateView):
    model = Post

    fields = ["group", "text", "image"]
    template_name = 'posts/create_post.html'

    def get(self, request, *args, **kwargs):
        form = PostForm(request.POST or None, files=request.FILES or None)
        return render(
            request,
            self.template_name,
            {'form': form, 'is_edit': False},
        )

    def form_valid(self, form):
        self.post = form.save(commit=False)
        self.post.author = self.request.user
        self.post_instance = form.instance
        self.post.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'posts:profile', kwargs={'username': self.post.author.username}
        )


# не получилось реализовать в CBV
@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = request.user

    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect('posts:profile', username=username)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.get(user=user, author__username=username).delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def add_comment(request, post_id):
    """Функция отображения добавления комментария к посту"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
