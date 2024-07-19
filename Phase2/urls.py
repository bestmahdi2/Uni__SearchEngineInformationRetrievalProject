from . import views
from django.urls import path

app_name = 'Phase2'

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
    # Other Pages
    path('index_construction_page', views.index_construction_page, name='index_construction_page'),
    path('index_compression_page', views.index_compression_page, name='index_compression_page'),
    path('add_document_page', views.add_document_page, name='add_document_page'),
    path('remove_document_page', views.remove_document_page, name='remove_document_page'),
    # APIs
    path('progress/', views.progress, name='progress'),
    path('add_document_single_api', views.add_document_single_api, name='add_document_single_api'),
    path('remove_document_single_api', views.remove_document_single_api, name='remove_document_single_api'),
    path('index_document_api', views.index_document_api, name='index_document_api'),
    path('index_compression_api', views.index_compression_api, name='index_compression_api'),
    ]
