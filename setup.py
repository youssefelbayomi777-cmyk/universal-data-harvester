from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="universal-data-harvester",
    version="1.0.0",
    author="Ahmed Hassan",
    author_email="ahmed.hassan@example.com",
    description="Universal Data Harvesting Unit - Advanced web scraping with AI collaboration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/youssefelbayomi777-cmyk/universal-data-harvester",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    keywords="web scraping, data extraction, ai collaboration, automation",
    project_urls={
        "Bug Reports": "https://github.com/youssefelbayomi777-cmyk/universal-data-harvester/issues",
        "Source": "https://github.com/youssefelbayomi777-cmyk/universal-data-harvester",
        "Documentation": "https://github.com/youssefelbayomi777-cmyk/universal-data-harvester/blob/main/README.md",
    },
)
