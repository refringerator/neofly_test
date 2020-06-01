from django.forms import ModelForm
from django.contrib.auth import get_user_model


class RegisterForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['last_name', 'first_name', 'phone_number', 'email']

