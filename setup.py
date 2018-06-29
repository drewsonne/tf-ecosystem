from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tf-ecosystem',
    author='Drew J. Sonne',
    author_email='drew.sonne@gmail.com',
    description='A framework for initialising a terraform environment',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3',
    version='1.0.4',
    url='http://github.com/drewsonne/tf-ecosystem',
    license='LGPLv2',
    include_package_data=True,
    packages=find_packages(),
    keywords='terraform cli',
    install_requires=[
        'marshmallow',
        'click',
        'pyaml',
        'termcolor'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System',
        'Topic :: System :: Systems Administration',
    ],
    setup_requires=['nose>=1.0'],
    entry_points={
        'console_scripts': [
            'tf-eco = tfeco.scripts:cli',
            'tf-ecosystem = tfeco.scripts:cli'
        ]
    },
    test_suite='nose.collector',
    tests_require=[
        'coverage',
        'nose',
        'nose-cover3'
    ],
    zip_safe=True,
)
