from django.db import models
from accounts.models import UserBankAccount
from .constants import TRANSECTION_TYPE_CHOICES

# Create your models here.


class TransectionModel(models.Model):
    account = models.ForeignKey(
        UserBankAccount,
        related_name='transections',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    balance_after_transection = models.DecimalField(
        decimal_places=2, max_digits=10, null=False
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approved = models.BooleanField(default=False)
    transection_type = models.PositiveIntegerField(
        choices=TRANSECTION_TYPE_CHOICES, null=True)

    class Meta:
        ordering = ['timestamp']
