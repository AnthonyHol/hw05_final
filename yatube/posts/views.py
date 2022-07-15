from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.urls import reverse
from django.views.generic import CreateView, TemplateView, UpdateView

from yatube.settings import POSTS_PER_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def _get_page_obj(request, posts):
    """Функция получения объекта страницы"""
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def index(request) -> HttpResponse:
    """Функция отображения для главной страницы."""
    posts = Post.objects.all()

    context = {'page_obj': _get_page_obj(request, posts)}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug: str) -> HttpResponse:
    """Функция отображения для страницы с постами конкретной группы."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()

    context = {
        'group': group,
        'page_obj': _get_page_obj(request, posts),
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username: str) -> HttpResponse:
    """Функция отображения для страницы с профилем пользователя."""
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    following = user.is_authenticated and user.following.exists()
    context = {
        'profile': user,
        'page_obj': _get_page_obj(request, posts),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id: int) -> HttpResponse:
    """Функция отображения для страницы с информацией о конкретном посте."""
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    following = (
        request.user.is_authenticated
        and post.author.following.filter(user=request.user).exists()
    )
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': form,
            'comments': comments,
            'following': following,
        },
    )


@login_required
def post_create(request) -> HttpResponse:
    """Функция отображения для страницы создания постов."""
    form = PostForm(request.POST or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(f'/profile/{post.author.username}/')

    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': False},
    )


@login_required
def post_edit(request, post_id: int) -> HttpResponse:
    """Функция отображения для страницы редактирования постов."""
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)

    context = {'form': form, 'is_edit': True, 'post_id': post.id}

    return render(request, 'posts/create_post.html', context)


@login_required
def follow_index(request):
    authors: list = request.user.follower.values_list('author', flat=True)
    posts = Post.objects.filter(author__id__in=authors)
    context = {'page_obj': _get_page_obj(request, posts)}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)

    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('posts:profile', username=username)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    Follow.objects.get(user=request.user, author__username=username).delete()

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
