from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ApplicationSettings

from students.models import Notification  # Assuming you have a notifications model

@receiver(post_save, sender=ApplicationSettings)
def notify_students_application_status(sender, instance, **kwargs):
    Student = apps.get_model('students', 'Student')
    message = ""
    if instance.is_open:
        message = f"Bursary applications are now OPEN for {instance.academic_year}. Apply before {instance.deadline}!"
    else:
        message = "Bursary applications are now CLOSED."

    # Send notification to all students
    students = Student.objects.all()
    for student in students:
        Notification.objects.create(user=student.user, message=message)
