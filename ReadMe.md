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