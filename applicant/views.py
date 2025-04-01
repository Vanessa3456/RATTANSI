from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives

import re

from .forms import RegistrationForm

User = get_user_model()

# Registration number validator
def validate_reg_number_format(reg_number):
    pattern = r'^[A-Z]{3}/[A-Z]/01-\d{5}/\d{4}$'
    return bool(re.match(pattern, reg_number))



#  Applicant Login (With Reg Number Validation)
def applicant_login(request):
    if request.method == 'POST':
        reg_number = request.POST.get('reg_number', '').strip()
        password = request.POST.get('password', '').strip()

        if not reg_number or not password:
            messages.error(request, "Registration number and password are required.")
            return render(request, 'login.html')

        # Authenticate user using registration number
        user = authenticate(request, username=reg_number, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('homepage')  #  Redirect to homepage.html
            else:
                messages.error(request, "Your account is not verified. Check your email.")
        else:
            messages.error(request, "Invalid registration number or password.")

    return render(request, 'login.html')

#  User Logout
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')


# Forgot Password (Supports Both Applicants & Staff)
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
            )

            print(f"🔗 Reset URL: {reset_url}")  # Debugging

            mail_subject = "Secure Password Reset Request"
            text_content = f"Hi {user.full_name},\n\nYou requested a password reset. Click the link below to reset your password:\n\n{reset_url}\n\nIf you did not request this, please ignore this email.\n\nThanks,\nYour Support Team"
            html_content = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url
            })

            try:
                email_message = EmailMultiAlternatives(
                    subject=mail_subject,
                    body=text_content,
                    from_email="josephmanga504@gmail.com",
                    to=[email],
                    #reply_to=["support@yourdomain.com"]
                )
                email_message.attach_alternative(html_content, "text/html")
                email_message.send(fail_silently=False)

                messages.success(request, "Password reset link sent to your email.")
            except Exception as e:
                messages.error(request, f"Failed to send email: {e}")

            return redirect('password_reset_done')

        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")

    return render(request, 'forgot_password.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Account will be activated after email confirmation
            user.is_applicant = True  # Mark as applicant
            user.save()

            # Generate email activation details
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"{request.scheme}://{current_site.domain}/activate/{uid}/{token}/"

            mail_subject = "Activate Your Account"
            message = render_to_string('email_verification.html', {
                'user': user,
                'activation_link': activation_link
            })

            try:
                email_message = EmailMessage(mail_subject, message, to=[user.email])
                email_message.content_subtype = "html"
                email_message.send(fail_silently=False)
                messages.success(request, "Check your email to verify your account.")
            except Exception as e:
                messages.error(request, f"Email sending failed: {e}")

            return redirect('login')
        else:
            print("Form Errors:", form.errors)  # Debugging: Print form errors

    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


#  User Registration (With Email Activation)
def registers(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Account will be activated after email confirmation
            user.is_applicant = True  # Mark as applicant
            user.save()
        else:
            print(form.errors)  # Debugging: Print form errors

        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"{request.scheme}://{current_site.domain}/activate/{uid}/{token}/"

        mail_subject = "Activate Your Account"
        message = render_to_string('email_verification.html', {
            'user': user,
            'activation_link': activation_link
        })

        try:
            email_message = EmailMessage(mail_subject, message, to=[user.email])
            email_message.content_subtype = "html"
            email_message.send(fail_silently=False)
            messages.success(request, "Check your email to verify your account.")
        except Exception as e:
            messages.error(request, f"Email sending failed: {e}")

        return redirect('login')

    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

#  Email Verification View
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account verified! You can now log in.")
        return redirect('login')

    messages.error(request, "Invalid or expired activation link.")
    return redirect('register')


#  Admin Login View
def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, "Admin login successful!")
            return redirect('admin_homepage')
        else:
            messages.error(request, "Invalid admin credentials.")

    return render(request, 'admin_login.html')


# Custom Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'forgot_password.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'

    def form_valid(self, form):
        uidb64 = self.kwargs.get('uidb64')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            messages.error(self.request, "Password reset failed. Please try again.")
            return redirect('forgot_password')

        if user:
            new_password = form.cleaned_data["new_password1"]
            user.set_password(new_password)
            user.save()

            if user.is_staff or user.is_superuser:
                messages.success(self.request, "Admin password updated successfully! Please log in.")
                return redirect(reverse('admin_login'))
            else:
                messages.success(self.request, "Password updated successfully! Please log in.")
                return redirect(reverse('login'))

        messages.error(self.request, "Invalid password reset request.")
        return redirect('forgot_password')