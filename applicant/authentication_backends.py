from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAuthBackend(ModelBackend):
    """ Custom authentication backend to support both reg_number and email login """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            if '@' in username:  #  Staff/Admin login via email
                user = User.objects.get(email=username)
            else:  #  Applicants login via reg_number
                user = User.objects.get(reg_number=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
