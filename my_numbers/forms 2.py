
from django import forms
from .models import *
from base.choices import (create_quarter_range_dates,
                          create_year_range_dates,
                          years_choices)


class ReportQuarterForm(forms.ModelForm):
    """
    To report different quarters
    """
    class Meta:
        model = ReportModel
        fields = ['year_start','quarter']
        labels = {
            'year_start':'Year Start',
            'quarter':'Quarter'}

    def save(self, commit=True):
        instance = super().save(commit=False)
        year_start = self.cleaned_data['year_start']
        quarter = self.cleaned_data['quarter']
        date_start,date_end = create_quarter_range_dates(quarter,year_start)
        instance.period_start = date_start
        instance.period_end = date_end
        instance.period_type = 'quarter'
        if commit:
            instance.save()
        return instance


class ReportYearForm(forms.ModelForm):
    """
    To report different years
    """
    class Meta:
        model = ReportModel
        fields = ['year_start']
        labels = {
            'year_start':'Year Start',
        }
    def save(self, commit=True):
        instance = super().save(commit=False)
        year_start = self.cleaned_data['year_start']
        date_start,date_end = create_year_range_dates("jan-dec",year_start)
        instance.period_start = date_start
        instance.period_end = date_end
        instance.period_type = 'year'
        if commit:
            instance.save()
        return instance


class ReportTaxYearForm(forms.Form):
    """
    To report different tax years
    """
    class Meta:
        model = ReportModel
        fields = ['year_start']
        labels = {
            'year_start':'Year Start',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        year_start = self.cleaned_data['year_start']
        date_start,date_end = create_year_range_dates("jan-dec",year_start)
        instance.period_start = date_start
        instance.period_end = date_end
        instance.period_type = 'tax_year'
        if commit:
            instance.save()
        return instance


class TransactionForm(forms.ModelForm):
    class Meta:
        model = TransactionModel
        fields = ['date',"amount","is_income","is_recurrent"]
        labels = {
            'date':"date",
            "amount":"amount",
            "is_income":"Is Income?",
            "is_recurrent":"Is recurrent?",
                  }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = TransactionModel
        fields = ['date',"amount","is_recurrent"]
        labels = {
            'date':"date",
            "amount":"amount",
            "is_recurrent":"Is recurrent?",
                  }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_income = False
        if commit:
            instance.save()
        return instance


class IncomeForm(forms.ModelForm):
    class Meta:
        model = TransactionModel
        fields = ['date',"amount","is_recurrent"]
        labels = {
            'date':"date",
            "amount":"amount",
            "is_recurrent":"Is recurrent?",
                  }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_income = True
        if commit:
            instance.save()
        return instance
