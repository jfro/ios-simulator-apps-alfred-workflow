#!/usr/bin/python
# encoding: utf-8


from workflow import Workflow
from os.path import expanduser, join, dirname, basename
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
    return "Unknown"

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
            pathLookup[appId] = dirname(file)
    return pathLookup

def get_sim6_items(data_paths, devices_info):
    appPaths = []
    for file in glob.glob(SIM_DIRAPP_SEARCH):
        plistPath = join(file, 'Info.plist')
        appId = get_plist_key(plistPath, 'CFBundleIdentifier')
        if appId in data_paths:
            dataPath = data_paths[appId]
        else:
            dataPath = ''

        deviceId = get_device_id_for_app_path(file)
        appInfo = {
            'id': appId,
            'path': file,
            'short_path': basename(file),
            'name': get_plist_key(plistPath, 'CFBundleDisplayName'),
            'data_path': dataPath,
            'device': devices_info[deviceId]
        }
        appPaths.append(appInfo)
    return appPaths


def main(wf):
    data_paths = get_sim6_data_paths()
    devices_info = get_device_infos()
    def get_items():
        return get_sim6_items(data_paths, devices_info)
    # apps = get_sim6_items(DATA_PATHS, devices_info)
    apps = wf.cached_data('sim6_items', get_items, max_age=600)
    # Record our progress in the log file
    wf.logger.debug('{} Apps cached'.format(len(apps)))

if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
