from django.contrib import messages
from django.utils.timezone import now

from .forms import StudentApplicationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Notification, ParentalIncomeRecord
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

            reg_no = form.cleaned_data['reg_no']
            father_kra_pin = form.cleaned_data.get('father_kra')
            mother_kra_pin = form.cleaned_data.get('mother_kra')
            try:
                record = ParentalIncomeRecord.objects.get(reg_no=reg_no)
                pin_match = False
                high_income = False

                if record.father_kra_pin == father_kra_pin:
                    pin_match = True
                    if record.father_salary and record.father_salary > 100000:
                        high_income = True

                if  record.mother_kra_pin == mother_kra_pin:
                    pin_match = True
                    if record.mother_salary and record.mother_salary > 100000:
                        high_income = True

                if not pin_match:
                    messages.error(request, "The provided KRA PIN(s) do not match our records.")
                    return render(request, "student_application.html", {"form": form})

                if high_income:
                    messages.error(request, "Your parent(s) income exceeds the allowed limit for bursary eligibility.")
                    return render(request, "student_application.html", {"form": form})

            except ParentalIncomeRecord.DoesNotExist:
                messages.error(request, "No KRA record(s) found for your registration number.")
                return render(request, "student_application.html", {"form": form})

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