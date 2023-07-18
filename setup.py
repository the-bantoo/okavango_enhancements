from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in okavango_enhancements/__init__.py
from okavango_enhancements import __version__ as version

setup(
	name="okavango_enhancements",
	version=version,
	description="Custom scripts for Okavango",
	author="Bantoo",
	author_email="devs@thebantoo.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
