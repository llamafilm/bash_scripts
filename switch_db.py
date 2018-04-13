#!/usr/bin/python

# Run as normal user, so that renderqueue will be loaded properly

import sys
import os
import getpass
import subprocess
import socket
import fileinput
import re
import xml.etree.ElementTree as ET

def switchXML(the_file):
	tree = ET.parse(the_file)
	root = tree.getroot()
	for key in root.iter('DatabaseServer'):
		old_value = key.text
		key.text = db_server
	tree.write(the_file)
	print("Changed " + old_value + " to " + key.text + " in " + the_file)

def runDarwin(): #a.k.a. macOS
	#################################################
	switchXML('/Applications/OSD2017/startup.xml')
	switchXML('/Applications/OSD2017/render/config/startup.xml')
	switchXML('/Applications/OSD2017/render/config/startup_template.xml')
	#################################################
	plist = '/Library/LaunchDaemons/com.colorfront.osd.renderqueue.plist'
		
	temp_plist = '/tmp/switch_db.plist'
	if not os.path.isfile(plist): # in case ExD was installed last
		plist = '/Library/LaunchDaemons/com.colorfront.exd.renderqueue.plist'
	print("Unloading " + plist + "...")
	subprocess.call(["launchctl", "unload", plist])
	tree = ET.parse(plist)
	root = tree.getroot()

	# edit the line following "-h"
	h_found = False
	for key in root.iter():
		if key.text == "-h":
			h_found = True
		elif h_found:
			old_value = key.text
			key.text = db_server
			break
	with open(temp_plist, 'wb') as f:
		xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
		f.write(xml_header.encode())
		tree.write(f)
	subprocess.call(["sudo", "cp", "-f", temp_plist, plist])
	print("Changed " + old_value + " to " + key.text + " in " + plist)
	print("Reloading " + plist + "...")
	subprocess.call(["launchctl", "load", plist])
	os.remove(temp_plist)
	print("Complete.")

def runWin32():
	#################################################
	switchXML('C:/Program Files/OSD2017/startup.xml')
	switchXML('C:/Program Files/OSD2017/render/config/startup.xml')
	switchXML('C:/Program Files/OSD2017/render/config/startup_template.xml')
	#################################################

	ini_file = 'C:/Program Files/OSD2017/render/bin/MonitorService.ini'
#	os.system('taskkill /im renderqueue.exe')
#	os.system('taskkill /im rendertray.exe')
	with fileinput.input(ini_file, inplace = True) as f:
		for line in f:
			if(line.startswith('CommandLine')):
				# RegEx match word characters and dots after -h
				print(re.sub('-h [\w.]+', '-h ' + db_server, line), end='')
				old_value = line.split('-h ')[1].split(' -')[0]
			else:
				print(line, end='')
	print("Changed " + old_value + " to " + db_server + " in " + ini_file)
#	print("Restarting render tray...")
#	subprocess.Popen('C:/Program Files/OSD2017/render/bin/rendertray.exe')
	

# check if an argument is passed
if (len(sys.argv) < 2):
    print("Error! Must enter IP address as argument.")
    print("Exiting with no changes...")
    sys.exit()
db_server = str(sys.argv[1]) # first argument from command-line
#db_server = raw_input("Enter IP address:")

# validate IP address
try:
	socket.inet_aton(db_server)
except socket.error:
	print("Error! Must specify IP address like 127.0.0.1")
	sys.exit()

# run correct method for OS
if sys.platform == "darwin":
	runDarwin()
elif sys.platform == "win32":
	runWin32()
else:
	print("This platform is not supported: " + sys.platform)
