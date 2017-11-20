from setuptools import find_packages, setup

author = __import__('postgres_metrics').__author__
version = __import__('postgres_metrics').__version__

setup(
    name='django-postgres-metrics',
    version=version,
    url='https://github.com/django-postgres-metrics/django-postgres-metrics',
    author=author,
    author_email='info@markusholtermann.eu',
    description='',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['Django>=1.11', 'psycopg2'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
