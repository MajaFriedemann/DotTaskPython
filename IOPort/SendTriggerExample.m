%setup at beginning of experiment:
IOPortfolder = 'C:\Users\braincoglab\Documents\MATLAB\IOPort';
addpath(IOPortfolder);
[portobject, portaddress] = OpenIOPort;

triggerlength = 0.005; %send trigger for 5 ms
holdvalue     = 0;
triggervalue  = 222;

io64( portobject, portaddress, triggervalue ); %this sends the trigger
pause(triggerlength);
io64( portobject, portaddress, holdvalue ); %this sets the trigger channel back to 0

%remember to close the port at the end of the script!!!
CloseIOPort;