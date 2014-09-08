#!/usr/bin/python

import os.path
import sys
from subprocess import check_output, call

device_id = sys.argv[1]
app_id = sys.argv[2]

def is_device_running(device_id):
	result = check_output(['xcrun', 'simctl', 'list'])

	for line in result.split('\n'):
		if device_id in line:
			print line
			if "Booted" in line:
				return True
	return False

shouldRun = not is_device_running(device_id)
canUninstall = True

# only boot sim if it's not already
if shouldRun:
	print 'Booting device'
	result = call(['xcrun', 'simctl', 'boot', device_id])
	if result != 0:
		print "Failed to boot simulator: %s" % (device_id)
		canUninstall = False
	else:
		print 'Booted'

# uninstall app
if canUninstall:
	print ' '.join(['xcrun', 'simctl', 'uninstall', device_id, app_id])
	result = call(['xcrun', 'simctl', 'uninstall', device_id, app_id])
	if result != 0:
		print "Failed to uninstall app: %s" % (app_id)
	else:
		print 'Success'

# shutdown if we had to boot it
if shouldRun:
	result = call(['xcrun', 'simctl', 'shutdown', device_id])
	if result != 0:
		print "Failed to shutdown simulator: %s" % (device_id)
