from django.db import models

class ApplicationSettings(models.Model):
    is_open = models.BooleanField(default=False)  # Whether applications are open or closed
    deadline = models.DateField(null=True, blank=True)  # Application deadline
    academic_year = models.CharField(max_length=9,default="2024/2025")  # Example: "2024/2025"

    def __str__(self):
        return f"Academic Year: {self.academic_year} | Open: {self.is_open} | Deadline: {self.deadline}"

class FundAllocationSettings(models.Model):
    year = models.IntegerField(unique=True)
    total_funds = models.FloatField()

    def __str__(self):
        return f"Bursary Fund - {self.year} (Total: {self.total_funds})"