'''Setup script for MonkeyPatchEasyBuild'''

from setuptools import setup, find_packages

setup(
    name="MonkeyPatchEasyBuild",
    version="0.2",
    packages=find_packages(),
    install_requires=['pluggy', 'py'],
    entry_points={
        'console_scripts': [
            'mpeb = mpeb.main:main',
        ]
    },
)
