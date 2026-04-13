import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="medpc2excel",
    version="4.0.0",
    license="MIT",
    author="Yifeng Cheng",
    author_email="cyfhopkins@gmail.com",
    description="export medpc data to excel file and generate user defined variables",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cyf203/medpc2excel",
    packages=setuptools.find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=2.4",
        "pandas>=2.3",
        "openpyxl>=3.1",
        "matplotlib>=3.10",
        "mplcursors>=0.7",
        "PyQt5>=5.15",
    ],
    entry_points={
        "console_scripts": [
            "medpc2excel=medpc2excel.gui:run",
        ]
    },
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
