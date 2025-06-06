from setuptools import setup, find_packages

setup(
    name="gwan-python-app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # As dependências serão lidas do requirements.txt
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.8",
) 