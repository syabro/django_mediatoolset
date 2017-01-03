from distutils.core import setup

__version__ = "0.1.3"

setup(
    name='django-mediatoolset',
    version=__version__,
    description='Useful tools to work with media',
    packages=['mediatoolset', 'mediatoolset.management', 'mediatoolset.management.commands'],

    author='Max Syabro',
    author_email='maxim@syabro.com',
    url='https://github.com/syabro/django_mediatoolset',

    classifiers=[
        'Environment :: Console',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
    ],
)