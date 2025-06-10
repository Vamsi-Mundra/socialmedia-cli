from setuptools import setup, find_packages

setup(
    name="socialmedia-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "tweepy",
        "pytest",
        "pytest-mock",
    ],
    entry_points={
        'console_scripts': [
            'socialmedia-cli=socialmedia_cli.cli:main'
        ]
    },
    python_requires=">=3.6",
    author="SocialMedia CLI Team",
    description="A CLI tool for posting to social media platforms",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
) 