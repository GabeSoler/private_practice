
from django import forms

from session_client.choices import years_choices
from .models import *
from .choices import TAX_YEAR_TYPE_CHOICES


class ReportQuarterForm(forms.ModelForm):
    class Meta:
        model = ReportModel
        fields = ['year_start','quarter']
        labels = {
            'year_start':'Year Start',
            'quarter':'Quarter'}

class ReportYearForm(forms.ModelForm):
    year = forms.ChoiceField(choices=years_choices())

class ReportTaxYearForm(forms.Form):
    year = forms.ChoiceField(choices=years_choices())
    tax_range = forms.ChoiceField(choices=TAX_YEAR_TYPE_CHOICES)

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
