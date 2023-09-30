from typing import Any
from django import forms
from .models import TransectionModel
from django.conf import settings


class TransectionModelForm(forms.ModelForm):
    class Meta:
        model = TransectionModel
        fields = ['amount', 'transection_type']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transection_type'].disabled = True
        self.fields['transection_type'].widget = forms.HiddenInput

    def save(self, commit: bool = True) -> Any:
        self.instance.account = self.account
        self.instance.balance_after_transection = self.account.balance
        return super().save()


class DepositForm(TransectionModelForm):

    def clean_amount(self):
        min_deposit_amount = settings.MINIMUM_DEPOSIT_AMOUNT
        amount = self.cleaned_data.get('amount')

        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount}')
        return amount


class WithdrawForm(TransectionModelForm):
    def clean_amount(self):
        account = self.account
        min_withdraw_amount = settings.MINIMUM_WITHDRAWAL_AMOUNT
        max_withdraw_amount = (
            account.account_type.maximum_withdrawal_amount
        )
        balance = account.balance
        amount = self.clean_amount.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'Minimum Withdrawal Amount is {min_withdraw_amount}')
        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'Maximun Withdrawal Amount for you is {max_withdraw_amount}')
        if amount > balance:
            raise forms.ValidationError(
                f'Insufficint Funds. Your current balance is {balance}.'
            )
        return amount


class LoanRequestForm(TransectionModelForm):
    def clean_field(self):
        amount = self.cleaned_data["amount"]

        return amount
