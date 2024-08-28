import os.path

from setuptools import find_packages, setup

REQUIREMENTS_FILE = "requirements.txt"
SRC_FOLDER = "src"

required:list[str] = []
if os.path.isfile(REQUIREMENTS_FILE):
    with open(REQUIREMENTS_FILE, encoding="utf8") as f:
        required.extend(f.read().splitlines())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description: str = fh.read()

setup(
    name="aws-s3-helper",
    version="1.0.0",
    author="Sergio Jimenez Moreno",
    author_email="sergio.jimenez@xauencybersecurity.com",
    description="Abstraction for easy access to AWS S3.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sjm00010/AWS_S3_Helper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": SRC_FOLDER},
    packages=find_packages(where=SRC_FOLDER),
    install_requires=required,
    python_requires=">=3.7",
)
