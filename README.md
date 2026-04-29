# 298-Asl
Final Project for E298(002). An ASL interpreter.
Requires python 3.11 for tensorflow version

TO RUN:

(Create virtual enviroment) py -3.11 -m venv env

(Activate enviroment) On windows: env\Scripts\activate

(Install requirements) pip install -r requirements.txt

(Run project) python live_demo.py

When ran the project will be in real-time mode and will periodically read a frame from the green box 
and attempt to interpret the symbol.

To switch to capture mode, where you can choose when it reads a frame, press C.
After this it will read a frame with every C press.

To switch back to real-time mode, press R.

To close the program, press ESC. 

(*NOTE clicking the right corner X does not stop the program and the window will reappear. 
You must press ESC to close.)
