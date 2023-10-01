from django.contrib import admin

from susu_groups.models import SusuGroupUser, SusuGroup, PaymentSchedule, SusuPosition, InvitedMember, Payout, \
    Contribution

admin.site.register(SusuGroupUser)
admin.site.register(SusuGroup)
admin.site.register(SusuPosition)
admin.site.register(PaymentSchedule)
admin.site.register(InvitedMember)
admin.site.register(Payout)
admin.site.register(Contribution)
