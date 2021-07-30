#!/usr/bin/env python
from setuptools import (
    setup,
    find_packages,
)

extras_require = {
    'test': [
        'django-constance[database]',
        'factory_boy',
        'pytest',
        'pytest-cov',
        'pytest-django',
    ],
    'lint': [
        'black',
        'flake8',
        'isort',
    ],
    'doc': [],
    'dev': ['tox', 'setuptools-scm'],
}

extras_require['dev'] += (
    extras_require['test'] +
    extras_require['lint'] +
    extras_require['doc']
)


setup(
    name='django_frontend_settings',
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    url='https://github.com/loadsmart/django-frontend-settings',
    license='MIT',
    description='Expose feature flags and settings from django waffle and django constance in an endpoint.',
    long_description=open('README.rst', 'r', encoding='utf-8').read(),
    author='Loadsmart',
    author_email='developer@loadsmart.com',
    install_requires=[
        'django',
        'djangorestframework',
        'django-picklefield',
        'django-constance>=2,<3',
        'django-waffle>=2,<3',
    ],
    python_requires='>=3.6',
    extras_require=extras_require,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
