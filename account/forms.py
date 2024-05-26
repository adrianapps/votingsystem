from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import PasswordInput


class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for user registration with additional fields and customized widgets.

    This form extends Django's built-in UserCreationForm to include an email field and customize
    the appearance of the form fields with placeholder text.

    Attributes
    ----------
    email : forms.EmailField
       Email field for user registration, required and with placeholder text.
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'E-mail'}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form instance.

        Customizes the password fields to include placeholder text.

        Parameters
        ----------
        args : tuple
            Positional arguments passed to the form constructor.
        kwargs : dict
            Keyword arguments passed to the form constructor.
        """
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(attrs={'placeholder': 'Password'})
        self.fields['password2'].widget = PasswordInput(attrs={'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        """
        Save the user instance to the database.

        Overrides the save method to set the email field before saving the user instance.

        Parameters
        ----------
        commit : bool, optional
            If True, the user instance is saved to the database. If False, the user instance
            is returned but not saved to the database. Default is True.

        Returns
        -------
        User
            The user instance that was saved to the database.

        Notes
        -----
        This method sets the email field of the user instance to the cleaned email data before
        saving the user. If commit is True, the user instance is saved to the database, otherwise
        it is returned without saving.
        """
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
