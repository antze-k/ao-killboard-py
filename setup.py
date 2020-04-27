import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ao-killboard",
    version="0.1.1",
    author="Antze K.",
    author_email="unresolved-external@singu-lair.com",
    description="A minimalistic Discord bot for Albion Online's killboard.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/antze-k/ao-killboard-py",
    project_urls={
        "Source": "https://github.com/antze-k/ao-killboard-py",
        "Tracker": "https://github.com/antze-k/ao-killboard-py/issues",
    },
    packages=setuptools.find_namespace_packages("src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "ao_killboard.py = antze.ao_killboard:_entrypoint_main",
        ]
    },
    zip_safe=True,
    install_requires=["discord.py","httpx","python-dateutil"],
    classifiers=[
        "Topic :: Utilities",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="MIT",
    platforms=["any"],
)
