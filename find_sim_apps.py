#!/usr/bin/python
# encoding: utf-8

import sys
import argparse
import siminfo
from workflow import (Workflow, ICON_WEB, ICON_INFO, ICON_WARNING,
                      PasswordNotFound)
from workflow.background import run_in_background, is_running


def search_key_for_app(app):
    """Generate a string search key for a app"""
    elements = []
    elements.append(app['name'])
    elements.append(app['id'])
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

    apps = siminfo.getSimAppResults(wf.cachedir)


    # If script was passed a query, use it to filter posts if we have some
    if query and apps:
        apps = wf.filter(query, apps, key=search_key_for_app, min_score=20)

    if not apps:  # we have no data to show, so show a warning and stop
        wf.add_item('No apps found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned posts and add a item for each to
    # the list of results for Alfred
    for app in apps:
        appName = '%s (%s - %s)' % (app['name'], app['device']['name'], app['device']['runtime'])

        wf.add_item(title=appName,
                    subtitle=app['short_path'],
                    arg=app['data_path'],
                    valid=True,
                    icon=app['icon'],
                    uid=app['data_path'])

    # Send the results to Alfred as XML
    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
