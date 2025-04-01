from django.shortcuts import render
from django.urls import path
from . import views

urlpatterns = [
    path('helpdesk/', views.help_view, name='helpdesk'),
    path('contact/', views.contact, name='contact'),
    path('homepage/', views.homepage, name='homepage'),
    path('dashboard/', views.student_dashboard, name='dashboard'),

    path("student_application/", views.student_application, name="student_application"),

    path("success/", lambda request: render(request, "application_success.html"), name="application_success"),

    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),

    ]
