from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autonoma",
    version="0.1.0",
    author="Bas Bollaart",
    author_email="sebastiaan.bollaart@gmail.com",
    description="AI-powered autonomous code modification and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sebasbo/autonoma",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pydantic>=1.8.0,<2.0.0",
        
        # Add other dependencies here
    ],
    extras_require={
        "dev": ["pytest>=6.0", "flake8>=3.9.0"],
    },
)