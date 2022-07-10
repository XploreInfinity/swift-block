<h1 align='center'> Swift-Block</h1>
<p align='center'>
<img src="swift_block/assets/app_icon.svg" height="200px" width="200px"/><br/>
Version:0.3.1(beta)
</p>

## About:

Swiftblock is a free and open-source hosts file based ad,malware and tracker blocker written in Python's Pyqt6 framework.

## Features:

* Free & Open Source(SwiftBlock is licensed under GPLv3)
* Custom sources(You can easily add custom sources of hosts files)
* Custom Rules(You can manually redirect,allow or block specific hostnames)
* Easy access(Swift-Block will create a launcher/start menu shortcut on first run)

## Supported Platforms:

Most linux distributions, Windows, FreeBSD and MacOS[Not tested on FreeBSD and MacOS]

## Installation:

* Open your terminal/command prompt and run the following command as superuser/administrator :
  `python -m pip install swift_block`
* Now launch swift-block from your terminal/command-line by running this command(ensure you have internet first):
  `swift-block`
* Swift-Block will pull hosts sources from the internet and create a launcher/start menu shortcut during the first run
* Swift-Block can be accessed from your DE's menu/start menu like any normal application from this point onwards.

## Uninstallation:

* Open Swift-Block
* Go to the `About` tab and click on the `Uninstall` button
* It is not recommended to directly use pip to uninstall swift-block unless the above method fails
* To uninstall Swift-Block directly using pip, run this as superuser/administrator from your terminal/cmd:
  `python -m pip uninstall swift_block`

## Building from source(for contributors):

* Clone this repo and open a terminal/cmd in the main project folder
* Run the following command as superuser/administrator:
  `python -m pip install .`
* Swift-Block will be built & installed

## (IMPORTANT) SPECIAL INSTRUCTIONS FOR WINDOWS USERS:

Windows has issues with larger hosts files.The DNS Client service needs to be disabled to mitigate this. Recent changes in security within Windows 10 denies access to changing services via other tools except registry hacks. Use [this bat file](https://github.com/StevenBlack/hosts/blob/master/disable-dnscache-service-win.bat))(Obviously,run this file as an Administrator) to make proper changes to the Windows registry. You will need to reboot your device once that's done.

## Why are my changes not applied?

Sometimes, to refresh the hosts file, a reboot is required. If you think your changes haven't been applied, either reboot or follow [this guide](https://github.com/StevenBlack/hosts#reloading-hosts-file).

## Inspiration:

Swiftblock is inspired from [Adaway](https://adaway.org) and uses some UX concepts from it[No code from the project has been taken,however].

## For Contributors:

* I've used qt-designer to create all the GUI interfaces,kindly use the same/another compatible designer for making any modifications in GUI. All the ui files are in `swift_block/ui`
* `swift_block/__init__.py` is the entry point/script executed to initialise everything
* `swift_block/main.py` is the home page of swift-block - it offers users options to manage their hosts sources,update source files, enable/disable or uninstall swift-block, etc.
* `swift_block/Parser.py` is the heart of swift-block, with low level functions for performing operations on hosts files and sources,first-start,restoring/replacing corrupt files,validation tasks,uninstall scripts, etc.[It is a non-GUI module]
* `swift_block/RuleManager.py` is the GUI rule editor. It offers users options to block/redirect/allow custom/specific hostnames and also allow or redirect the hostnames being blocked by the source files
* Images and icons used within the GUI are stored in the `swift_block/assets` directory.
* `swift_block/elevate` is a sub-package that provides privilege escalation functionality(Required to read/write to the system hosts file). It is my modification of the original and currently broken [elevate](https://github.com/barneygale/elevate).

### Attribution:
* [Tattoo machine icons created by Smashicons - Flaticon](https://www.flaticon.com/free-icons/tattoo-machine)
* [Uninstall icons created by Us and Up - Flaticon](https://www.flaticon.com/free-icons/uninstall)

<hr />
Made with ❤️ by Xploreinfinity ✧･ﾟ: ✧･ﾟ: :･ﾟ✧:･ﾟ✧ 
