
from django.contrib import messages
from students.models import StudentApplication
from .fund_allocation import allocate_funds
from django.contrib import admin
from .models import ApplicationSettings, FundAllocationSettings


@admin.register(ApplicationSettings)
class ApplicationSettingsAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'is_open', 'deadline')
    list_editable = ('is_open', 'deadline')

@admin.register(FundAllocationSettings)
class FundAllocationSettingsAdmin(admin.ModelAdmin):
    list_display = ('year', 'total_funds')




@admin.register(StudentApplication)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'status', 'university_siblings', 'secondary_siblings', 'approved_amount')
    actions = ['allocate_funds_action']

    def allocate_funds_action(self, request, queryset):
        # Get the latest available fund settings
        fund_settings = FundAllocationSettings.objects.order_by('-year').first()

        if not fund_settings:
            self.message_user(request, "No bursary fund settings found! Set the total funds first.", messages.ERROR)
            return

        total_fund_amount = fund_settings.total_funds  # Dynamic fund amount
        approved_applications = queryset.filter(status="Approved")
        num_applicants = approved_applications.count()

        if num_applicants == 0:
            self.message_user(request, "No approved applications found!", messages.WARNING)
            return

        # Get total need score based on income and dependents
        total_need_score = 0
        need_scores = {}

        for app in approved_applications:
            need_score = self.calculate_need_score(app.university_siblings, app.secondary_siblings)
            need_scores[app.id] = need_score
            total_need_score += need_score

        # Allocate funds based on need score
        for app in approved_applications:
            if total_need_score > 0:
                app.approved_amount = (need_scores[app.id] / total_need_score) * total_fund_amount
            else:
                app.approved_amount = 0  # Prevent division by zero
            app.save()

        self.message_user(request, "Funds allocated successfully!", messages.SUCCESS)

    allocate_funds_action.short_description = "Allocate Bursary Funds (Only Approved Applications)"

    def calculate_need_score(self, university_siblings, secondary_siblings):
        """
        Simple need-based score:
        - Lower income → Higher score
        - More dependents → Higher score
        """
        income_factor = max(1, 50000 / (university_siblings + 1))  # Prevent division by zero
        dependents_factor = max(1, secondary_siblings)  # More dependents = higher need
        return income_factor * dependents_factor  # Combined need score

