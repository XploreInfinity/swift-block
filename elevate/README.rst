Elevate: Request root privileges
================================

Elevate is a small Python library that re-launches the current process with
root/admin privileges using one of the following mechanisms:

- UAC (Windows)
- AppleScript (macOS)
- ``pkexec``, ``gksudo`` or ``kdesudo`` (Linux)
- ``sudo`` (Linux, macOS)

Added to this project for privilege elevation until I come up with a custom solution
