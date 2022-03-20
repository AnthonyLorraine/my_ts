from django import forms
from django.core.exceptions import ValidationError
from main.models import Timesheet, TimesheetRow, Penalty, PenaltyType, Employee


class TimeSheetModelForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['start_date_time', 'duration', 'penalty']
        widgets = {
            'start_date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'max': '2100-01-01T00:00', 'min': '2020-01-01T00:00', 'placeholder': 'Start Date Time'}),
            'duration': forms.TextInput(attrs={'type': 'number', 'placeholder': 'Duration'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [field.widget.attrs.update({'class': 'form-control', 'aria-describedby': f'{str(field.label).replace(" ", "").lower()}Feedback'}) for field in self.fields.values()]

    def clean_duration(self):
        data = self.cleaned_data['duration']
        if data > 1440:
            raise ValidationError('Duration over 24 hours. Max 1440 minutes allowed',
                                  code='invalid')
        if data < 1:
            raise ValidationError('Duration must be a positive number.',
                                  code='invalid')

        return data

    def clean(self):
        for field in self.errors:
            self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
        for field in self.cleaned_data:
            self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
        return super().clean()


class PenaltyCreateModelForm(forms.ModelForm):
    class Meta:
        model = Penalty
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'required': True, 'maxlength': 40}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [field.widget.attrs.update({'class': 'form-control form-control-sm'}) for field in self.fields.values()]


class PenaltyTypeCreateModelForm(forms.ModelForm):
    class Meta:
        model = PenaltyType
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'required': True, 'maxlength': 40}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [field.widget.attrs.update({'class': 'form-control form-control-sm'}) for field in self.fields.values()]


class EmployeeUpdateModelForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'username': forms.TextInput(attrs={'required': True, 'maxlength': 40}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [field.widget.attrs.update({'class': 'form-control form-control-sm'}) for field in self.fields.values()]
