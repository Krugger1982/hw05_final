from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import (Group, Post, User, Follow)


def get_page_from_paginator(list_items, request):
    """ Функция для вызова паджинатора.
        Возвращает объект page_obg с разбитыми постранично элементами.
        """
    page_number = request.GET.get('page')
    p = Paginator(list_items, settings.PAGINATION_COUNT)
    return p.get_page(page_number)


def index(request):
    post_list = Post.objects.all()
    context = {
        'page_obj': get_page_from_paginator(post_list, request)
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page_from_paginator(posts, request)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author_profile = get_object_or_404(User, username=username)
    author_posts = author_profile.posts.all()
    page_obj = get_page_from_paginator(author_posts, request)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author_profile
        ).exists()
    context = {
        'author': author_profile,
        'following': following,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    current_post = get_object_or_404(Post, id=post_id)
    comments = current_post.comments.all()
    context = {
        'current_post': current_post,
        'form': CommentForm(),
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """ Добавляет новую запись."""
    is_edit = False
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user.username)
    # если запрос не POST, a GET или форма невалидна - создаем пустую форму
    context = {'form': form, 'is_edit': is_edit}
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    """ Редактирует существующую запись."""
    current_post = get_object_or_404(Post, pk=post_id)
    if request.user.pk != current_post.author_id:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=current_post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    # В случае если форма невалидна (или запрос GET)
    # создается форма с данными для редактирования
    context = {
        'form': form, 'post': current_post, 'is_edit': True}
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    """ Добавляет комментарий к посту."""
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """ Представляет страницу со списком постов всех авторов,
        на которых подписан текущий пользователь"""
    follows = request.user.following.all()
    followed_posts = []
    for follow in follows:
        followed_posts += list(follow.author.posts.all())
    # Весь набор постов для ленты должен быть отсортирован по дате
    # от свежих постов к более старым
    followed_posts.sort(key=lambda post: post.pub_date, reverse=True)
    page_obj = get_page_from_paginator(followed_posts, request)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """ Функция реализует возможность подписаться на автора."""
    author = get_object_or_404(User, username=username)
    # Если подписка уже есть, повторный запрос на подписку
    # будет проигнорирован
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """ Функция реализует возможность отписаться от автора."""
    author = get_object_or_404(User, username=username)
    get_object_or_404(Follow, user=request.user, author=author).delete()
    return redirect('posts:profile', username)
