from setuptools import find_packages, setup

setup(
    name='eco',
    version='1.0.0',
    url='http://github.com/drewsonne/eco',
    license='Apache 2.0',
    author='Drew J. Sonne',
    author_email='drew.sonne@gmail.com',
    description='A framework for initialising a terraform environment',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'click',
        'termcolor',
        'pyaml'
    ],
    entry_points='''
        [console_scripts]
        tf-eco=tfeco.scripts:cli
        tf-ecosystem=tfeco.scripts:cli
    ''',
)
