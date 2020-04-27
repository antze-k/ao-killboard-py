import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ao-killboard",
    version="0.1.1.post1",
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
    classifiers=[
        "Topic :: Utilities",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    platforms=["any"],

    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages("src"),
    namespace_packages=["antze"],
    zip_safe=True,

    python_requires=">=3.6",
    install_requires=["discord.py","httpx","python-dateutil"],

    entry_points={
        "console_scripts": [
            "ao_killboard.py = antze.ao_killboard:_entrypoint_main",
        ]
    },
)
