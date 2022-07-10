'''
Copyright (C) 2021 xploreinfinity

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

import sys
from PyQt6 import QtWidgets
from swift_block import main,elevate
def start():
    #*Privilege escalation:
    elevate.elevate(__file__)
    #*WINDOWS ONLY: WindowIcon doesn't reflect the icon on the taskbar. To fix this, add a registry key to tell windows pythonw is just a host rather than an application on its own:
    #*https://stackoverflow.com/a/1552105
    if sys.platform.startswith("win32"):
        import ctypes
        #*App id can be any arbitrary unicode string:
        appid = u'org.xinfi.swiftblock'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    app=QtWidgets.QApplication(sys.argv)
    ui=main.Ui()
    sys.exit(app.exec())
start()
