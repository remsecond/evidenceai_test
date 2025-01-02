from setuptools import setup, find_packages

setup(
    name="evidenceai",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'PyPDF2>=3.0.0',
    ],
)