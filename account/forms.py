from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import PasswordInput


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'E-mail'}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(attrs={'placeholder': 'Password'})
        self.fields['password2'].widget = PasswordInput(attrs={'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
