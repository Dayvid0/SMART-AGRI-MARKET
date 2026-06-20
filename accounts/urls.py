from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('verification/submit/', views.submit_verification, name='submit_verification'),
    path('verification/status/', views.verification_status, name='verification_status'),

    # --- Password Reset Flow ---
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/',
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html',
         ),
         name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password-reset/complete/',
         ),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html',
         ),
         name='password_reset_complete'),
]
