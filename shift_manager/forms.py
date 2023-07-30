from django import forms
from .models import Department, Employee
from django.contrib.auth.forms import AuthenticationForm


class ShiftForm(forms.ModelForm):
    class Meta:
        # model = Shift
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
#
#
# class AvailabilityForm(forms.ModelForm):
#     class Meta:
#         model = Shift_time
#         fields = ('date', 'start_time', 'end_time')
#         widgets = {
#             'start_time': forms.TimeInput(attrs={'type': 'time'}),
#             'end_time': forms.TimeInput(attrs={'type': 'time'}),
#         }
#
#     shift_type = forms.ChoiceField(choices=Shift_time.SHIFT_CHOICES, widget=forms.RadioSelect)
#     available = forms.BooleanField(required=False)


class EmployeeForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    image = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model = Employee
        fields = ('first_name', 'last_name', 'other_name', 'department', 'email', 'image')


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput,
    )

