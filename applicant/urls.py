from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    applicant_login,
    user_logout,
    register,
    admin_login,
    forgot_password,
    activate_account
)

urlpatterns = [

    path('', applicant_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),

    # Admin Authentication

    path('admin-login/', admin_login, name='admin_login'),

    # Password Reset Flow
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # Forgot Password (Custom View)
    path('forgot-password/', forgot_password, name='forgot_password'),

    # Email Verification
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
]
