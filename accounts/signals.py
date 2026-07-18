# from allauth.account.signals import user_signed_up
# from django.dispatch import receiver
# from django.contrib.auth import get_user_model
# 
# User = get_user_model()
# 
# @receiver(user_signed_up)
# def populate_profile(request, user, **kwargs):
#     """
#     When a user signs up via social authentication (e.g. Google),
#     they won't have a user_type set from the normal registration form.
#     We default them to 'buyer' so the platform doesn't crash expecting a role.
#     """
#     if not user.user_type:
#         user.user_type = 'buyer'
#         user.save()
