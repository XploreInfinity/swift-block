<h1 align='center'> Swift-Block</h1>
<p align='center'>
<img src="swift_block/assets/app_icon.svg" height="200px" width="200px"/><br/>
Version:0.1-beta
</p>

**About:**

Swiftblock is a free and open-source hosts file based ad,malware and tracker blocker written in Python's Pyqt6 framework.

**Features:**

* Free & Open Source(SwiftBlock is licensed under GPLv3)
* Custom sources(You can easily add custom sources of hosts files)
* Custom Rules(You can manually redirect,allow or block specific hostnames!)

**Supported Platforms:**

Most linux distributions, Windows, FreeBSD and MacOS[Testing on all these platforms is pending. Please note though, that I currently have no plans to test it on MacOS]

**Run Instructions:**
To run swift block,execute the following commands in your terminal/command prompt:

* First get all the dependencies of swift_block by running the following:
* `python -m pip install pyqt6>=6.2.2` on Linux/FreeBSD/MacOS or `py -m pip install pyqt6>=6.2.2` on Windows
* Next,open the terminal/command prompt in the root folder of the project
* `cd swift_block`
* For Linux/FreeBSD/MacOS: `python __init__.py`
* For Windows `py __init__.py`
* Swift-Block should now be running

**Why the weird way of distribution?**
I'm experiencing several issues with packaging and publishing swift-block on pypi,until I resolve those issues, I'm afraid this is the only way swift-block will be distributed.

**Inspiration:**

Swiftblock is inspired from [Adaway](https://adaway.org) and uses some UX concepts from it[No code from the project has been taken,however].

**For Contributors:**

* I've used qt-designer to create all the GUI interfaces,kindly use the same/another compatible designer for making any modifications in GUI. All the ui files are in `swift_block/ui`
* `swift_block/__init.py` is the entry point/script executed to initialise everything
* `swift_block/main.py` is the home page of swift-block - it offers users options to manage their hosts sources,update source files, enable/disable swift-block and other misc. stuff.
* `swift_block/Parser.py` is the heart of swift-block, with low level functions for performing operations on hosts files and sources,first-start,restoring/replacing corrupt files,validation tasks, etc.[It is a non-GUI module]
* `swift_block/RuleManager.py` is the GUI rule editor. It offers users options to block/redirect/allow custom/specific hostnames and also allow or redirect the hostnames being blocked by the source files
* Images and icons used within the GUI are stored in the `swift_block/assets` directory.
* `swift_block/elevate` is a sub-package that provides privilege escalation functionality(Required to read/write to the system hosts file). It is my modification of the original and currently broken [elevate](https://github.com/barneygale/elevate).

Made with ❤️ by Xploreinfinity

P.S:Yes,I am aware swift-block's logo is that of [Swift lang](https://www.swift.org/), but there really aren't any better icons out there,sadly[None that suit the overall feel of swift-block,anyway].
