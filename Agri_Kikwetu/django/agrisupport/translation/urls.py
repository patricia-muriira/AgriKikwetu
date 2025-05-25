from django.urls import path
from .views import handle_translation_and_intent

urlpatterns = [
    path('translate-intent/', handle_translation_and_intent, name='translate_intent'),
]
