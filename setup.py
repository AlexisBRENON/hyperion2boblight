""" Installation module """

from setuptools import setup

setup(
    name='hyperion2boblight',
    version='1.0',
    description='Control a Boblight server with a Hyperion client',
    long_description="""This tiny app allow you to use some Hyperion client
    (as the Hyperion Remote smartphone app) to control your boblight server.""",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License'
        ],
    keywords='hyperion boblight',
    url='http://github.com/AlexisBRENON/hyperemote2boblight',
    author='Alexis BRENON',
    author_email='brenon.alexis+hyperemote2boblight@gmail.com',
    license='MIT',
    packages=['hyperion2boblight'],
    zip_safe=False,
    )

