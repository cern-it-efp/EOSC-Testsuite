#!/usr/bin/python -u

from dateutil.tz import tzlocal
import time
import requests
import json
import dateutil.parser
import getopt
import datetime
import os
import sys

# This is the name of the host where the task should be posted.
LEAD = "localhost"
tasks_url = "https://%s/pscheduler/tasks" % (LEAD)
endpoint = getopt.getopt(sys.argv, "", ["--ep"])[1][2]
resultsFile = "/tmp/perfsonar_results.json"
customTO=30

TASK_latency = {  # pscheduler task --format=json latencybg --packet-count 38 --dest $ENDPOINT / pscheduler task --format=json latency --dest $ENDPOINT
    "schema": 1,
    "test": {
        "spec": {
            "dest": endpoint,
            "schema": 1
        },
        "type": "latency"
    },
    "schedule": {}
}

TASK_latencybg = {
    "schema": 1,
    "test": {
        "spec": {
            "dest": endpoint,
            "packet-count": 38,
            "schema": 1
        },
        "type": "latencybg"
    },
    "schedule": {}
}

TASK_throughput = {  # pscheduler task --format=json throughput --dest $ENDPOINT
    "schema": 1,
    "test": {
        "spec": {
            "dest": endpoint,
            "schema": 1
        },
        "type": "throughput"
    },
    "schedule": {}
}

TASK_throughput_reverse = {
    "schema": 1,
    "test": {
        "spec": {
            "dest": endpoint,
            "reverse": True,
            "schema": 1
        },
        "type": "throughput"
    },
    "schedule": {}
}

TASK_rtt = {  # pscheduler task --format=json rtt --dest $ENDPOINT
    "schema": 1,
    "test": {
        "spec": {
            "dest": endpoint,
            "schema": 1
        },
        "type": "rtt"
    },
    "schedule": {}
}

TASK_trace = {  # pscheduler task --format=json trace --dest $ENDPOINT
    "schema": 1,
    "test": {
        "spec": {
            "dest": endpoint,
            "schema": 1
        },
        "type": "trace"
    },
    "schedule": {}
}

TASKS = [TASK_rtt, TASK_trace, TASK_latency, TASK_throughput, TASK_throughput_reverse]
TASKS = [TASK_throughput]


# -----------------------------------------------------------------------------
# Utilities
def fail(message, task=None, quit=None):
    """Complain about a problem and exit."""

    print("----------------------------------------------------------")
    print(message)
    print(task)
    print(quit)
    print("----------------------------------------------------------")

    error = {
        "message": message
    }
    if task is not None:
        error["task"] = task
    with open(resultsFile, 'a') as outfile:
        outfile.write(json_dump(error))
    if quit is True:
        exit(1)


def json_load(source):
    """Load a blob of JSON into Python objects"""

    try:
        json_in = json.loads(str(source))
    except ValueError as ex:
        raise ValueError("Invalid JSON: " + str(ex))

    return json_in


def json_dump(obj):
    """Convert a blob of Python objects to a string"""
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))


def url_post(url,          # GET URL
             data=None,    # Data to post
             ):
    """Post to a URL, returning whatever came back as JSON"""

    try:
        request = requests.post(url, data=data, verify=False,
                                allow_redirects=True, timeout=customTO)
        status = request.status_code
        text = request.text
    except requests.exceptions.Timeout:
        status = 400
        text = "Request timed out"
    except requests.exceptions.ConnectionError as ex:
        status = 400
        text = str(ex)
    except Exception as ex:
        status = 500
        text = str(ex)

    if status not in [200, 201]:
        return (status, text)

    return (status, json_load(text))


def url_get(url,          # GET URL
            params={},    # GET parameters
            json=True     # Evaluate returned data as JSON
            ):
    """Fetch a URL using GET with parameters"""

    try:
        request = requests.get(
            url,
            params=params,
            verify=False,
            allow_redirects=True,
            timeout=customTO)
        status = request.status_code
        text = request.text
    except requests.exceptions.Timeout:
        status = 400
        text = "Request timed out"
    except requests.exceptions.ConnectionError as ex:
        status = 400
        text = str(ex)
    except Exception as ex:
        status = 400
        text = str(ex)

    if status not in [200, 201]:
        return (status, text)

    if json:
        return (status, json_load(text))
    else:
        return (status, text)


def manageAndRunTask():
    # Post the task to the server's "tasks" endpoint
    try:
        status, task_url = url_post(tasks_url, data=json_dump(TASK))
    except Exception as ex:
        fail("Unable to post task: %s" % (str(ex)), TASK["test"]["type"])
        continue

    # -----------------------------------------------------------------------------
    # Fetch the posted task with extra details.
    try:
        status, task_data = url_get(task_url, params={"detail": True})
        if status != 200:
            raise Exception(task_data)
    except Exception as ex:
        fail("Failed to post task: %s" % (str(ex)), TASK["test"]["type"])
        continue

    try:
        first_run_url = task_data["detail"]["first-run-href"]
    except KeyError:
        fail("Server returned incomplete data.", TASK["test"]["type"])
        continue

    # -----------------------------------------------------------------------------
    # Get first run and make sure we have what we need to function. Server will wait until the first run has been scheduled before returning a result.
    status, run_data = url_get(first_run_url)

    if status == 404:
        fail("The server never scheduled a run for the task.",
             TASK["test"]["type"])
        continue
    if status != 200:
        fail("Error %d: %s" % (status, run_data), TASK["test"]["type"])
        continue

    skipIT = False
    for key in ["start-time", "end-time", "result-href"]:
        if key not in run_data:
            fail("Server did not return %s with run data" %
                 (key), TASK["test"]["type"])
            skipIT = True
            break
    if skipIT is True:
        continue

    # -----------------------------------------------------------------------------
    # Wait for the end time to pass
    try:
        end_time = dateutil.parser.parse(run_data["end-time"])
    except ValueError as ex:
        fail("Server did not return a valid end time for the task: %s" %
             (str(ex)), TASK["test"]["type"])
        continue

    now = datetime.datetime.now(tzlocal())
    sleep_time = end_time - now if end_time > now else datetime.timedelta()
    sleep_seconds = (sleep_time.days * 86400) \
        + (sleep_time.seconds) \
        + (sleep_time.microseconds / (10.0**6))

    time.sleep(sleep_seconds)

    # -----------------------------------------------------------------------------
    # Wait for the result to be produced and fetch it.
    err = ""
    retries = 20
    for i in range(retries):
        status, result_data = url_get(
            run_data["result-href"], params={"wait-merged": True})
        if status == 200:
            break
        elif status != 200 and i == retries-1:
            err = "Did not get a result: %s" % (
                result_data), TASK["test"]["type"]
            break
        time.sleep(2)
    return err, result_data

# This disables warnings about unverifiable keys when fetching HTTPS
# URLs.  pScheduler rolls its own key by default.
try:
    warning = requests.packages.urllib3.exceptions.InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(warning)
except:
    print("Error disabling insecure request warning, not quitting")

# -----------------------------------------------------------------------------
# TESTING BEGINS HERE
# -----------------------------------------------------------------------------

if os.system("pscheduler ping %s" % endpoint) != 0:
    fail("perfSONAR not reachable at '%s'" % endpoint, quit=True)

# Wait for test tools to be ready on the server
while len(url_get("https://localhost/pscheduler/tests",
    params={"detail": True})[1]) < 1:
    #print("Tools not ready yet...")
    time.sleep(10)
    pass

for TASK in TASKS:

    print("Running: "+ TASK["test"]["type"])

    err, result_data = manageAndRunTask()

    if err:
        fail(err, TASK["test"]["type"])
        continue

    result_data["task"] = TASK["test"]["type"]
    print json_dump(result_data)

    with open(resultsFile, 'a') as outfile:
        outfile.write(json_dump(result_data))


# The End
exit(0)
