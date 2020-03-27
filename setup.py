import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="medpc2excel",
    version="1.5.5",
    license="MIT",
    author="Yifeng Cheng",
    author_email="cyfhopkins@gmail.com",
    description="export medpc data to excel file and generate user defined variables",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cyf203/medpc2excel",
    packages=setuptools.find_packages(),
    install_requires = ['numpy', 'pandas','dill','openpyxl'],
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)