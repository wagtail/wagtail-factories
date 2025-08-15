import re

from setuptools import find_packages, setup

install_requires = [
    "factory-boy>=3.2,<4",
    "wagtail>=6.3",
]

docs_require = [
    "sphinx>=7.3.7",
]

tests_require = [
    "pytest==8.4.1",
    "pytest-django==4.11.1",
    "pytest-cov==6.2.1",
    "coverage==7.10.3",
    "ruff==0.12.8",
]

with open("README.md") as fh:
    long_description = re.sub(
        r"^## Status.*\n(## Installation)", r"\1", fh.read(), flags=re.M | re.S
    )

setup(
    name="wagtail_factories",
    version="4.3.0",
    description="Factory boy classes for wagtail",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Michael van Tellingen",
    author_email="michaelvantellingen@gmail.com",
    url="https://github.com/wagtail/wagtail-factories/",
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        "docs": docs_require,
        "test": tests_require,
    },
    entry_points={},
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 6",
        "Framework :: Wagtail :: 7",
    ],
    zip_safe=False,
)
