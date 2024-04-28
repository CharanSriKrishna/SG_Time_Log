## Steps to be followed to setup the Time Log 

- Create a time log custom entity ( customentity07 ) 
- Create field in task with custom time log entity as multi entity field 
- In the time log page add a start time , end time, total time, productive time fields in the time log page and arrange the fields for easy use 
- Edit the task page so the time log is visible from within the task 

## Now four are three things that are things modified 

- new hook time log 
- update the hook in info.yml 
- called the hook in the scene operations.py file in python>tk_multi_workfiles
- added the pynput library

## How This works 

- Every time when a new file or file open is clicked through the DCC then a new time log entry is created
- When file save or CTRL + S is pressed the time log is updated (make sure you save file before publishing) 
- This works based on two conditions active window and mouse and keyboard movements 
- One use case where it doesnt work is when two tasks are opened at the same time on the same tool ( eg task A and task B are opened using Maya )