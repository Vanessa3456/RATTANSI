from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class StudentApplication(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]

    STUDENT_STATUS_CHOICES = [
        ('KUCCPS', 'Government Sponsored (KUCCPS)'),
        ('PSSP', 'Self Sponsored (PSSP)')
    ]
    RESIDENTIAL_STATUS_CHOICES = [
        ('Resident', 'Resident'),
        ('Non Resident', 'Non Resident')
    ]

    COUNTY_CHOICES = [
        ('Baringo', 'Baringo'),
        ('Bomet', 'Bomet'),
        ('Bungoma', 'Bungoma'),
        ('Busia', 'Busia'),
        ('Elgeyo Marakwet', 'Elgeyo Marakwet'),
        ('Embu', 'Embu'),
        ('Garissa', 'Garissa'),
        ('Homa Bay', 'Homa Bay'),
        ('Isiolo', 'Isiolo'),
        ('Kajiado', 'Kajiado'),
        ('Kakamega', 'Kakamega'),
        ('Kericho', 'Kericho'),
        ('Kiambu', 'Kiambu'),
        ('Kilifi', 'Kilifi'),
        ('Kirinyaga', 'Kirinyaga'),
        ('Kisii', 'Kisii'),
        ('Kisumu', 'Kisumu'),
        ('Kitui', 'Kitui'),
        ('Kwale', 'Kwale'),
        ('Laikipia', 'Laikipia'),
        ('Lamu', 'Lamu'),
        ('Machakos', 'Machakos'),
        ('Makueni', 'Makueni'),
        ('Mandera', 'Mandera'),
        ('Marsabit', 'Marsabit'),
        ('Meru', 'Meru'),
        ('Migori', 'Migori'),
        ('Mombasa', 'Mombasa'),
        ('Murang\'a', 'Murang\'a'),
        ('Nairobi', 'Nairobi'),
        ('Nakuru', 'Nakuru'),
        ('Nandi', 'Nandi'),
        ('Narok', 'Narok'),
        ('Nyamira', 'Nyamira'),
        ('Nyandarua', 'Nyandarua'),
        ('Nyeri', 'Nyeri'),
        ('Samburu', 'Samburu'),
        ('Siaya', 'Siaya'),
        ('Taita Taveta', 'Taita Taveta'),
        ('Tana River', 'Tana River'),
        ('Tharaka Nithi', 'Tharaka Nithi'),
        ('Trans Nzoia', 'Trans Nzoia'),
        ('Turkana', 'Turkana'),
        ('Uasin Gishu', 'Uasin Gishu'),
        ('Vihiga', 'Vihiga'),
        ('Wajir', 'Wajir'),
        ('West Pokot', 'West Pokot'),
    ]

    SCHOOL_CHOICES=[
        ('SCI', 'SCI'),
        ('SEDU', 'SEDU'),
        ('SDHMA', 'SDHMA'),
        ('SOM', 'SOM'),
        ('SEBE', 'SEBE'),
        ('SASS', 'SASS'),
        ('SONAS', 'SONAS'),
        ('SONMAPS', 'SONMAPS'),
        ('SPB&T', 'SPB&T'),
        ('SOBE', 'SOBE'),
        ('SAVET', 'SAVET'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    parental_status = models.CharField(max_length=10, choices=[
        ("both", "Have both parents"),
        ("one", "Have one parent"),
        ("orphan", "Total orphan"),
    ])

    EMPLOYER_CHOICES=[
        ('Employed', 'Employed'),
        ('Not employed','Not employed')
    ]

    # Personal Details
    name = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=50, unique=True)
    school = models.CharField(max_length=100,choices=SCHOOL_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    home_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    county = models.CharField(max_length=20, choices=COUNTY_CHOICES)
    next_of_kin = models.CharField(max_length=100)
    next_of_kin_address = models.CharField(max_length=255)
    next_of_kin_phone = models.CharField(max_length=15)
    chief_name = models.CharField(max_length=100)
    chief_address = models.CharField(max_length=255)
    chief_phone = models.CharField(max_length=15)
    disability = models.BooleanField(default=False)
    disability_details = models.CharField(max_length=255, blank=True, null=True)
    student_status = models.CharField(max_length=10, choices=STUDENT_STATUS_CHOICES)
    residential_status = models.CharField(max_length=15, choices=RESIDENTIAL_STATUS_CHOICES)

    # Family Background


    death_certificate = models.FileField(upload_to="documents/", null=True, blank=True)

    # Father's Details
    father_age = models.IntegerField(null=True, blank=True)
    father_occupation = models.CharField(max_length=100, null=True, blank=True)
    father_employer = models.CharField(max_length=100, choices=EMPLOYER_CHOICES)
    father_health_status = models.FileField(upload_to="documents/", null=True, blank=True)

    # Mother's Details
    mother_age = models.IntegerField(null=True, blank=True)
    mother_occupation = models.CharField(max_length=100, null=True, blank=True)
    mother_employer = models.CharField(max_length=100, choices=EMPLOYER_CHOICES)
    mother_health_status = models.FileField(upload_to="documents/", null=True, blank=True)

    # Sibling Details
    total_siblings = models.IntegerField()
    university_siblings = models.IntegerField(null=True, blank=True)
    secondary_siblings = models.IntegerField(null=True, blank=True)
    out_of_school_siblings = models.IntegerField(null=True, blank=True)
    out_of_school_reason = models.TextField(null=True, blank=True)
    working_siblings_occupation = models.TextField(null=True, blank=True)

    # Other Information Fields
    SCHOO_FEES_CHOICES=[
        ('Parent','Parent'),
        ('External Sponsor','External Sponsor')
    ]
    school_fee_payer = models.CharField(max_length=255, choices=SCHOO_FEES_CHOICES)
    school_fee_evidence = models.FileField(upload_to="documents/", null=True, blank=True)

    work_study = models.CharField(max_length=3, choices=[("yes", "Yes"), ("no", "No")])
    work_study_evidence = models.FileField(upload_to="documents/", null=True, blank=True)

    external_support = models.CharField(max_length=3, choices=[("yes", "Yes"), ("no", "No")])
    sponsor_source = models.CharField(
        max_length=50, choices=[
            ("HELB", "HELB"),
            ("NGO", "NGO"),
            ("CDF", "CDF"),
            ("Other", "Other")], null=True,
        blank=True
    )
    sponsor_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    tuition_fee_paid = models.CharField(max_length=3, choices=[("yes", "Yes"), ("no", "No")])
    fee_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,default=0.0)
    fee_statement = models.FileField(upload_to="documents/", null=True, blank=True)

    deferred_study = models.CharField(max_length=3, choices=[("yes", "Yes"), ("no", "No")])
    defer_reason = models.CharField(
        max_length=50,
        choices=[("Medical", "Medical"),
                 ("Social", "Social"),
                 ("Financial", "Financial"),
                 ("Academic", "Academic")],
        null=True, blank=True
    )

    additional_info = models.TextField(null=True, blank=True)
    additional_info_evidence = models.FileField(upload_to="documents/", null=True, blank=True)

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    academic_year = models.CharField(max_length=9,default='2024/2025')  # Store the academic year
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)  # Timestamp of submission
    reviewed_at = models.DateTimeField(null=True, blank=True)  # Timestamp when reviewed
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'academic_year')  # Ensure one application per student per year

    def __str__(self):
        return f"{self.reg_no} - {self.academic_year} - {self.status}"

class feebalance(models.Model):
    reg_no = models.CharField(max_length=20, unique=True)
    total_fees=models.DecimalField(max_digits=10,decimal_places=2)
    amount_paid=models.DecimalField(max_digits=10,decimal_places=2)
    balance=models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.student.name}'s Fee record"

class Notification(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()  # Notification message
    is_read = models.BooleanField(default=False)  # Track if the notification is read
    created_at = models.DateTimeField(default=timezone.now)  # Time of creation

    def __str__(self):
        return f"Notification for {self.student.name} - {'Read' if self.is_read else 'Unread'}"
