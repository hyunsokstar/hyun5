from django.urls import path, re_path, include
from . import views

urlpatterns = [
    re_path(
        r'^$',
        view=views.Notifications.as_view(),
        name='notifications'
    )
]
