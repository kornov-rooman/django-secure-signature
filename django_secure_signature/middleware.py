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
        referer = request.META.get('HTTP_REFERER')

        for signature_settings in settings:
            if signature_settings.RECIPIENT and not referer.startswith(signature_settings.RECIPIENT):
                # skip generation of the signature if a user defined RECIPIENT (service-recipient)
                # and request was made from a different service
                continue

            data = signature_settings.get_data(request)
            if data is None:
                continue

            secrets = {
                'key': signature_settings.SECRET,
                'salt': signature_settings.SALT,
            }

            dumped = signing.dumps(data, **secrets)
            timestamped = signing.TimestampSigner(**secrets).sign(dumped)

            secure_signed_headers[signature_settings.HEADER] = timestamped

        if secure_signed_headers:
            setattr(request, self.request_attr, secure_signed_headers)

    def add_response_headers(self, request, response):
        secure_signed_headers = getattr(request, self.request_attr, None)

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
        confirmed_signed_data = []
        referer = request.META.get('HTTP_REFERER')

        for signature_settings in settings:
            if signature_settings.SENDER and not referer.startswith(signature_settings.SENDER):
                # skip verification of the signature if a user defined SENDER (service-sender)
                # and request was made from a different service
                continue

            value = request.META.get(signature_settings.meta_formatted_header, None)
            if value is None:
                continue

            secrets = {
                'key': signature_settings.SECRET,
                'salt': signature_settings.SALT,
            }

            fresh_data = signing.TimestampSigner(**secrets).unsign(value, max_age=signature_settings.MAX_AGE)
            confirmed_signed_data.append(signing.loads(fresh_data, **secrets))

        setattr(request, self.request_attr, confirmed_signed_data)
