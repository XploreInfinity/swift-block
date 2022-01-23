import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="swift_block",
    version="3.7",
    author="Xploreinfinity",
    author_email="author@example.com",
    description="Swiftblock is a free and open-source hosts file based ad,malware and tracker blocker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/XploreInfinity/swift-block",

    entry_points={
        'console_scripts': [
            'swift-block =swift_block.__init__:main',
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/XploreInfinity/swift-block/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: BSD :: FreeBSD",
    ],
    package_dir={"": ".",},
    packages=setuptools.find_packages(where="."),
    include_package_data=True,
    install_requires=['pyqt6>=6.2.2'],
    python_requires=">=3.6",
)
