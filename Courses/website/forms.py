from django import forms
from . import models
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, date
from django.contrib.auth import get_user_model


def get_year():
    return datetime.now().year


class UserForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'is_instructor',
                  'phone', 'is_male', 'birthdate', 'country', 'pic')
        widgets = {'birthdate': forms.SelectDateWidget(
            years=[i for i in range(1990, get_year()-6)])}


class SearchForm(forms.Form):
    name = forms.CharField(max_length=255, label=_('Name'))
