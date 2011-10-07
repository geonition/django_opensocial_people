from setuptools import setup
from setuptools import find_packages

setup(
    name='opensocial_people',
    version='1.0.2',
    author='Kristoffer Snabb',
    url='https://github.com/geonition/django_opensocial_people',
    packages=find_packages(),
    include_package_data=True,
    package_data = {
        "opensocial_people": [
            "templates/*.js"
        ],
    },
    zip_safe=False,
    install_requires=['django']
)
