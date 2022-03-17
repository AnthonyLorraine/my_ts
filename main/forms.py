from django import forms
from django.forms import inlineformset_factory
from main.models import Timesheet, TimesheetRow


class TimeSheetModelForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = '__all__'
        widgets = {
            'employee': forms.TextInput(attrs={'hidden': True}),
            'start_date_time': forms.DateTimeInput(attrs={'required': True, 'type': 'datetime-local', 'max': '2100-01-01T00:00', 'min': '2020-01-01T00:00', 'placeholder': 'Start Date Time'}),
            'duration': forms.TextInput(attrs={'required': True, 'maxlength': 4, 'placeholder': 'Duration'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [field.widget.attrs.update({'class': 'form-control'}) for field in self.fields.values()]


