from django.urls import path

from account.views import RegisterView
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login', views.login_user, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name="profile"),
]