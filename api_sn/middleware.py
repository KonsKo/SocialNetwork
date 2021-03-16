from django.utils import timezone

from .models import UserSocial


# Custom middleware for catching last user request
# if success than write date and time to db
# it can be slow for real project
class LastUserRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user:
            if UserSocial.objects.filter(user=request.user.id).exists():
                user_social = UserSocial.objects.get(user=request.user)
                user_social.last_request = timezone.now()
                user_social.save()
        return response
