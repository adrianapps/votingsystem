from django import forms


class ContactForm(forms.Form):
    """
    Form for user contact information and message submission.

    This form provides fields for users to input their name, email, and message content
    for contacting the website administrators.

    Attributes
    ----------
    name : forms.CharField
        Field for user's full name, with maximum length and placeholder text.
    email : forms.EmailField
        Field for user's email address, with placeholder text.
    content : forms.CharField
        Field for user's message content, with placeholder text.

    Notes
    -----
    The form does not represent a model, it's a simple form for user input.
    """
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Type your message...'}))

