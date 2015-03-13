import os
from glob import glob
import re
from subprocess import check_output, CalledProcessError, STDOUT

XCODES = glob("/Applications/Xcode*.app")
# Contents/Developer/Applications/iOS\ Simulator.app

class SimControl(object):
	def __init__(self):
		self.devices = {}
		pass

	def activeDevices(self):
		for xcode in XCODES:
			xcrun = os.path.join(xcode, 'Contents/Developer/usr/bin/xcrun')
			result = check_output([xcrun, 'simctl', 'list'])
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
						info = self.devices[deviceID]
						info['xcruns'].append(xcrun)
						info['xcodes'].append(os.path.basename(xcode))
					else:
						self.devices[deviceID] = info

		return self.devices.values()

if __name__ == '__main__':
	sim = SimControl()
	print sim.activeDevices()
