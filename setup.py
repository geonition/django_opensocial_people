from setuptools import setup
from setuptools import find_packages

setup(
    name='opensocial_people',
    version='4.0.1',
    author='Kristoffer Snabb',
    url='https://github.com/geonition/django_opensocial_people',
    packages=find_packages(),
    include_package_data=True,
    package_data = {
        "opensocial_people": [
            "templates/opensocial_people.jquery.js",
            "templates/email_base.html",
            "templates/emailconfirmation/default_confirm_template.html",
            "templates/emailconfirmation/email_confirmation_message.txt",
            "templates/emailconfirmation/email_confirmation_subject.txt"
        ],
    },
    zip_safe=False,
    install_requires=['django']
)
