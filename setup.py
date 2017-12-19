#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='python-canfix',
    version='0.2.0',
    long_description=open('README.rst').read(),
    description="Python CAN-FIX Library",
    author="Phil Birkelbach",
    author_email="phil@petrasoft.net",
    license='GNU General Public License Version 2',
    url='https://github.com/birkelbach/python-canfix',
    packages=['canfix'],
    package_data = {'canfix':['canfix.xml']},
    install_requires = ['python-can',],
    test_suite = 'tests',
)
