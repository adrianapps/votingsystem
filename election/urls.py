from django.urls import path

from .views import ElectionList, ElectionDetail, ElectionResult, CandidateCreate, CandidateDetail, CandidateUpdate, CandidateDelete, Contact
from . import views

app_name = 'election'

urlpatterns = [
    path('', ElectionList.as_view(), name='election-list'),
    path('<int:pk>/', ElectionDetail.as_view(), name='election-detail'),
    path('<int:pk>/vote', views.vote, name='vote'),
    path('<int:pk>/result', ElectionResult.as_view(), name='election-result'),
    path('<int:pk>/result/pdf', views.generate_pdf, name='generate-pdf'),
    path('candidate/<int:pk>', CandidateDetail.as_view(), name='candidate-detail'),
    path('candidate/<int:pk>/update', CandidateUpdate.as_view(), name='candidate-update'),
    path('candidate/<int:pk>/delete', CandidateDelete.as_view(), name='candidate-delete'),
    path('candidate/add', CandidateCreate.as_view(), name='candidate-create'),
    path('contact/', Contact.as_view(), name='contact'),
    path('about_us/', views.about_us_view, name='about_us_view'),
    path('profile/', views.profile_view, name="profile"),
]
