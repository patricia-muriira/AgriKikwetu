from django.urls import path
from django.views.generic import TemplateView
from .views import ImageUploadView
from . import views

urlpatterns = [
    path('upload/', ImageUploadView.as_view(), name='image_upload'),
    path('', TemplateView.as_view(
        template_name='plant_disease/upload.html'), name='upload-form'),
    path('weather/', views.get_weather, name='get_weather'),
    path('chat/', views.chat_with_bot, name='chat_with_bot'),



]
