from django.core import signing
from django.http import HttpResponseForbidden

from .settings import settings


class SignMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.secrets = {
            'key': settings.SECRET,
            'salt': settings.SALT,
        }
        self.signer = signing.TimestampSigner(**self.secrets)

    def __call__(self, request):
        if settings.SHOULD_SIGN_DATA:
            self.patch_request_with_signed_data(request)

        response = self.get_response(request)

        if settings.SHOULD_SIGN_DATA:
            self.add_response_headers(request, response)

        return response

    def patch_request_with_signed_data(self, request):
        data = settings.TARGET(request)

        signed_data = signing.dumps(data, **self.secrets)
        timestamped_signed_data = self.signer.sign(signed_data)

        setattr(request, 'signed_data', timestamped_signed_data)

    @staticmethod
    def add_response_headers(request, response):
        signed_data = getattr(request, 'signed_data', None)

        if signed_data is not None:
            response[settings.HEADER] = signed_data


class UnsignMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.secrets = {
            'key': settings.SECRET,
            'salt': settings.SALT,
        }
        self.signer = signing.TimestampSigner(**self.secrets)

    def __call__(self, request):
        try:
            self.patch_request_with_confirmed_signed_data(request)
        except (signing.SignatureExpired, signing.BadSignature) as e:
            msg = f'{e.__class__.__name__}: "{e}"'
            return HttpResponseForbidden(msg)

        return self.get_response(request)

    def patch_request_with_confirmed_signed_data(self, request):
        value = request.META.get(settings.META_FORMATTED_HEADER, None)
        if value is None:
            return

        signed_data = self.signer.unsign(value, max_age=settings.MAX_AGE)
        confirmed_signed_data = signing.loads(signed_data, **self.secrets)

        setattr(request, 'confirmed_signed_data', confirmed_signed_data)
