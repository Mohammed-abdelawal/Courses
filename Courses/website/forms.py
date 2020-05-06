from django import forms
from . import models
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, date

y = datetime.now().year


# Forms


class UserForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class ProfileForm(forms.ModelForm):

    class Meta:
        model = models.Profile
        fields = ('about', 'phone', 'is_male', 'birthdate', 'country', 'city',
                  'state')
        widgets = {'birthdate': forms.SelectDateWidget(
                                      years=[i for i in range(2000, y-7)])}


class SearchForm(forms.Form):

    name = forms.CharField(max_length=120, label=_('Name'), required=False)
    pub_date = forms.DateField(required=False, label=_('Pub Date'),
                               widget=forms.SelectDateWidget(
                                      years=[i for i in range(2000, y+1)]),
                               initial=date(2015, 1, 1))
