from distutils.core import setup

from setuptools import find_packages

setup(name="LocalJudge",
      version="0.0.1",
      description="",
      long_description="",
      author="NoCLin",
      author_email="engineelin@gmail.com",
      url="https://github.com/NoCLin/LocalJudge",
      license="MIT Licence",
      install_requires=[
          'colorful>=0.5.0',
      ],
      packages=find_packages(),
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'lj = lj.lj:main',
              'ljc = lj.ljc:main',
          ]},
      )
