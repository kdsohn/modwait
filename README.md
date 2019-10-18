# modwait
Python Script to add wait time for printing small parts

inserts wait time comands G4 into gcode to achieve a minumum layer title
default min Layertime is 90 seconds, can be overriden with a startcode, i.e. ";minLaerTime,120"
default waitingposition is x+20, y+20 z+5, can be overriden with a startcode, i.e. ";waitoffset,G27"
for S3D layer start is detected by the beginning withof prime tower (recommended size 12 x 12 mm)
for Prusaslicer layer start is detected by "AFTER_LAYER_CHANGE". If not preset, add this comment to custom code after layer change
layer print time is calculatet from G1 codes
calling without parameters will use stdin and stdout, so script my be used for piping
first parameter is input file, second parameter is output file
if second parameter is omitted, output name is input name appended by "_w"
A summary is printed to stdout at end of script. By using as pipe the summary will be appended to the destination

