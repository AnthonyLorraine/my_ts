from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from main.models import Timesheet, Penalty, PenaltyType, Employee, Claim, Team


class FloatingValidationModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [field.widget.attrs.update({
            'class': 'form-control',
            'aria-describedby': f'{str(field.label).replace(" ", "").lower()}Feedback',
            'placeholder': f'{str(field.label).capitalize()}'
        }) for field in self.fields.values()]

    def clean(self):
        for field in self.errors:
            self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
        for field in self.cleaned_data:
            self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
        return super().clean()


class TimeSheetModelForm(FloatingValidationModelForm):
    class Meta:
        model = Timesheet
        fields = ['start_date_time', '_duration', 'penalty']
        widgets = {
            'start_date_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local',
                       'max': '2100-01-01T00:00',
                       'min': '2020-01-01T00:00',
                       'placeholder': 'Start Date Time'}),
            '_duration': forms.TextInput(
                attrs={'type': 'number',
                       'placeholder': 'Duration'}),
        }

    def clean__duration(self):
        data = self.cleaned_data['_duration']
        if data > 1440:
            raise ValidationError('Duration over 24 hours. Max 1440 minutes allowed',
                                  code='invalid')
        if data < 1:
            raise ValidationError('Duration must be a positive number.',
                                  code='invalid')
        if data == 0:
            raise ValidationError('Duration must not be zero.',
                                  code='invalid')
        return data


class ClaimForm(FloatingValidationModelForm):
    class Meta:
        model = Claim
        fields = ['employee', 'penalty_type', 'claimed_seconds']
        widgets = {
            'claimed_seconds': forms.TextInput(attrs={'type': 'number', 'placeholder': 'Duration'}),
            'employee': forms.HiddenInput(),
        }

    def clean_claimed_seconds(self):
        claimed_minutes = self.cleaned_data['claimed_seconds']
        employee = self.cleaned_data['employee']
        try:
            penalty_type = self.cleaned_data['penalty_type']
        except KeyError:
            raise ValidationError('Penalty type is required.',
                                  code='invalid')
        available_minutes = penalty_type.calculate_available_employee_time(employee) * 60
        if claimed_minutes > 1440:
            raise ValidationError('Duration over 24 hours. Max 1440 minutes allowed',
                                  code='invalid')
        if claimed_minutes < 1:
            raise ValidationError('Duration must be a positive number.',
                                  code='invalid')
        if claimed_minutes > available_minutes:
            raise ValidationError(f'Penalty type only has {round(available_minutes / 60, 2)} hours available.')
        return claimed_minutes


class PenaltyCreateModelForm(FloatingValidationModelForm):
    class Meta:
        model = Penalty
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'required': True, 'maxlength': 40}),
        }


class PenaltyTypeCreateModelForm(FloatingValidationModelForm):
    class Meta:
        model = PenaltyType
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'required': True, 'maxlength': 40}),
        }


class EmployeeUpdateModelForm(FloatingValidationModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'username': forms.TextInput(attrs={'required': True, 'maxlength': 40}),
        }


class LogInModelForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [field.widget.attrs.update({
            'class': 'form-control',
            'aria-describedby': f'{str(field.label).replace(" ", "").lower()}Feedback',
            'placeholder': f'{str(field.label).capitalize()}'
        }) for field in self.fields.values()]

    def clean(self):
        for field in self.errors:
            self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
        for field in self.cleaned_data:
            self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
        return super().clean()


class RegisterModelForm(FloatingValidationModelForm):
    class Meta:
        model = Employee
        fields = ['username', 'first_name', 'last_name', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'required': True, 'maxlength': 40}),
            'password': forms.PasswordInput(attrs={'required': True})
        }


class TeamCreateModelForm(FloatingValidationModelForm):
    class Meta:
        model = Team
        fields = ['name', ]
        widgets = {
            'name': forms.TextInput(attrs={'required': True, 'maxlength': 40}),
        }