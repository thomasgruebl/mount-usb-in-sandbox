from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='mount-usb-in-sandbox',
    version='1.0.0',
    description='Automatically mounts a USB device in a sandbox',
    long_description=long_description,
    author='Thomas Gruebl',
    author_email="notmyrealemail@gmail.com",
    url='https://github.com/thomasgruebl/mount-usb-in-sandbox',
    packages=['usb', 'sandbox'],
    license='MIT',
    keywords='usb mount sandbox whonix',
    python_requires='>=3.8',
    install_requires=[
        'setuptools>=57.0.0'
    ]
)
