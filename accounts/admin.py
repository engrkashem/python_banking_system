from django.contrib import admin

# Register your models here.
from .models import User, UserAddress, UserBankAccount, UserBankAccountType

admin.site.register(User)
admin.site.register(UserAddress)
admin.site.register(UserBankAccount)
admin.site.register(UserBankAccountType)
