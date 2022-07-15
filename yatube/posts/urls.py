from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views
from .views import (
    FollowPageView,
    GroupPageView,
    HomePageView,
    PostCreatePageView,
    PostDetailPageView,
    PostEditPageView,
    ProfileFollowPageView,
    ProfilePageView,
    ProfileUnfollowPageView,
)

app_name = 'posts'

urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('group/<slug:slug>/', GroupPageView.as_view(), name='group_list'),
    path('profile/<str:username>/', ProfilePageView.as_view(), name='profile'),
    path(
        'posts/<int:post_id>/',
        PostDetailPageView.as_view(),
        name='post_detail',
    ),
    path(
        'posts/<int:post_id>/edit/',
        login_required(PostEditPageView.as_view()),
        name='post_edit',
    ),
    path(
        'follow/',
        login_required(FollowPageView.as_view()),
        name='follow_index',
    ),
    path(
        'create/',
        login_required(PostCreatePageView.as_view()),
        name='post_create',
    ),
    path(
        'posts/<int:post_id>/comment/', views.add_comment, name='add_comment'
    ),
    path(
        'profile/<str:username>/follow/',
        login_required(ProfileFollowPageView.as_view()),
        name='profile_follow',
    ),
    path(
        'profile/<str:username>/unfollow/',
        login_required(ProfileUnfollowPageView.as_view()),
        name='profile_unfollow',
    ),
    # path(
    #     'profile/<str:username>/follow/',
    #     views.profile_follow,
    #     name='profile_follow',
    # ),
    # path(
    #     'profile/<str:username>/unfollow/',
    #     views.profile_unfollow,
    #     name='profile_unfollow',
    # ),
]
