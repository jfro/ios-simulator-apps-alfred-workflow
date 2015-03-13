#!/usr/bin/python

import os.path
import sys
from subprocess import check_output, call
import re

device_id = sys.argv[1]

device_name = "Unknown"

def is_device_running(device_id):
	result = check_output(['xcrun', 'simctl', 'list'])
	name = None
	for line in result.split('\n'):
		m = re.search("(\s+)(.*)\s\(([\d\w]{8}-[\w\d]{4}-[\w\d]{4}-[\w\d]{4}-[\w\d]{12})\)\s+\((\w+)\)(\s+\((unavailable).*)?", line)
		if m:
			device_id_check = m.group(3)
			if device_id == device_id_check:
				name = m.group(2)
				device_id_check = m.group(3)
				device_status = m.group(4)
				if "Booted" == device_status:
					return True, name
	return False, name

isRunning, device_name = is_device_running(device_id)

# uninstall app
if not isRunning:
	result = call(['xcrun', 'simctl', 'erase', device_id])
	if result != 0:
		print "Failed to erase device: %s" % (device_name)
	else:
		print 'Erased %s' % (device_name)
else:
	print "Can't erase %s, already booted" % (device_name)
