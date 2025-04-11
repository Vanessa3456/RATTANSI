from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import StudentApplicationForm
from .models import Notification, StudentApplication, feebalance
from admins.models import ApplicationSettings


def help_view(request):
    return render(request, 'helpdesk.html')


def contact(request):
    return render(request, 'contact.html')


def student_dashboard(request):
    settings = ApplicationSettings.objects.first()
    application = StudentApplication.objects.filter(student=request.user).first()

    context = {
        "settings": settings,
        "application": application,
    }
    return render(request, "dashboard.html", context)


@login_required
def homepage(request):
    return render(request, 'dashboard.html')


@login_required
def student_application(request):
    settings = ApplicationSettings.objects.last()

    if not settings or not settings.is_open:
        return render(request, 'application_closed.html')

    if settings.deadline and now().date() > settings.deadline:
        return render(request, 'application_closed.html', {'message': "The application deadline has passed."})

    existing_application = StudentApplication.objects.filter(
        student=request.user,
        academic_year=settings.academic_year
    ).first()

    if existing_application:
        messages.info(request, "You have already submitted an application for this academic year")
        return redirect('dashboard')

    if request.method == "POST":
        form = StudentApplicationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            tuition_fee_paid = form.cleaned_data.get('tuition_fee_paid')
            if tuition_fee_paid == 'no':
                reg_no = form.cleaned_data['reg_no']
                fee_balance = form.cleaned_data.get('fee_balance')

                try:
                    record = feebalance.objects.get(reg_no=reg_no)
                    if record.balance != fee_balance:
                        messages.error(request, "The fees balance provided is incorrect. Please contact finance officer.")
                        return render(request, 'student_application.html', {'form': form})

                    if fee_balance < 10000:
                        messages.error(request, "You are not eligible to apply for the bursary")
                        return render(request, 'dashboard.html', {'record': record})
                except feebalance.DoesNotExist:
                    messages.error(request, "No fees balance record(s) found for your registration number.")
                    return render(request, "student_application.html", {"form": form})

            application = form.save(commit=False)
            application.academic_year = settings.academic_year
            application.status = "Pending"
            application.save()

            Notification.objects.create(
                student=request.user,
                message=f"Your bursary application for {settings.academic_year} has been submitted successfully."
            )

            messages.success(request, "Application submitted successfully!")
            return redirect("application_success")
    else:
        form = StudentApplicationForm(user=request.user)  # user passed here too

    return render(request, "student_application.html", {
        "form": form,
        "settings": settings,
    })


@login_required
def notifications(request):
    notifications = Notification.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, student=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')


@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, student=request.user)
    notification.delete()
    return redirect('notifications')
