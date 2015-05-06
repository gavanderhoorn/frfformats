import os
from setuptools import setup

setup(
    name = "frfformats",
    version = "0.0.1",
    author = "G.A. vd. Hoorn",
    author_email = "g.a.vanderhoorn@tudelft.nl",
    description = ("A Python library for reading (and sometimes writing) Fanuc Robotics file formats."),
    license = "Apache2.0",
    packages=['frfformats'],
    package_dir={'': 'src'},
    url="https://github.com/gavanderhoorn/frfformats",
    install_requires=['enum34']
)
