import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="django-postgres-metrics",
    author="Markus Holtermann",
    author_email="info@markusholtermann.eu",
    description="A Django application that exposes a bunch of PostgreSQL database metrics.",
    license="BSD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/django-postgres-metrics/django-postgres-metrics",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    include_package_data=True,
    extras_require={"test": ["tox"]},
    setup_requires=["setuptools_scm>=5<6"],
    use_scm_version=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.5",
)
