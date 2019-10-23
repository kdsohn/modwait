#!/usr/bin/python3
# Version 1.0 
# 18.10.2019
# Author Klaus-Dieter Sohn
# Repository: https://github.com/kdsohn/modwait
# Description: https://github.com/kdsohn/modwait/blob/master/README.md

import fileinput
import sys
import math

class delaylayer:
    minlayertime = 90
#    waitoffset1 = "dl.z+5,1000"
#    waitoffset2 = "dl.x-20, dl.y+20, dl.z+5"
    waitoffset2 = "dl.x-20, dl.y+20"
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
    total_wait = 0
    mylines = []
    
    def print_delay(dl):
        dl.doit_prusa = False
        dl.doit_s3d = False
        x = int(dl.minlayertime - dl.layertime)
        if (x > 0):
            if not dl.first:
#                exec("fo.write(\"G1 X%.3f Y%.3f Z%.3f\\n\" %(" + dl.waitoffset2 + "))")
                exec("dl.mylines.append(\"G1 X%.3f Y%.3f\\n\" %(" + dl.waitoffset2 + "))")
                dl.total_wait += x
                dl.mylines.append("G4 S%d\n" %(x))
#                fo.write("G1 X%.3f Y%.3f Z%.3f\n" %(dl.x,dl.y,dl.z))
                dl.mylines.append("G1 X%.3f Y%.3f\n" %(dl.x,dl.y))
                dl.printtime += dl.minlayertime
        else:
            dl.mylines.append(";Layertime: %d\n" %(dl.layertime))
            if dl.layertime > dl.maxlayertime:
                dl.maxlayertime = dl.layertime
            dl.printtime += dl.layertime
        dl.layertime = 0
        dl.first = False

        
    def process_line_1(dl,line):
    #    print(line,line.find('M106'))

        line_ori = line
        line = line.upper()    

        if line.find('G28') != -1:
            dl.x = 0
            dl.y = 0
            dl.z = 0

        if line.find('G1 E0.0000') != -1 and dl.doit_s3d == 1:
            dl.print_delay()

        dl.mylines.append(line_ori)

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
                dl.print_delay()

        if line.find('MINLAYERTIME') in(1,2):
            s1,s2,x = line.rpartition(',');
            dl.minlayertime = float(x)
            dl.maxlayertime = dl.minlayertime

        if line.find('FEATURE PRIME PILLAR') != -1: # S3D mit Prime Pillar
            dl.doit_s3d = True	
        if line.find('AFTER_LAYER_CHANGE') != -1:   # Prusa entry after layer change
            dl.doit_prusa = True		

    def process_line_2(dl,line,fo):
        line_ori = line
        line = line.upper()    
        if line.find('M73') == 0:
            line_ori = ""
            if line.find(';') != -1:
                line1,comment = line.split(";",1);
            else:
                comment = ""
                line1 = line
            args = line1.split()
            for arg in args:
    #            print("Arg",arg)
                s1,s2,val = arg.partition('R')
                if s2 == 'R':
                    R = float(val)
                    arg = "R%d" % (R + dl.total_wait / 60)
                s1,s2,val = arg.partition('S')
                if s2 == 'S':
                    S = float(val)
                    arg = "S%d" % (S + dl.total_wait / 60)
                line_ori += arg + " "
            if comment != "":
                line_ori += ";" + comment
            line_ori = line_ori.rstrip() + "\n"
            fo.write(line_ori)
            return
            
        if line.find('G4') == 0:
            if line.find(';') != -1:
                line1,comment = line.split(";",1);
            else:
                line1 = line
            args = line1.split()
            for arg in args:
    #            print("Arg",arg)
                s1,s2,val = arg.partition('S')
                if s2 == 'S':
                    dl.total_wait -= float(val)
        fo.write(line_ori)

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
        dl.process_line_1(line)
        
    for line in dl.mylines:
        dl.process_line_2(line,fo)
        
    print("; Min layer time",int(dl.minlayertime),"seconds")
    print("; Print time",int(dl.printtime/60), "minutes =",float(dl.printtime/3600),"hours")
    print("; Max layer time",int(dl.maxlayertime),"seconds")
    fi.close()
    fo.close()
  
main()