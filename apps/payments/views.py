from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from .providers import PROVIDERS


@csrf_exempt
def webhook(request, provider):
    handler = PROVIDERS.get(provider)
    if not handler:
        return HttpResponseBadRequest("Unknown provider")
    handler.handle_webhook(request)
    return HttpResponse("ok")
