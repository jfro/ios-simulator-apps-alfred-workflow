#!/usr/bin/python
# encoding: utf-8

import sys
import argparse
import simctl
from workflow import (Workflow, ICON_WEB, ICON_INFO, ICON_WARNING,
                      PasswordNotFound)
from workflow.background import run_in_background, is_running


def search_key_for_device(device):
    """Generate a string search key for a device"""
    elements = []
    elements.append(device.name)
    elements.append(device.deviceId)
    elements.append(device.version)
    return u' '.join(elements)


def main(wf):

    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()

    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    ####################################################################
    # View/filter Simulator apps
    ####################################################################

    query = args.query
    siminfo = simctl.SimControl()
    devices = siminfo.activeDevices()


    # If script was passed a query, use it to filter posts if we have some
    if query and devices:
        devices = wf.filter(query, devices, key=search_key_for_device, min_score=20)

    if not devices:  # we have no data to show, so show a warning and stop
        wf.add_item('No devices found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned posts and add a item for each to
    # the list of results for Alfred
    for device in devices:
        deviceName = '%s (%s)' % (device.name, device.version)

        wf.add_item(title=deviceName,
                    subtitle=', '.join(device.info['xcodes']),
                    arg=device.deviceId,
                    valid=True,
                    uid=device.deviceId)

    # Send the results to Alfred as XML
    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
