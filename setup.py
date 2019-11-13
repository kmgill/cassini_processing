#!/usr/bin/env python

from setuptools import setup

__version__ = '0.1'

setup(
    name="cassini_processing",
    version=__version__,
    url="https://github.com/kmgill/cassini_processing",

    author="Kevin M. Gill",
    maintainer="Kevin M. Gill",
    author_email="kmsmgill [at] gmail [dot] com",
    maintainer_email="kmsmgill [at] gmail [dot] com",

    description="Cassini image processing and simplified ISIS3 API",
    long_description=open('README.md').read(),

    packages=['sciimg',
              'sciimg.isis3',
              'sciimg.pipelines',
              'sciimg.pipelines.cassini_iss',
              'sciimg.pipelines.galileo_iss',
              'sciimg.pipelines.voyager_iss',
              'sciimg.pipelines.mex_hrsc',
              'sciimg.pipelines.junocam',
              'sciimg.pds',
              'sciimg.processes',
              'sciimg.util'
              ],
    package_data={},
    data_files=[],
    platforms='any',

    keywords=[
        'cassini',
        'huygens',
        'saturn',
        'imaging',
        'space',
        'titan',
        'jupiter',
        'iss',
        'issna',
        'isswa',
        'science',
        'planetary',
        'isis3'
    ],

    install_requires=[
        'requests',
        'numpy',
        'pvl',
        'spiceypy',
        'pyopengl',
        'libtiff',
        'scipy',
        'utm',
        'pillow',
        'six'
    ],

    classifiers=[
        'Development Status :: 1 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering'
    ]
)
