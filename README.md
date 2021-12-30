# TimingManager - CS50x Final Project

#### Video Demo: https://youtu.be/9hAO2zduxBs

#### Description:
This is an application that tracks how much time a computer is being used or sitting idle.
An SQLite database is used to record the data, after which it can be plotted into the application's GUI directly or exported into an Excel file for further analysis.
Two calendars can be used to select a start and end date to be used when plotting the data in the GUI or when exporting to an Excel file.
Warning messages are displayed if the user inputs cannot be plotted correctly or when no file name is given for the Excel file. Additional notifications are displayed when starting or
stopping TimingManager from the `Start Recording` and `StopRecording` buttons.

Because I wanted to be able to check if `TimingManager` was currently running on the system or not, I needed to have an executable file running (so this is why pyinstaller was used). Because of this, this program
is designed for Windows only. The graphics user interface was designed with Qt5 and then Python was used to connect the GUI to the relevant functions that needed to be ran. The GUI was split into two files because it is
easier to maintain, and allows for code separation between starting/stopping the recording of user status, as well as visualizing or analyzing when the computer was used. An SQLite database was used here because it
allows for easier expansion later (for example, the database could be only show relevant information for the current user that is logged in). Another reason why I chose to use SQLite is because of the built-in SQL
functions relating to date and time, allowing me to easily extract relevant information from the database.


`requirements.txt`: Contains all the dependencies needed to run the project
`.gitignore`: Contains all files to be excluded from github.
`clock.png`: An icon to be used for the GUI (and that also shows up in the Windows Taskbar)
`test.xlsx`: An Excel file which contains data exported from the SQLite Database
`TimingManager_config.py`: A configuration file that has some variables defined which are imported into other scripts. These include program name, program path, database path, etc.
`TimingManager.py`: A python script which records if a user is active or not. Reads in information from the `TimingManager_config.py` that determines how often to check if a user is active or not (using the Windows API for Python).
`TimingManager.exe`: An executable of `TimingManager.py`, compiled with `pyinstaller` for Windows. This allows the script to show up with the correct name in the Windows Task Manager.
`TimingManager_GUI.py`: Python code that implements the GUI logic and connects buttons to their relevant functions/methods.
`TimingManager_plotter.py`: Python code that implements the logic for plotting the bar charts which display information for computer usage.
`TimingManager.ui`: Qt5 file produced using QtDesigner which controls how the GUI looks like, as well as containing information about button and other widget names.
`TimingManager_plotter.ui`: Qt5 file produced using QtDesigner which controls how the plotting GUI looks like.
