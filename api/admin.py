# from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Project, Verification, CarbonCredit, CreditRequest, Transaction, Certificate


admin.site.register(User)
admin.site.register(Project)
admin.site.register(Verification)
admin.site.register(CarbonCredit)
admin.site.register(CreditRequest)
admin.site.register(Transaction)
admin.site.register(Certificate)