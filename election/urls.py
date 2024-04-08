from django.urls import path

from .views import ElectionList, ElectionDetail
from . import views

app_name = 'election'

urlpatterns = [
    path('', ElectionList.as_view(), name='election-list'),
    path('<int:pk>/', ElectionDetail.as_view(), name='election-detail'),
    path('<int:pk>/vote', views.vote, name='vote'),
    path('contact/', views.contact, name='contact')
]
