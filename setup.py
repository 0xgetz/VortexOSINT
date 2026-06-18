from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vortexosint",
    version="1.1.0",
    description="Modern, complete, 100% free OSINT toolkit (username, email, domain, IP, phone).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0xgetz/VortexOSINT",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.7.0",
        "dnspython>=2.6.0",
        "python-whois>=0.9.4",
        "phonenumbers>=8.13.0",
        "Pillow>=10.0.0",
        "reportlab>=4.0.0",
    ],
    entry_points={"console_scripts": ["vortex=vortexosint.cli:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Intended Audience :: Information Technology",
    ],
)
