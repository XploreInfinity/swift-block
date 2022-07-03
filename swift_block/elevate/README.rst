Elevate: Request root privileges
================================

Elevate is a small Python library that re-launches the current process with
root/admin privileges using one of the following mechanisms:

- UAC (Windows)
- AppleScript (macOS)
- ``pkexec``, ``gksudo`` or ``kdesudo`` (Linux)
- ``sudo``, ``doas`` (Linux, macOS)
