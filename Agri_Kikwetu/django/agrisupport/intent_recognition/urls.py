
from django.urls import path
from . import views

urlpatterns = [
    path('handle-intent/', views.handle_intent, name='handle_intent'),
]
