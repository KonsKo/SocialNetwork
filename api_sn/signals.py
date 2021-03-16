from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone

from .models import UserSocial


# Signal catches processing of user login and write date and time to db
# 'try-except' if user was crated no by service (for example superuser)
@receiver(user_logged_in)
def last_user_login(sender, request, user, **kwargs):
    try:
        user_social = UserSocial.objects.get(user=user)
        user_social.last_login = timezone.now()
        user_social.save()
    except:
        pass
