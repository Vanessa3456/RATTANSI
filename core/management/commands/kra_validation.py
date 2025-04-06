import csv
from django.core.management.base import BaseCommand
from students.models import ParentalIncomeRecord  # Adjust based on where your model is

class Command(BaseCommand):
    help = "Import income data from CSV"

    def handle(self, *args, **kwargs):
        with open('students/kra_validation.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ParentalIncomeRecord.objects.update_or_create(
                    reg_no=row['reg_no'],
                    defaults={
                        'father_kra_pin': row['father_kra_pin'],
                        'mother_kra_pin': row['mother_kra_pin'],
                        'father_salary': row['father_salary'],
                        'mother_salary': row['mother_salary'],
                    }
                )
        self.stdout.write(self.style.SUCCESS("Income data imported successfully."))
