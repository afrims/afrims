import datetime

from django.test import TestCase

from afrims.apps.reports.forms import GraphRangeForm, ReportForm


class GraphRangeFormTest(TestCase):
    "Form to validate graph range selection."

    def test_empty_form(self):
        "Nothing is required so an empty form is valid."
        form = GraphRangeForm({})
        self.assertTrue(form.is_valid())

    def test_date_without_months(self):
        "If date is given with no months then use a default 8 months."
        form = GraphRangeForm({'start_date': '2011-06-28'})
        self.assertTrue(form.is_valid())
        data = form.cleaned_data
        self.assertEqual(data['months'], 8)        
        self.assertEqual(data['start_date'], datetime.date(2011, 6, 28))

    def test_months_without_date(self):
        "If months is given with no date then use today as the day."
        form = GraphRangeForm({'months': 6})
        self.assertTrue(form.is_valid())
        data = form.cleaned_data
        self.assertEqual(data['months'], 6)        
        self.assertEqual(data['start_date'], datetime.date.today())


class ReportFormTest(TestCase):
    "Report month/year selection."

    def test_empty_form(self):
        "Nothing is required so an empty form is valid."
        form = ReportForm({})
        self.assertTrue(form.is_valid())

    def test_max_year(self):
        "Cannot select a year greater than the current year."
        form = ReportForm({'report_year': datetime.date.today().year + 1})
        self.assertFalse(form.is_valid())
