from django.core import signing
from django.http import HttpResponseForbidden

from .settings import settings


class SignMiddleware:
    request_attr = 'signed_headers'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.patch_request_with_signed_data(request)
        response = self.get_response(request)
        self.add_response_headers(request, response)
        return response

    def patch_request_with_signed_data(self, request):
        secure_signed_headers = {}

        for signature_settings in settings:
            data = signature_settings.get_data(request)
            if data is None:
                continue

            secrets = {
                'key': signature_settings.SECRET,
                'salt': signature_settings.SALT,
            }

            signature = signing.dumps(data, **secrets)
            secure_signed_headers[signature_settings.HEADER] = signature

        if secure_signed_headers:
            setattr(request, self.request_attr, secure_signed_headers)

    def add_response_headers(self, request, response):
        secure_signed_headers = getattr(request, self.request_attr, None)

        if secure_signed_headers is None:
            return

        for header, signature in secure_signed_headers.items():
            response[header] = signature


class UnsignMiddleware:
    request_attr = 'confirmed_data'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            self.patch_request_with_confirmed_signed_data(request)
        except (signing.SignatureExpired, signing.BadSignature) as e:
            msg = f'{e.__class__.__name__}: "{e}"'
            return HttpResponseForbidden(msg)

        return self.get_response(request)

    def patch_request_with_confirmed_signed_data(self, request):
        confirmed_data = []

        for signature_settings in settings:
            signature = request.META.get(signature_settings.meta_formatted_header, None)
            if signature is None:
                continue

            secrets = {
                'key': signature_settings.SECRET,
                'salt': signature_settings.SALT,
            }

            data = signing.loads(signature, **secrets, max_age=signature_settings.MAX_AGE)
            confirmed_data.append(data)

        if confirmed_data:
            setattr(request, self.request_attr, confirmed_data)
