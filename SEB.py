#!/usr/bin/python

import sys, os, subprocess

#Hello reader, getting a few pills of aspirin before reading this is recommended, proceed at your own risk :)
#Unix systems only
#Requirements: 3 virgins, a goat, Python2, Nasm, Ndisasm, Perl, Ld, Objdump, Grep, Sed, Cut (most should be available for most Unix systems)
#Author(more like reason behind future mass-suicides): Obsrv_
print "*********************************************\n"
print "   SHELLCODE-RELATED EYE BLEEDER 300000000   \n"
print "*********************************************\n"

def getFilename():
    global filename
    global filenameobj
    global filenamenasm
    #Get filename preferably without stabbing yourself
    filename = raw_input('\nFilename to write to[defaults to shellobjdmpstr_tmp, !!WILL GET DELETED AFTERWARDS IF EXSISTS!!]: ')
    #Declare temporary files
    if(len(filename) < 1):
        filename = 'shellobjdmpstr_tmp'
        filenameobj = filename + ".o"
        filenamenasm = filename + ".nasm"
        print "\nUsing default filename\n"
    else:
        filename = filename
        filenameobj = filename + ".o"
        filenamenasm = filename + ".nasm"
        
def checkAndPad(str1):
    #Check if string is divisable by 8
    while((len(str1) % 8) != 0):
        #If it's not, add dashes in front of it till it does >:)
        str1 = "/" + str1
    return str1

def NDisasmOutput(inputfile):
    #Temporary files
    file1 = open(inputfile, 'rw')
    file2 = open(inputfile + "_", 'wb')
    asms = ''
    #Read lines from file1 and grab only the instructions while maintaining readable format
    for line in file1:
        line = line.split()
        line[0] = ''
        line[1] = ''
        try:
            asms += "\t" + line[2] + " " + line[3] + " " + line [4] + "\n"
        except:
            try:
                asms += "\t" + line[2] + " " + line[3] + "\n"
            except:
                try:
                    asms += "\t" + line[2] + "\n"
                except:
                    #I don't even
                    print "IDK WHAT'S HAPPENING GET OUT IT'S GONNA BLOW!!!"
    file1.close()
    #Make a template in file2
    file2.write('global _start\n\n')
    file2.write('section .text\n\n')
    file2.write('_start:\n')
    #Add the grabbed instructions to file2
    file2.write(asms)
    file2.close()

def runShellcode():
    #Link and run
    subprocess.call("ld -m elf_i386 -o" + filename + " " + filenameobj, shell=True)
    subprocess.call("./" + filename, shell=True)

def testShellCode():
    filename = 'shellTest_tmp'
    #Put shellcode in a file for ndisasm to read
    subprocess.call("perl -e 'print " + '"' + commInput + '"' + "'" + " > " + filename, shell=True)
    #Read from file
    output = subprocess.check_output("ndisasm -b 32" + " " + filename, shell=True)
    #Write output to a temporary file
    file2 = open(filename, 'wb')
    file2.write(output)
    file2.close()
    #Recognise instructions and write them to a temporary file
    NDisasmOutput(filename)
    #TEMPORARY FILES AAAAAAAAAAAAAAAH
    filenameobj = filename + ".o"
    filename_ = filename + "_"
    #Compile and assemble
    subprocess.call("nasm -f elf32 -o " + filenameobj + " " + filename_, shell=True)
    subprocess.call("ld -m elf_i386 -o" + filename + " " + filenameobj, shell=True)
    #Run
    subprocess.call("./" + filename, shell=True)
    #Clean up
    print "\n\nCleaning up..."
    subprocess.call("rm " + filename + " " + filenameobj + " " + filename_, shell=True)
    
def CommToShell(command):
    #set up skeleton
    shellstr = ''
    shellstr += 'global _start\n\n'
    shellstr += 'section .text\n\n'
    shellstr += '_start:\n\n'
    shellstr += '\txor eax,eax\n'
    shellstr += '\tpush eax\n'
    #Add padding, encode and reverse string
    com = checkAndPad(command)
    com = com.split()
    comPush = checkAndPad(com[0])[::-1].encode('hex')
    #split by 8 for proper PUSHes
    comPush = [comPush[i: i + 8] for i in range(0, len(comPush), 8)]
    for i in range(0, len(comPush)):
        shellstr += '\tpush ' + "0x" + comPush[i] + "\n"
    #finalize skeleton
    shellstr += '\tmov ebx, esp\n'
    shellstr += '\tpush eax\n'
    shellstr += '\tmov edx, esp\n'
    #Use as many args as needed (iteration starts from 1 so program name is skipped and only following agruments are gathered)
    for i in range(1, len(com)):
        shellstr += '\tpush ' + 'arg' + str(i) + "\n"
    shellstr += '\tpush ebx\n'
    shellstr += '\tmov ecx, esp\n'
    shellstr += '\tmov al, 0xb\n'
    shellstr += '\tint 0x80\n'
    shellstr += '\n\nsection .data\n'
    #Define as many args as needed (identical reason to start iteration from 1)
    for i in range(1, len(com)):
        shellstr += '\targ' + str(i) + ' DB ' + "'" + com[i] + "'\n"
    #Write to file
    file1 = open(filenamenasm, 'wb')
    file1.write(shellstr)
    file1.close()
    #Compile temporary obj file to grep shellcode from
    p = subprocess.call("nasm -f elf32 -o" + " " + filenameobj + " " + filenamenasm, shell=True)
    #Grep shellcode using objdump
    print "Shellcode:\n"
    cmd = "objdump -D " + filenameobj + "|grep '[0-9a-f]:'|grep -v 'file'|cut -f2 -d:|cut -f1-6 -d' '|tr "
    cmd += "-s ' '|tr '\t' ' '|sed 's/ "
    cmd += "$//g'|sed 's/ /\\\\x/g'|paste -d '' -s |sed 's/^/" + '"' + "/'|sed 's/$/" + '"' + "/g'"
    #Call command
    output = subprocess.check_output(cmd, shell=True)
    print output
    runOpt = raw_input("\nDo you want to run the shellcode now?[y/N]: ")
    if(runOpt.upper() == 'Y'):
        print "\nRunning shellcode...\n" + stars + "\n\n"
        runShellcode()
        #Clean up
        print stars + "\n"
        print "\n\nCleaning up..."
        subprocess.call("rm " + filename + " " + filenameobj + " " + filenamenasm, shell=True)
    else:
        #Clean up
        print stars + "\n"
        print "\n\nCleaning up..."
        subprocess.call("rm " + filename + " " + filenameobj + " " + filenamenasm, shell=True)
        sys.exit(0)
    
    
#Start of program
#Get terminal size for stars padding
rows, columns = subprocess.check_output(['stty', 'size']).split()
stars = "*" * (int(rows) * 3 + int(rows)/2 - 2)
usrC = raw_input("[1] Linux Command --> Shellcode (Execve method)\n[2] Test Shellcode\n\nChoice: ")

if(int(usrC) != 1) and (int(usrC) != 2):
    print "\n[-] Invalid choice"
    sys.exit(1)
else:
    if(int(usrC) == 1):
        commInput = raw_input('\nCommand to convert[Must be present in "/bin/"]: ')
        commModified = "/bin/" + commInput
        getFilename()
        CommToShell(commModified)
    else:
        commInput = raw_input('\nShellcode to test: ')
        testShellCode()
