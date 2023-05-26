#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='python-canfix',
    version='0.3.0',
    long_description=open('README.rst').read(),
    description="Python CAN-FIX Library",
    author="Phil Birkelbach",
    author_email="phil@petrasoft.net",
    license='GNU General Public License Version 2',
    url='https://github.com/birkelbach/python-canfix',
    packages=find_packages(),
    package_data = {'canfix':['canfix.json']},
    install_requires = ['python-can',],
    test_suite = 'tests',
)
