'''
Copyright (C) 2021 xploreinfinity

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
'''

import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name="swift_block",
    version="0.3",
    author="Xploreinfinity",
    license="GPLv3",
    description="Swiftblock is a free and open-source hosts file based ad,malware and tracker blocker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/XploreInfinity/swift-block",

    entry_points={
        'gui_scripts': [
            'swift-block =swift_block.__init__:main',
        ],
        'console_scripts': [
            'swift-block-win =swift_block.__init__:main',
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
    install_requires=[
        'pyqt6>=6.2.2',
        'requests',
        'winshell; sys_platform == "win32"',
        'pywin32; sys_platform == "win32"'
    ],
    python_requires=">=3.6",
)
