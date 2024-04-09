To use the raspberry pi simply plug in using ethernet cable

Make sure to have visual studio code downloaded

Install Remote Explorer extension
Add an ssh connection by clicking the plus
Add ssh raspberrypi.local
    - This should enable you to access the pi and its documents eaily in visual studio
    - connect to raspberrypi.local
    - password: password

Should now have access to files, Navigate to Desktop/code directory
    - Command - Shift - P to open command or type in search bar '>Arduino:UploadCLI' to upload program to arduino
    - the directory Desktop/code/arduinoControl holds a sketch that can be edited which responds to serial inputs
        - Use this general structure to control using the PY
    - navigate to the Desktop/code directory in the terminal
    - in terminal excecute program by running python3 ardControl.py 

This opens a blank screen in terminal that should take key inputs as follows:
    - UP_KEY     =  U 
    - DOWN_KEY   =  D
    - LEFT_KEY   =  L
    - RIGHT_KEY  =  R
    - ENTER      =  E
    - DELETE     =  F
 
Use CTRL_C to exit out of this screen back to the terminal