from setuptools import find_packages, setup

REQUIREMENTS_FILE = "requirements.txt"
SRC_FOLDER = "src"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description: str = fh.read()

setup(
    name="aws-s3-helper",
    version="1.3.2",
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
    install_requires=["boto3", "tqdm"],
    python_requires=">=3.8",
)
