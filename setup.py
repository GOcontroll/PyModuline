from pathlib import Path

from setuptools import setup

root = Path(__file__).parent
long_description = (root / "README.md").read_text()

setup(
    name="PyModuline",
    version="0.0.1",
    description="A python api for several functions of the GOcontroll Moduline controllers",
    url="https://github.com/GOcontroll/PyModuline",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GOcontroll",
    author_email="info@gocontroll.com",
    maintainer="Maud Spierings",
#    install_requires=["pydbus","PyGObject"],
    packages=[
        "PyModuline",
    ],
    python_requires=">=3.9",
)
