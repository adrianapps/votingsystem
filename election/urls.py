from django.urls import path

from .views import (ElectionList, ElectionDetail, ElectionResult, ElectionUpdate, ElectionDelete,
                    ElectionCreate, CandidateCreate, CandidateDetail, CandidateUpdate, CandidateDelete, Contact)
from . import views

app_name = 'election'

urlpatterns = [
    path('', views.homepage_view, name="homepage"),
    path('elections', ElectionList.as_view(), name='election-list'),
    path('elections/search/', views.search, name='search'),
    path('election/<int:pk>/', ElectionDetail.as_view(), name='election-detail'),
    path('election/<int:pk>/vote', views.vote, name='vote'),
    path('election/<int:pk>/signup', views.signup_for_election, name='voter-create'),
    path('election/<int:pk>/result', ElectionResult.as_view(), name='election-result'),
    path('election/<int:pk>/result/pdf', views.generate_pdf, name='generate-pdf'),
    path('election/<int:pk>/update', ElectionUpdate.as_view(), name='election-update'),
    path('election/<int:pk>/delete', ElectionDelete.as_view(), name='election-delete'),
    path('election/create', ElectionCreate.as_view(), name='election-create'),
    path('candidate/<int:pk>', CandidateDetail.as_view(), name='candidate-detail'),
    path('candidate/<int:pk>/update', CandidateUpdate.as_view(), name='candidate-update'),
    path('candidate/<int:pk>/delete', CandidateDelete.as_view(), name='candidate-delete'),
    path('candidate/add', CandidateCreate.as_view(), name='candidate-create'),
    path('contact/', Contact.as_view(), name='contact'),
    path('about_us/', views.about_us_view, name='about_us_view'),
    path('profile/', views.profile_view, name="profile"),
]
