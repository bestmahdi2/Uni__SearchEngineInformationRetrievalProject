from . import views
from django.urls import path

app_name = 'Phase3'

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
    path('search_retrieve_page', views.search_retrieve_page, name='search_retrieve_page'),
    path('measure_system_page', views.measure_system_page, name='measure_system_page'),
    # APIs
    path('progress/', views.progress, name='progress'),
    path('search_retrieve_api', views.search_retrieve_api, name='search_retrieve_api'),
    path('measure_system_api', views.measure_system_api, name='measure_system_api'),
]
