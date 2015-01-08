from setuptools import setup, find_packages

setup(
    name='bitcoingraph',
    version='0.1.dev',
    packages=['bitcoingraph'],
    scripts=['bin/bcgraph-generate'],

    install_requires=['requests>=2.5.0'],

    test_suite='tests',

    author='Bernhard Haslhofer',
    author_email='bernhard.haslhofer@ait.ac.at',
    description='A Python library for extracting graphs from the\
                   Bitcoin\ blockchain',
    license='MIT',
    url='https://bitbucket.org/bhaslhofer/bitcoingraph',
)
