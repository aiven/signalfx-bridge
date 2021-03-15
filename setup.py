from sfxbridge import __version__
from setuptools import find_packages, setup
import os

setup(
    name="sfxbridge",
    version=os.getenv("VERSION") or __version__,
    description="telegraf http output to signalfx pump",
    author="Aiven Oy",
    author_email="support@aiven.io",
    zip_safe=False,
    packages=find_packages(exclude=["tests"]),
    extras_require={},
    dependency_links=[],
    package_data={},
    data_files=[],
    python_requires=">=3.7",
    install_requires=["aiohttp", "systemd-python"],
    entry_points={
        "console_scripts": [
            "sfxbridge = sfxbridge.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
    ],
)
