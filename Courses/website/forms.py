from django import forms
from . import models

# Your Forms


class UserForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class ProfileForm(forms.ModelForm):

    class Meta:
        model = models.Profile
        fields = ('about', 'phone', 'is_male', 'birthdate', 'country', 'city',
                  'state')
