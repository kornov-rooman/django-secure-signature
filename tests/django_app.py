from django.conf.urls import url
from django.http import JsonResponse

DEBUG = True
SECRET_KEY = 'some-secret-key'
ROOT_URLCONF = __name__


# noinspection PyUnusedLocal
def index0(request):
    return JsonResponse({'data': 'ok'})


def index1(request):
    return JsonResponse({'data': request.signed_headers})


def index2(request):
    return JsonResponse({'data': request.confirmed_data})


urlpatterns = [
    url(r'^index-0/$', index0, name='index0'),
    url(r'^index-1/$', index1, name='index1'),
    url(r'^index-2/$', index2, name='index2'),
]


def custom_data_generator():
    return 'test'
