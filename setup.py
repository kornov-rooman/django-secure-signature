import os
import shutil
import sys
from setuptools import setup, find_packages

from django_secure_signature import __version__

try:
    from pypandoc import convert_file

    def read_md(f):
        return convert_file(f, 'rst')
except ImportError:
    print('warning: pypandoc module not found, could not convert Markdown to RST')

    def read_md(f):
        return open(f, 'r', encoding='utf-8').read()

if sys.argv[-1] == 'publish':
    try:
        import pypandoc
    except ImportError:
        print('pypandoc not installed.\nUse `pip install pypandoc`.\nExiting.')

    if os.system('pip freeze | grep twine'):
        print('twine not installed.\nUse `pip install twine`.\nExiting.')
        sys.exit()

    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    print('You probably want to also tag the version now:')
    print('  git tag -a %s -m \'version %s\'' % (__version__, __version__))
    print('  git push --tags')

    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('django_secure_signature.egg-info')

    sys.exit()

setup(
    name='django-secure-signature',

    description='Secure data signing for django apps, ready-to-use (allegedly).',
    long_description=read_md('README.md'),

    url='https://github.com/kornov-rooman/django-secure-signature',
    version=__version__,
    license='MIT',

    author='Kornov Rooman',
    author_email='kornov.rooman@gmail.com',

    packages=find_packages(exclude=['tests*']),
    python_requires='>=3.4',
    requires=['django', 'typing'],

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
)
