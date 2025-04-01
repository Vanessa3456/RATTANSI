from django.contrib import messages
from django.utils.timezone import now

from .forms import StudentApplicationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Notification
from admins.models import ApplicationSettings


def help_view(request):
    return render(request, 'helpdesk.html')

def contact(request):
    return render(request, 'contact.html')

def student_dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def homepage(request):
    return render(request, 'homepage.html')


def student_application(request):
    settings = ApplicationSettings.objects.last()  # Get the latest settings

    # Check if applications are open
    if not settings or not settings.is_open:
        return render(request, 'application_closed.html')  # Show "Applications are Closed" page

    # Check if the deadline has passed
    if settings.deadline and now().date() > settings.deadline:
        return render(request, 'application_closed.html', {'message': "The application deadline has passed."})

    if request.method == "POST":
        form = StudentApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.academic_year = settings.academic_year  # Use current academic year
            application.student = request.user
            application.status = "Pending"
            application.save()

            messages.success(request, "Application submitted successfully!")
            return redirect("application_success")  # Redirect to success page
        else:
            messages.error(request, "There were errors in your form. Please check and submit again.")
    else:
        form = StudentApplicationForm()

    return render(request, "student_application.html", {"form": form})


def notifications(request):
    """ Display all notifications for the logged-in student """
    notifications = Notification.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})


def mark_as_read(request, notification_id):
    """ Mark a notification as read """
    notification = get_object_or_404(Notification, id=notification_id, student=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')


def delete_notification(request, notification_id):
    """ Delete a notification """
    notification = get_object_or_404(Notification, id=notification_id, student=request.user)
    notification.delete()
    return redirect('notifications')