# fund_allocation.py in admins app
from django.db.models import Sum
from students.models import StudentApplication


def allocate_funds(total_fund_amount):
    """Distribute bursary funds based on parental status and financial need."""

    if StudentApplication.objects.filter(status='Pending').exists():
        return "Cannot allocate funds until all applications are reviewed."

    # Categorize applications
    orphans = StudentApplication.objects.filter(status='Approved', parental_status='Orphan')
    single_parent = StudentApplication.objects.filter(status='Approved', parental_status='Single ')
    both_parents = StudentApplication.objects.filter(status='Approved', parental_status='Both ')

    # Define allocation percentages
    orphan_share = 0.5  # 50% of the total funds go to orphans
    single_parent_share = 0.3  # 30% goes to single-parent students
    both_parents_share = 0.2  # 20% for students with both parents

    # Distribute funds
    orphan_amount = (total_fund_amount * orphan_share) / max(1, orphans.count())
    single_parent_amount = (total_fund_amount * single_parent_share) / max(1, single_parent.count())
    both_parents_amount = (total_fund_amount * both_parents_share) / max(1, both_parents.count())

    # Assign funds
    for app in orphans:
        app.approved_amount = orphan_amount
        app.save()

    for app in single_parent:
        app.approved_amount = single_parent_amount
        app.save()

    for app in both_parents:
        app.approved_amount = both_parents_amount
        app.save()

    return "Funds allocated based on parental status."
