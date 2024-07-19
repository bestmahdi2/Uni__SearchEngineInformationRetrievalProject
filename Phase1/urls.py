from . import views
from django.urls import path

app_name = 'Phase1'

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
    # Preprocess Pages
    path('preprocess_text_page', views.preprocess_text_page, name='preprocess_text_page'),
    path('preprocess_file_page', views.preprocess_file_page, name='preprocess_file_page'),
    # APIs
    path('preprocess_text', views.preprocess_text_api, name='preprocess_text'),
    path('preprocess_file', views.preprocess_file_api, name='preprocess_file'),
    path('progress/', views.progress, name='progress'),
]
