#!/usr/bin/python
# encoding: utf-8

import sys
import argparse
from workflow import (Workflow, ICON_WEB, ICON_INFO, ICON_WARNING,
                      PasswordNotFound)
from workflow.background import run_in_background, is_running


def search_key_for_app(app):
    """Generate a string search key for a app"""
    elements = []
    elements.append(app['name'])  # title of post
    elements.append(app['id'])  # post tags
    # elements.append(app['extended'])  # description
    return u' '.join(elements)


def main(wf):

    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    # add an optional (nargs='?') --apikey argument and save its
    # value to 'apikey' (dest). This will be called from a separate "Run Script"
    # action with the API key
    # parser.add_argument('--setkey', dest='apikey', nargs='?', default=None)
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    ####################################################################
    # View/filter Pinboard posts
    ####################################################################

    query = args.query

    # Get posts from cache. Set `data_func` to None, as we don't want to
    # update the cache in this script and `max_age` to 0 because we want
    # the cached data regardless of age
    apps = wf.cached_data('sim6_items', None, max_age=0)

    # Start update script if cached data is too old (or doesn't exist)
    if not wf.cached_data_fresh('apps', max_age=600):
        cmd = ['/usr/bin/python', wf.workflowfile('update.py')]
        run_in_background('update', cmd)

    # Notify the user if the cache is being updated
    if is_running('update'):
        wf.add_item('Getting new apps from disk',
                    valid=False,
                    icon=ICON_INFO)

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
                    icon=ICON_WEB)

    # Send the results to Alfred as XML
    wf.send_feedback()
    return 0


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
