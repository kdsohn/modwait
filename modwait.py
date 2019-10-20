#!/usr/bin/python3
# Version 1.0 
# 18.10.2019
# Author Klaus-Dieter Sohn
#
# inserts wait time comands G4 into gcode to achieve a minumum layer title
# default min Layertime is 90 seconds, can be overriden with a startcode, i.e. ";minLayerTime,120"
# default waitingposition is x+20 y+20 z+5 F1000
# for S3D layer start is detected by the beginning withof prime tower (recommended size 12 x 12 mm)
# for Prusaslicer layer start is detected by "AFTER_LAYER_CHANGE". If not preset, add this comment to custom code after layer change
# Wait is applied to the first object in layer, so you way want to add a waist object (i.e. cylinder with 12 mm diameter) to catch the ooze
# layer print time is calculatet from G1 codes
# calling without parameters will use stdin and stdout, so script my be used for piping
# first parameter is input file, second parameter is output file
# if second parameter is omitted, output name is input name appended by "_w"
# A summary is printed to stdout at end of script. By using as pipe the summary will be appended to the destination

import fileinput
import sys
import math

class delaylayer:
    minlayertime = 90
    waitoffset = "dl.x-20,dl.y+20,dl.z+5,1000"
    doit_prusa = False
    doit_s3d = False
    layertime = 0
    maxlayertime = 90
    printtime = 0
    first = True
    x = 0
    y = 0
    z = 0
    f = 1
    alt_x = 0
    alt_y = 0
    alt_z = 0
    
    def print_delay(dl,fo):
        dl.doit_prusa = False
        dl.doit_s3d = False
        x = int(dl.minlayertime - dl.layertime)
        if (x > 0):
            if not dl.first:
                exec("fo.write(\"G1 X%.3f Y%.3f Z%.3f F%d\\n\" %(" + dl.waitoffset + "))")
                fo.write("G4 S%d\n" %(x))
                fo.write("G1 Z%.3f\n" %(dl.z))
                fo.write("G1 X%.3f Y%.3f\n" %(dl.x,dl.y))
                dl.printtime += dl.minlayertime
        else:
            fo.write(";Layertime: %d\n" %(dl.layertime))
            if dl.layertime > dl.maxlayertime:
                dl.maxlayertime = dl.layertime
            dl.printtime += dl.layertime
        dl.layertime = 0
        dl.first = False

        
    def process_line(dl,line,fo):
    #    print(line,line.find('M106'))

        fo.write(line)
        line = line.upper()    

        if line.find('G28') != -1:
            dl.x = 0
            dl.y = 0
            dl.z = 0

        if line.find('G1') == 0:
    #        print("Line",line)
            if line.find(';') != -1:
                line1,comment = line.split(";",1);
            else:
                line1 = line
            line1 = line1.upper()    
            args = line1.split()
            for arg in args:
    #            print("Arg",arg)
                s1,s2,val = arg.partition('X')
                if s2 == 'X':
                    dl.x = float(val)
                s1,s2,val = arg.partition('Y')
                if s2 == 'Y':
                    dl.y = float(val)
                s1,s2,val = arg.partition('Z')
                if s2 == 'Z':
                    dl.z = float(val)
                s1,s2,val = arg.partition('F')
                if s2 == 'F':
                    dl.f = float(val) / 60
            distance = math.sqrt(math.pow(dl.x-dl.alt_x,2)+math.pow(dl.y-dl.alt_y,2)+math.pow(dl.z-dl.alt_z,2))
            dl.layertime += distance / dl.f 
            dl.alt_x = dl.x
            dl.alt_y = dl.y
            dl.alt_z = dl.z
            if dl.doit_prusa:
                dl.print_delay(fo)

        if line.find('MINLAYERTIME') in(1,2):
            s1,s2,x = line.rpartition(',');
            dl.minlayertime = float(x)
            dl.maxlayertime = dl.minlayertime

        if line.find('FEATURE PRIME PILLAR') != -1: # S3D mit Prime Pillar
            dl.doit_s3d = True	
        if line.find('AFTER_LAYER_CHANGE') != -1:   # Prusa entry after layer change
            dl.doit_prusa = True		

        if line.find('G92') != -1 and dl.doit_s3d == 1:
            dl.print_delay(fo)


def main():	
    dl = delaylayer()
    if len(sys.argv) < 2:
        fi = sys.stdin
        fo = sys.stdout
    else:
        filein = sys.argv[1];
        fi = open(filein,"r")
        if len(sys.argv) < 3:
            s1,s2,s3 = filein.rpartition('.')
            fileout = s1 + "-w" + s2 + s3
        else:
            fileout = sys.argv[2];
        fo = open(fileout,"w")
        
        
    for line in fi:
        dl.process_line(line,fo)
    print("; Min layer time",int(dl.minlayertime),"seconds")
    print("; Print time",int(dl.printtime/60), "minutes =",float(dl.printtime/3600),"hours")
    print("; Max layer time",int(dl.maxlayertime),"seconds")
    fi.close()
    fo.close()
  
main()