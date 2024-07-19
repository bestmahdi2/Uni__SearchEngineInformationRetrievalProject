from . import views
from django.urls import path

app_name = 'core'

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
]
