from setuptools import find_packages
from setuptools import setup

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(name='secnlp',
      version="0.0.1",
      description="NLP applied to SEC filings",
      license="MIT",
      author="Debora",
      author_email="debora.ramell@gmail.com",
      install_requires=requirements,
      packages=find_packages())
