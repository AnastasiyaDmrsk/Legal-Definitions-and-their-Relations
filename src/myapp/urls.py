from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('result/', views.result, name='result'),
    path('download/', views.download_definitions_file, name='download_definitions_file'),
    path('download-annotations/', views.download_annotations, name='download_annotations'),
    path('download-sentences/', views.download_sentences, name='download_sentences'),
]