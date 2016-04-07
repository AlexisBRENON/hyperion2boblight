""" Installation module """
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    """ PyTest integration with setuptools """
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ["hyperion2boblight"]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name='hyperion2boblight',
    version='2.0.0',
    description='Control a Boblight server with a Hyperion client',
    long_description="""This tiny app allow you to use some Hyperion client
    (as the Hyperion Remote smartphone app) to control your boblight server.""",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License'
        ],
    keywords='hyperion boblight',
    url='http://github.com/AlexisBRENON/hyperion2boblight',
    author='Alexis BRENON',
    author_email='brenon.alexis+hyperion2boblight@gmail.com',
    license='MIT',
    packages=['hyperion2boblight'],
    zip_safe=False,
    tests_require=['pytest'],
    cmdclass={'test':PyTest},
    entry_points={
        'console_scripts': ['hyperion2boblight=hyperion2boblight.main:main']
    }
)

