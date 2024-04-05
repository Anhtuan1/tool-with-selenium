# tool-with-selenium

##bash

`pip install -r requirements.txt`

**Brief description of your project.**

Building the Executable
To build your Python project into an executable (.exe) file, follow these steps:

_Install PyInstaller:_

`pip install pyinstaller`

_Navigate to Your Project Directory:_

`cd /path/to/your/project`

_Build the Executable:_

`pyinstaller --onefile main.py`

or

`pyinstaller --onefile --noconsole main.py`

This command creates a standalone executable file in the dist/ directory.~~~~

Locate the Executable: After the build process is complete, find the standalone executable in the dist/ directory:
~~~~
/path/to/your/project
├── dist/
│   └── main.exe
└── ...
~~~~
Running the Executable To run the executable, simply execute the main.exe file located in the dist/ directory.

Notes If your project has dependencies, the resulting executable may be large. You can explore additional options or alternative tools like cx_Freeze or py2exe for more compact executables.