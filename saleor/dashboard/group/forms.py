from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import pgettext_lazy

from ...core.permissions import get_permissions


class GroupPermissionsForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': pgettext_lazy('Group name', 'Name'),
            'permissions': pgettext_lazy('Group permission', 'Permission')}

    permissions = forms.ModelMultipleChoiceField(
        queryset=get_permissions(),
        widget=forms.CheckboxSelectMultiple
    )
