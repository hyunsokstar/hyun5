from django.urls import path, re_path, include
from . import views

app_name = 'images'
urlpatterns = [

    # 피드뷰 상세 보기
    re_path(
        r'^(?P<image_id>\d+)/$',
        view = views.ImageDetail.as_view(),
        name='feed'
    ),

    re_path(
        r'^search/$',
        view=views.Search.as_view(),
        name='search'
    ),

    re_path(
        r'^$',
        view=views.Feed.as_view(),
        name='feed'
    ),

    # 좋아요
    re_path(
        r'^(?P<image_id>\w+)/likes/',
        view=views.LikeImage.as_view(),
        name="like_image"
    ),
    # 싫어요
    re_path(
        r'^(?P<image_id>\w+)/unlikes/',
        view=views.UnLikeImage.as_view(),
        name="unlike_image"
    ),

    #  삭제에 대한 url 패턴 추가
    re_path(
        r'^(?P<image_id>\d+)/comments/(?P<comment_id>\d+)/$',
        view=views.DeleteComments.as_view(),
        name="delete_Comments"
    ),

    re_path(
        r'^(?P<image_id>\d+)/comments/',
        view=views.CommentOnImage.as_view(),
        name="comment_image"
    ),

]
