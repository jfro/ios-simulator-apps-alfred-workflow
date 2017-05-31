import simctl
import sys

url = sys.argv[1]

siminfo = simctl.SimControl()
devices = siminfo.activeDevices()

foundDevice = None
for device in devices:
    if device.isBooted():
        foundDevice = device
        break

if foundDevice:
    if not siminfo.openURL(device, url):
        print("Failed to open URL: %s" % (url))
else:
    print("Failed to find booted device")
