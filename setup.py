from setuptools import find_packages, setup

author = __import__('postgres_stats').__author__
version = __import__('postgres_stats').__version__


setup(
    name='django-postgres-stats',
    version=version,
    url='https://github.com/MarkusH/django-postgres-stats',
    author=author,
    author_email='info@markusholtermann.eu',
    description='',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['Django>=1.11'],
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
