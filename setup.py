from setuptools import setup, find_packages

PACKAGE_VERSION = "0.2"
MINOR_RELEASE = "0"

setup(
    name="deep_parser",
    version=f"{PACKAGE_VERSION}.{MINOR_RELEASE}",
    packages=find_packages(where="src"),  # include all packages under src
    package_dir={"": "src"},
    include_package_data=True,

    install_requires=[
        "numpy",
        "pymupdf",
        "anytree",
        "pyyaml",
        "beautifulsoup4",
        "lxml",
        # "requests-html",
        "readable-content",
        "timeout-decorator",
        "pandas>=2.0.0",
        "requests",
        "trafilatura"
        ],

    entry_points={
        'console_scripts': [
            'download-chromium = deep_parser:download_pypeeter_chromium',
        ]
    },

    author="",
    author_email="",
    description="This package contains parsing utilities for text extraction",

    classifiers=[
        ""
    ]
)
