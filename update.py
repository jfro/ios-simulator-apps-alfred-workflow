#!/usr/bin/python
# encoding: utf-8


from workflow import Workflow
from os.path import expanduser, join, dirname, basename, isfile
import glob
from subprocess import check_output, CalledProcessError, STDOUT
import re

HOME = expanduser("~")
SIM_DIR = join(HOME, "Library/Application\ Support/iPhone\ Simulator/7.1/Applications/*/*.app")
SIM_DIR6 = join(HOME, "Library/Developer/CoreSimulator/Devices/*/data/Containers")
SIM_DIRAPP_SEARCH = join(SIM_DIR6, 'Bundle/Application/*/*.app')

def get_plist_key(path, key):
    try:
        result = check_output(['/usr/libexec/PlistBuddy', '-c', ("Print :%s" % (key)), path], stderr=STDOUT)
        return result.strip()
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

def get_sim6_items(data_paths, devices_info):
    appPaths = []
    for file in glob.glob(SIM_DIRAPP_SEARCH):
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
            'device': devices_info[deviceId],
            'icon': get_app_icon(file)
        }
        appPaths.append(appInfo)
    return appPaths


def main(wf):
    data_paths = get_sim6_data_paths()
    devices_info = get_device_infos()
    def get_items():
        return get_sim6_items(data_paths, devices_info)
    apps = wf.cached_data('sim6_items', get_items, max_age=600)
    # Record our progress in the log file
    wf.logger.debug('{} Apps cached'.format(len(apps)))

if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
