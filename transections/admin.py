from typing import Any
from django.contrib import admin
from transections.models import TransectionModel

# Register your models here.


@admin.register(TransectionModel)
class TransectionModelAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transection',
                    'transection_type', 'loan_approved']

    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.amount
        obj.balance_after_transection = obj.account.balance
        obj.account.save()
        super().save_model(request, obj, form, change)
