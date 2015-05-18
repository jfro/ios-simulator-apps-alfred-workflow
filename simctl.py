import os
from glob import glob
import re
from subprocess import check_output, CalledProcessError, STDOUT, call

XCODES = glob("/Applications/Xcode*.app")
# Contents/Developer/Applications/iOS\ Simulator.app

class SimDevice(object):
	def __init__(self, info):
		self.updateWithInfo(info)
		self.info = info
	def updateWithInfo(self, info):
		self.deviceId = info['id']
		self.name = info['name']
		self.state = info['state']
		self.version = info['version']
	def isBooted(self):
		if self.state == 'Booted':
			return True
		return False
	def addXcrun(self, xcrun):
		self.info['xcruns'].append(xcrun)
	def addXcode(self, xcode):
		self.info['xcodes'].append(xcode)
	def getXcrun(self, xcrunIndex=0):
		return self.info['xcruns'][xcrunIndex]

class SimControl(object):
	def __init__(self):
		self.devices = {}
		pass

	def bootDevice(self, device):
		result = call([device.getXcrun(), 'simctl', 'boot', device.deviceId])
		if result != 0:
			return False
		return True
	def shutdownDevice(self, device):
		result = call([device.getXcrun(), 'simctl', 'shutdown', device.deviceId])
		if result != 0:
			return False
		return True
	def uninstallApp(self, device, app_id):
		result = call([device.getXcrun(), 'simctl', 'uninstall', device.deviceId, app_id])
		if result != 0:
			print "Failed to uninstall app: %s" % (app_id)
			return False
		return True

	def deviceLookupHash(self):
		self.loadDevices()
		return self.devices

	def loadDevices(self):
		for xcode in XCODES:
			xcrun = os.path.join(xcode, 'Contents/Developer/usr/bin/xcrun')
			result = check_output([xcrun, 'simctl', 'list', 'devices'])
			lines = re.split("\n+", result)
			currentOS = ''
			for line in lines:
				osMatch = re.search("--\s+(iOS\s+\d+\.\d+)\s+--", line)
				if osMatch:
					currentOS = osMatch.group(1)
					continue

				m = re.search("(\s+)(.*)\s\(([\d\w]{8}-[\w\d]{4}-[\w\d]{4}-[\w\d]{4}-[\w\d]{12})\)\s+\((\w+)\)(\s+\((unavailable).*)?", line)
				if m:
					name = m.group(2)
					deviceID = m.group(3)
					state = m.group(4)
					unavailable = True if m.group(6) else False
					if unavailable:
						continue

					info = {'name': name,
						'id': deviceID,
						'state': state,
						'unavailable': unavailable,
						'xcruns': [xcrun],
						'xcodes': [os.path.basename(xcode)],
						'version': currentOS}

					if self.devices.has_key(deviceID):
						device = self.devices[deviceID]
						device.addXcrun(xcrun)
						device.addXcode(xcode)
					else:
						device = SimDevice(info)
						self.devices[deviceID] = device

	def activeDevices(self):
		self.loadDevices()
		return self.devices.values()

if __name__ == '__main__':
	sim = SimControl()
	print sim.activeDevices()
