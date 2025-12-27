from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('api/chat/', views.chat_api, name='chat_api'),
]