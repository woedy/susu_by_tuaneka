from django.contrib import admin

from user_profile.models import PersonalInfo, AdminInfo, Wallet

admin.site.register(PersonalInfo)
admin.site.register(Wallet)
admin.site.register(AdminInfo)
