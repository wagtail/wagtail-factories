import re

from setuptools import find_packages, setup

install_requires = [
    "factory-boy>=2.8.0",
    "wagtail>=2.0",
]

docs_require = [
    "sphinx>=1.4.0",
]

tests_require = [
    "pytest==6.0.1",
    "pytest-django==3.9.0",
    "pytest-cov==2.7.1",
    "pytest-pythonpath==0.7.3",
    "psycopg2>=2.3.1",
    "coverage==4.5.3",
    "isort==4.3.21",
    "flake8==3.7.8",
    "flake8-blind-except==0.1.1",
    "flake8-debugger==3.1.0",
]

with open("README.rst") as fh:
    long_description = re.sub(
        "^.. start-no-pypi.*^.. end-no-pypi", "", fh.read(), flags=re.M | re.S
    )

setup(
    name="wagtail_factories",
    version="2.0.1",
    description="Factory boy classes for wagtail",
    long_description=long_description,
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    zip_safe=False,
)
