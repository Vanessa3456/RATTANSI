from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from students.models import StudentApplication, Notification
from .models import ApplicationSettings,FundAllocationSettings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os




def admin_homepage(request):
    return render(request,'admin_homepage.html')
def review_applications(request):
    # Fetch all applications with status 'Pending'
    pending_apps = StudentApplication.objects.filter(status='Pending').order_by('-submitted_at')

    return render(request, 'review_applications.html', {'pending_apps': pending_apps})

def review_application_details(request, app_id):
    application = get_object_or_404(StudentApplication, id=app_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            application.status = 'Approved'
            Notification.objects.create(student=application.student, message="Your application has been approved!")
            messages.success(request, "Application approved successfully.")
        elif action == 'reject':
            application.status = 'Rejected'
            Notification.objects.create(student=application.student, message="Your application was rejected.")
            messages.warning(request, "Application rejected.")

        application.save()
        return redirect('review_applications')  # Redirect back to pending applications

    return render(request, 'review_details.html', {'application': application})


def approved_applications(request):
    approved_apps = StudentApplication.objects.filter(status="Approved")

    # Get search query
    search_query = request.GET.get('q', '')
    if search_query:
        approved_apps = approved_apps.filter(student__username__icontains=search_query)

    # Get sorting parameter
    sort_by = request.GET.get('sort_by')
    if sort_by == "student__username_asc":
        approved_apps = approved_apps.order_by("student__username")
    elif sort_by == "student__username_desc":
        approved_apps = approved_apps.order_by("-student__username")
    elif sort_by == "submitted_at_asc":
        approved_apps = approved_apps.order_by("submitted_at")
    elif sort_by == "submitted_at_desc":
        approved_apps = approved_apps.order_by("-submitted_at")

    return render(request, 'approved_applications.html', {'approved_apps': approved_apps})

def rejected_applications(request):
    query = request.GET.get('search', '')  # Get search query from URL
    rejected_apps = StudentApplication.objects.filter(status="Rejected")

    if query:
        rejected_apps = rejected_apps.filter(student__username__icontains=query)  # Case-insensitive search

    return render(request, 'rejected_applications.html', {'rejected_apps': rejected_apps, 'search_query': query})


def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin Staff").exists()


@user_passes_test(is_admin)
def admin_dashboard(request):
    settings = ApplicationSettings.objects.last()
    return render(request, 'admin_dashboard.html', {'settings': settings})

def allocate_funds(request):
    current_year = now().year

    # Get total available funds for the year
    try:
        fund_settings = FundAllocationSettings.objects.get(year=current_year)
        available_funds = fund_settings.total_funds
    except FundAllocationSettings.DoesNotExist:
        messages.error(request, "No fund allocation settings found for the current year.")
        return render(request, 'fund_allocation.html')

    approved_apps = StudentApplication.objects.filter(status="Approved").order_by("submitted_at")

    # Ensure all applications are reviewed before proceeding
    if StudentApplication.objects.filter(status="Pending").exists():
        messages.error(request, "Fund allocation cannot proceed. All applications must be reviewed first.")
        return redirect("allocate_funds")

    total_allocated = 0  # Track total allocated funds

    with transaction.atomic():  # Ensures all changes are committed
        for app in approved_apps:
            if available_funds <= 0:
                break  # Stop allocating if funds are exhausted

            if app.approved_amount and app.approved_amount > 0:
                continue

            allocated_amount = 0  # Default allocation

            parental_status = app.parental_status or ""  # Ensure it's not None
            fee_balance = app.fee_balance or 0  # Default 0 if None
            work_study = app.work_study or "no"  # Default to "No"
            death_certificate = app.death_certificate or False  # Default False
            father_employer = app.father_employer or "Unknown"
            mother_employer = app.mother_employer or "Unknown"
            university_siblings = app.university_siblings or 0
            secondary_siblings = app.secondary_siblings or 0
            total_siblings = university_siblings + secondary_siblings


            # If both parents are alive
            if parental_status.lower() == "both":
                if (
                    father_employer == "Employed" and
                    mother_employer == "Employed" and
                    app.father_health_status and
                    app.mother_health_status and
                    total_siblings > 4 and
                    work_study == "yes" and
                    fee_balance == 0
                ):
                    allocated_amount = 2000
                elif father_employer == "Not Employed" or mother_employer == "Not Employed":
                    allocated_amount = 4000
                elif work_study == "no" and fee_balance > 0:
                    allocated_amount = 6000

            # If one parent is alive
            elif parental_status.lower() == "one":
                if (
                    (father_employer == "Employed" or mother_employer == "Employed") and
                    (app.father_health_status or app.mother_health_status) and
                    total_siblings > 4 and
                    work_study == "yes" and
                    fee_balance == 0
                ):
                    allocated_amount = 3000
                elif father_employer == "Not employed" or mother_employer == "Not employed":
                    allocated_amount = 6000
                elif work_study == "no" and fee_balance > 0:
                    allocated_amount = 8000

            #  If both parents are deceased
            elif parental_status.lower() == "orphan":
                if death_certificate and total_siblings > 4 and fee_balance > 0:
                    allocated_amount = 15000
                elif not death_certificate:
                    allocated_amount = 3000
                elif work_study == "yes" and fee_balance == 0:
                    allocated_amount = 8000

            # Ensure we do not allocate more than available funds
            allocated_amount = max(min(allocated_amount, available_funds), 1000)



            app.approved_amount = allocated_amount
            app.save()

            Notification.objects.create(
                student=app.student,
                message=f"You have been allocated KES {allocated_amount:,} in bursary funds."
            )

            total_allocated += allocated_amount
            available_funds -= total_allocated


        fund_settings.total_funds = available_funds
        fund_settings.save()

        messages.success(request, f"Funds allocated successfully. Remaining funds: KES {available_funds}.")
        return render(request, 'fund_allocation.html', {
            'approved_apps': approved_apps,
            'remaining_funds': available_funds,
            'total_allocated': total_allocated,
        })


def export_fund_allocation_pdf(request):
    """Generates a PDF report of allocated bursary funds."""

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fund_allocation_report.pdf"'

    width, height = A4
    pdf = canvas.Canvas(response, pagesize=A4)
    logo_path = os.path.join(os.path.dirname(__file__), "static", "images", "logo.jpg")
    if os.path.exists(logo_path):
        pdf.drawImage(ImageReader(logo_path), width / 2 - 40, height - 100, width=80, height=80)  # Centered

    # **2. Add Title (Closer to Logo)**
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 120, "MASINDE MULIRO UNIVERSITY OF SCIENCE AND TECHNOLOGY")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(width / 2, height - 140, "FUND ALLOCATION REPORT")
    # Fetch approved applications
    applications = StudentApplication.objects.filter(status="Approved").order_by("submitted_at")

    # Table Data
    data = [["Student Name", "Reg No", "Parental Status", "Allocated Amount"]]
    total_allocated = 0

    for app in applications:
        data.append([
            app.name,
            app.reg_no,
            app.parental_status,
            f"KES {app.approved_amount:,}"
        ])
        total_allocated += app.approved_amount

    # Add total allocated funds row
    data.append(["", "", "Total Allocated:", f"KES {total_allocated:,}"])

    # Create table
    table = Table(data, colWidths=[150, 100, 120, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Position table on PDF
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 50, height - 550)

    # Save PDF
    pdf.save()

    return response


