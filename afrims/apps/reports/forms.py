import datetime

from django import forms
from django.utils.dates import MONTHS


class GraphRangeForm(forms.Form):
    "Validate graph date range selections."

    start_date = forms.DateField(required=False)
    months = forms.IntegerField(required=False)

    def clean(self):
        cleaned_data = super(GraphRangeForm, self).clean()
        start_date = cleaned_data.get('start_date', None) or None
        months = cleaned_data.get('months', None) or None
        if start_date is not None and months is None:
            # Default to show 8 months if start date is specified
            cleaned_data['months'] = 8
        elif start_date is None and months is not None:
            # Use today for start
            cleaned_data['start_date'] = datetime.date.today()
        return cleaned_data


class ReportForm(forms.Form):
    report_month = forms.TypedChoiceField(label='Report Month', required=False,
        coerce=int, choices=MONTHS.items(), 
    )
    report_year = forms.IntegerField(label='Report Year', required=False,
        min_value=1970, max_value=datetime.date.today().year
    )
