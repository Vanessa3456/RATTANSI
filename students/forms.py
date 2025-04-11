from django import forms
from django.core.exceptions import ValidationError

from .models import StudentApplication, feebalance


class StudentApplicationForm(forms.ModelForm):
    PARENTAL_STATUS_CHOICES = [
        ("both", "Have both parents"),
        ("one", "Have one parent"),
        ("orphan", "Total orphan"),
    ]

    # Existing Fields
    school = forms.ChoiceField(choices=StudentApplication.SCHOOL_CHOICES, required=True)
    county = forms.ChoiceField(choices=StudentApplication.COUNTY_CHOICES, required=True)
    parental_status = forms.ChoiceField(
        choices=PARENTAL_STATUS_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    death_certificate = forms.FileField(required=False)

    father_age = forms.IntegerField(widget=forms.NumberInput(attrs={"min": 0}), required=False)
    father_occupation = forms.CharField(max_length=100, required=False)
    father_employer = forms.ChoiceField(choices=StudentApplication.EMPLOYER_CHOICES, required=False)
    father_health_status = forms.FileField(required=False)

    mother_age = forms.IntegerField(widget=forms.NumberInput(attrs={"min": 0}), required=False)
    mother_occupation = forms.CharField(max_length=100, required=False)
    mother_employer = forms.ChoiceField(choices=StudentApplication.EMPLOYER_CHOICES, required=False)
    mother_health_status = forms.FileField(required=False)

    total_siblings = forms.IntegerField(widget=forms.NumberInput(attrs={"min": 0}), required=True)
    university_siblings = forms.IntegerField(widget=forms.NumberInput(attrs={"min": 0}), required=False)
    secondary_siblings = forms.IntegerField(widget=forms.NumberInput(attrs={"min": 0}), required=False)
    out_of_school_siblings = forms.IntegerField(widget=forms.NumberInput(attrs={"min": 0}), required=False)
    out_of_school_reason = forms.CharField(max_length=255, required=False)
    working_siblings_occupation = forms.CharField(max_length=255, required=False)



    YES_NO_CHOICES = [("yes", "Yes"), ("no", "No")]
    SPONSOR_CHOICES = [("HELB", "HELB"), ("NGO", "NGO"), ("CDF", "CDF"), ("Other", "Other")]
    DEFER_REASON_CHOICES = [("Medical", "Medical"), ("Social", "Social"), ("Financial", "Financial"),
                            ("Academic", "Academic")]


    school_fee_payer = forms.ChoiceField(choices=StudentApplication.SCHOO_FEES_CHOICES, required=False)
    school_fee_evidence = forms.FileField(required= False)

    work_study = forms.ChoiceField(choices=YES_NO_CHOICES, widget= forms.RadioSelect)
    work_study_evidence = forms.FileField(required=False)

    external_support = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect)
    sponsor_source = forms.ChoiceField(choices=SPONSOR_CHOICES, required=False, widget=forms.Select)
    sponsor_amount = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"min": 0}))

    tuition_fee_paid = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect)
    fee_balance = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"min": 0}))




    fee_statement = forms.FileField(required=False)

    deferred_study = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect)
    defer_reason = forms.ChoiceField(choices=DEFER_REASON_CHOICES, required=False, widget=forms.Select)

    additional_info = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Enter any other relevant information"}), required=False)
    additional_info_evidence = forms.FileField(required=False)

    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user', None)
    #     super().__init__(*args, **kwargs)

    #     if self.user:
    #         self.fields['reg_no'].initial=self.user.reg_number
    #         self.fields['reg_no'].disabled = True
    #
    #     if self.user:
    #         self.fields['name'].initial = self.user.full_name
    #         self.fields['name'].disabled = True
    #
    # def save(self, commit = True):
    #     instance=super().save(commit=False)
    #     if self.user:
    #         instance.reg_no = self.user.email
    #     if commit:
    #         instance.save()
    #     return  instance
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Catch the logged-in user passed from the view
        super().__init__(*args, **kwargs)

        if self.user:
            # Assume CustomUser has reg_number and full_name
            self.fields['reg_no'].initial = self.user.reg_number
            self.fields['reg_no'].disabled = True

            self.fields['name'].initial = self.user.full_name
            self.fields['name'].disabled = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.reg_no = self.user.reg_number
            instance.name = self.user.full_name
            instance.student = self.user  # Link to the ForeignKey field
        if commit:
            instance.save()
        return instance

    class Meta:
        model = StudentApplication
        fields = '__all__'
        exclude = ['student', 'status', 'academic_year']
        widgets = {
            "name": forms.TextInput(attrs={"readonly": "readonly"}),
            "reg_no": forms.TextInput(attrs={"readonly": "readonly"}),
            "school": forms.TextInput(attrs={"placeholder": "Enter your school name"}),
            "gender": forms.Select(attrs={"placeholder": "Select your gender"}),
            "home_address": forms.TextInput(attrs={"placeholder": "Enter your home address"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "Enter your phone number"}),
            "next_of_kin": forms.TextInput(attrs={"placeholder": "Enter next of kin's name"}),
            "next_of_kin_address": forms.TextInput(attrs={"placeholder": "Enter next of kin's address"}),
            "next_of_kin_phone": forms.TextInput(attrs={"placeholder": "Enter next of kin's phone"}),
            "chief_name": forms.TextInput(attrs={"placeholder": "Enter chief's name"}),
            "chief_address": forms.TextInput(attrs={"placeholder": "Enter chief's address"}),
            "chief_phone": forms.TextInput(attrs={"placeholder": "Enter chief's phone"}),
            "disability_details": forms.TextInput(attrs={"placeholder": "If yes, specify your disability"}),
        }
