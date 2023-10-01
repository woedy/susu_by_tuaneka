from django.contrib import admin

from payments.models import Payment, Bank

admin.site.register(Payment)
admin.site.register(Bank)