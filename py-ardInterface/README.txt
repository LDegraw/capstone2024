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

Commands For Arduino:
1. Go to the search bar
2. Write >Arduino:
3. A list should appear, you should set your port, and type of board.
4. You should now be able to write >Arduino: UploadCLI which flashes the arduino