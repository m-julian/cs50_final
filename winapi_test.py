import win32api
from datetime import datetime
from time import sleep

last_input = win32api.GetLastInputInfo()
print(last_input)

sleep(5)

next_input = win32api.GetLastInputInfo()
print(next_input)

if next_input == last_input:
    print("user is not here")