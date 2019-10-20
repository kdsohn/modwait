# modwait
Python Script to add wait time for printing small parts

Version 1.0 
18.10.2019
Author Klaus-Dieter Sohn
Repository: https://github.com/kdsohn/modwait

inserts wait time comands G4 into gcode to achieve a minumum layer title
default min Layertime is 90 seconds, can be overriden with a startcode, i.e. ";minLayerTime,120"
default waitingposition is x+20 y+20 z+5 F1000, 
please leave room for this move or change position
it is essential, that the waste tower is located between the real object and the waiting position, otherwise it will not catch te ooze
for S3D layer start is detected by the beginning withof prime tower (recommended size 12 x 12 mm)
for Prusaslicer layer start is detected by "AFTER_LAYER_CHANGE". If not preset, add this comment to custom code after layer change
Wait is applied to the first object in layer, so you way want to add a waist object (i.e. cylinder with 12 mm diameter) to catch the ooze
layer print time is calculatet from G1 codes

# Usage
Calling without parameters will use stdin and stdout, so script may be used for piping
First parameter is input file, second parameter is output file
If second parameter is omitted, output name is input name appended by "_w"
A summary is printed to stdout at end of script. By using as pipe the summary will be appended to the destination
