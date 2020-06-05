import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ocus_helper",
    version="0.0.6",
    author="Megan Fillion",
    author_email="megan@ocus.com",
    description="methods pertaining to database and server calls",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/megan-fillion/ocus_helper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
