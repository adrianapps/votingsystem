from django.urls import path
from django.contrib.auth import views as auth_views

from account.views import RegisterView
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login', views.login_user, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name="profile"),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='account/password_reset.html'
    ),
         name="password-reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='account/password_reset_done.html'
    ),
         name="password-reset-done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='account/password_reset_confirm.html'
    ),
         name="password-reset-confirm"),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='account/password_reset_complete.html'
    ),
         name="password-reset-complete"),
]
