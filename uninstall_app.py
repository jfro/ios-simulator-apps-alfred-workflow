#!/usr/bin/python

import os.path
import sys
from subprocess import check_output, call
from simctl import SimControl

device_id = sys.argv[1]
app_id = sys.argv[2]

simctl = SimControl()
devices = simctl.deviceLookupHash()

device = devices[device_id]

shouldRun = not device.isBooted()
canUninstall = True

# only boot sim if it's not already
if shouldRun:
	print 'Booting device'
	result = simctl.bootDevice(device)
	if not result:
		print "Failed to boot simulator: %s" % (device_id)
		canUninstall = False

# uninstall app
if canUninstall:
	result = simctl.uninstallApp(device, app_id)
	if result != True:
		print "Failed to uninstall app: %s" % (app_id)
	else:
		print 'Successfully uninstalled %s' % (app_id)

# shutdown if we had to boot it
if shouldRun:
	result = simctl.shutdownDevice(device)
	if result != True:
		print "Failed to shutdown simulator: %s" % (device_id)
