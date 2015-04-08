#!/usr/bin/python
# encoding: utf-8


#from workflow import Workflow
from os.path import expanduser, join, dirname, basename, isfile, realpath
import glob
from subprocess import check_output, CalledProcessError, STDOUT
import re
import cPickle

HOME = expanduser("~")
SIM_DIR = join(HOME, "Library/Application\ Support/iPhone\ Simulator/7.1/Applications/*/*.app")
SIM_DIR6 = join(HOME, "Library/Developer/CoreSimulator/Devices/*/data/Containers")
SIM_DIRAPP_SEARCH = join(SIM_DIR6, 'Bundle/Application/*/*.app')

class DeviceInfo(object):
    def __init__(self, cachePath):
        self.cacheFilePath = join(cachePath, 'devices.cache')
        self.devices = {}
        self.cacheIsDirty = False
        if isfile(self.cacheFilePath):
            cacheFile = file(self.cacheFilePath)
            cache = cPickle.load(cacheFile)
            if cache:
                self.devices = cache

    def infoForDevice(self, deviceID):
        if deviceID in self.devices:
            return self.devices[deviceID]
        else:
            # no cache yet, read it in
            plist = join(HOME, "Library/Developer/CoreSimulator/Devices/", deviceID, "device.plist")
            if isfile(plist):
                deviceName = get_plist_key(plist, 'name')
                deviceRuntime = get_plist_key(plist, 'runtime')
                deviceRuntime = deviceRuntime.split('.')[-1].split('-')
                deviceRuntime = '%s %s.%s' % (deviceRuntime[0], deviceRuntime[1], deviceRuntime[2])
                result = {'name': deviceName, 'id': deviceID, 'runtime': deviceRuntime}
                self.devices[deviceID] = result
                self.cacheIsDirty = True
                return result
            #else:
            #    print "Device %s missing device.plist: %s" % (deviceID, plist)
        return None
    def updateCache(self):
        if self.cacheIsDirty:
            cacheFile = file(self.cacheFilePath, "w+")
            cPickle.dump(self.devices, cacheFile)


def get_plist_key(path, key):
    try:
        result = check_output(['/usr/libexec/PlistBuddy', '-c', ("Print :%s" % (key)), path], stderr=STDOUT)
        result = result.strip()
        return unicode( result, "utf-8" )
    except CalledProcessError, e:
        pass
    return None

def get_device_id_for_app_path(path):
    m = re.search('CoreSimulator/Devices/([\w\d\-]+)/data', path)
    return m.group(1)

def get_device_infos():
    deviceInfos = {}
    devicePaths = glob.glob(join(HOME, "Library/Developer/CoreSimulator/Devices/*"))
    for devicePath in devicePaths:
        plist = join(devicePath, 'device.plist')
        if not isfile(plist):
            continue
        deviceId = basename(devicePath)
        deviceName = get_plist_key(plist, 'name')
        deviceRuntime = get_plist_key(plist, 'runtime')
        deviceRuntime = deviceRuntime.split('.')[-1].split('-')
        deviceRuntime = '%s %s.%s' % (deviceRuntime[0], deviceRuntime[1], deviceRuntime[2])
        deviceInfos[deviceId] = {'name': deviceName, 'id': deviceId, 'runtime': deviceRuntime}
    return deviceInfos

def get_sim6_data_paths():
    pathLookup = {}
    for file in glob.glob(join(SIM_DIR6, 'Data/Application/*/.com.apple.mobile_container_manager.metadata.plist')):
        appId = get_plist_key(file, 'MCMMetadataIdentifier')
        if appId:
            lookupKey = get_device_id_for_app_path(file) + '-' + appId
            pathLookup[lookupKey] = dirname(file)
    return pathLookup

def get_app_icon(appPath):
    plistPath = join(appPath, 'Info.plist')
    devices = ['', '~ipad', '~iphone']
    for device in devices:
        for x in [2,1,0]:
            key = 'CFBundleIcons%s:CFBundlePrimaryIcon:CFBundleIconFiles:%i' % (device, x)
            icon = get_plist_key(plistPath, key)
            if icon:
                iconPath = join(appPath, icon + '%s.png' % (device))
                if not isfile(iconPath):
                    iconPath = join(appPath, icon + '@2x%s.png' % (device))
                if not isfile(iconPath):
                    iconPath = None
                return iconPath

    return None

def get_sim6_items(data_paths, device_info):
    appPaths = []
    for file in glob.glob(SIM_DIRAPP_SEARCH):
        file = unicode( file, "utf-8" )
        deviceId = get_device_id_for_app_path(file)
        plistPath = join(file, 'Info.plist')
        appId = get_plist_key(plistPath, 'CFBundleIdentifier')
        lookupKey = deviceId + '-' + appId
        if lookupKey in data_paths:
            dataPath = data_paths[lookupKey]
        else:
            dataPath = ''
        appName = get_plist_key(plistPath, 'CFBundleDisplayName')
        if not appName:
            appName = basename(file)
        appInfo = {
            'id': appId,
            'path': file,
            'short_path': basename(file),
            'name': appName,
            'data_path': dataPath,
            'device': device_info.infoForDevice(deviceId),
            'icon': get_app_icon(file)
        }
        appPaths.append(appInfo)
    return appPaths

def getSimAppResults(cachePath):
    data_paths = get_sim6_data_paths()
    #devices_info = get_device_infos()
    device_info = DeviceInfo(cachePath)
    def get_items():
        #wf.logger.debug('Finding apps')
        return get_sim6_items(data_paths, device_info)
    apps = get_sim6_items(data_paths, device_info) #wf.cached_data('sim6_items', get_items, max_age=0)
    device_info.updateCache()
    return apps

def main(wf):
    data_paths = get_sim6_data_paths()
    #devices_info = get_device_infos()
    device_info = DeviceInfo(wf.cachedir)
    def get_items():
        print "What"
        #wf.logger.debug('Finding apps')
        return get_sim6_items(data_paths, device_info)
    apps = get_sim6_items(data_paths, device_info) #wf.cached_data('sim6_items', get_items, max_age=0)
    print "Done: "
    print len(apps)
    device_info.updateCache()
    # Record our progress in the log file
    #wf.logger.debug('{} Apps cached'.format(len(apps)))

if __name__ == '__main__':
    #wf = Workflow()
    #wf.run(main)
    main(None)

