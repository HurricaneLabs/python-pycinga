from setuptools import setup

# Get the long description by reading the README
try:
    readme_content = open("README.rst").read()
except Exception as e:
    readme_content = ""

# Create the actual setup method
setup(
    name="pycinga",
    version="1.0.0",
    description="Python library to write Icinga plugins.",
    long_description=readme_content,
    author="Steve McMaster",
    author_email="mcmaster@hurricanelabs.com",
    maintainer="Steve McMaster",
    maintainer_email="mcmaster@hurricanelabs.com",
    url="https://github.com/hurricanelabs/python-pycinga",
    license="MIT License",
    keywords=["nagios", "pynagios", "icinga", "pycinga", "monitoring"],
    packages=["pycinga"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration"
    ]
)
