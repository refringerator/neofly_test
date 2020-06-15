from django.forms import ModelForm, Form, CharField, EmailField
from django.contrib.auth import get_user_model


class RegisterForm(Form):
    surname = CharField(max_length=30)
    name = CharField(max_length=30)
    email = EmailField(required=False)

