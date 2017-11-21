from setuptools import find_packages, setup

author = __import__('postgres_metrics').__author__
version = __import__('postgres_metrics').__version__

with open('README.rst') as fp:
    description = fp.read()

setup(
    name='django-postgres-metrics',
    version=version,
    url='https://github.com/django-postgres-metrics/django-postgres-metrics',
    author=author,
    author_email='info+django-postgres-stats@markusholtermann.eu',
    description=description,
    license='BSD',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    install_requires=['Django>=1.11', 'psycopg2'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
