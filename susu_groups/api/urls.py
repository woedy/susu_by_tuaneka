from django.urls import path

from home_page.api.views.views import susu_user_home
from susu_groups.api.views import view_all_public_susu_groups, view_all_private_susu_groups, susu_group_detail_view, \
    create_private_susu_group_view, show_susu_group_positions, display_payment_schedule, \
    make_contribution_to_group, receive_payouts_view, kickout_user, join_susu_group_site, join_susu_group_view, \
    delete_group, confirm_payment, show_payment_confirmation_list, view_all_user_susu_groups, \
    join_private_susu_group_view

app_name = 'susu_groups'

urlpatterns = [
    path('list-all-user-groups', view_all_user_susu_groups, name="list_all_user_groups"),
    path('list-all-public-groups', view_all_public_susu_groups, name="list_all_public_groups"),
    path('list-all-private-groups', view_all_private_susu_groups, name="list_all_private_groups"),
    path('susu-group-detail', susu_group_detail_view, name="susu_group_detail"),


    path('create-private-susu-group', create_private_susu_group_view, name="create_private_susu_group_view"),
    path('show-susu-group-positions', show_susu_group_positions, name="show_susu_group_positions"),
    path('display-payment-schedule', display_payment_schedule, name="display_payment_schedule"),
    path('join-susu-group', join_susu_group_view, name="join_susu_group_view"),
    path('join-private-susu-group', join_private_susu_group_view, name="join_private_susu_group_view"),
    path('join_susu_group_site', join_susu_group_site, name="join_susu_group_site"),
    path('make-contribution-to-group', make_contribution_to_group, name="make_contribution_to_group_view"),
    path('receive-payouts', receive_payouts_view, name="receive_payouts_view"),
    path('kickout-user', kickout_user, name="kickout_user_view"),
    path('delete-group', delete_group, name="delete_group_view"),
    path('confirm-payment', confirm_payment, name="confirm_payment_view"),
    path('show-payment-confirmation-list', show_payment_confirmation_list, name="confirm_payment_view"),


]
