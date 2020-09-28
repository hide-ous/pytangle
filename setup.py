import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytangle-hide_ous",
    version="0.0.1",
    author="Mattia Samory",
    author_email="mattia.samory@gmail.com",
    description="A python wrapper for crowdtangle API endpoints",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hide-ous/pytangle/",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests>=2.9.1",
        "ratelimit>=2.2.1",
        "python_dateutil>=2.8.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)