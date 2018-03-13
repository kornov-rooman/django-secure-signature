from setuptools import setup, find_packages

from django_secure_signature import __version__

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='django-signed',
    version=__version__,
    packages=find_packages(),
    url='https://github.com/kornov-rooman/django-secure-signature',
    license='MIT',
    author='Kornov Rooman',
    author_email='kornov.rooman@gmail.com',
    description='Django Secure Signature, secure data signing for django apps, ready-to-use (allegedly).',
    long_description=long_description,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
    ],
    requires=['django']
)
