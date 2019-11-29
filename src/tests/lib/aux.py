#!/usr/bin/env python3

import sys
try:
    import yaml
    import json
    import os
    import datetime
    import time
    import subprocess
    import shutil

except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)

def runCMD(cmd, hideLogs=None, read=None):
    """ Run the command.

    Parameters:
        cmd (str): Command to be run
        hideLogs (bool): Indicates whether cmd logs should be hidden
        read (bool): Indicates whether logs of the command should be returned

    Returns:
        int or str: Command's exit code. Logs of the command if read=True
    """

    if read is True:
        return os.popen(cmd).read().strip()
    if hideLogs is True:
        return subprocess.call(
            cmd, shell=True, stdout=open(
                os.devnull, 'w'), stderr=subprocess.STDOUT)
    else:
        return os.system(cmd)


def stop(code):
    """ Stops the TS run exiting using the provided status code

    Parameters:
        code (int): Exit code to be used
    """

    time.sleep(2)
    sys.exit(code)


def loadFile(loadThis, required=None):
    """ Loads a file

    Parameters:
        loadThis (str): Path to the file to load
        required (bool): Indicates whether the file is required

    Returns:
        str or yaml: The loaded file or empty string if the file was not found
                     and required is not True. Exits with code 1 otherwise.
    """

    if os.path.exists(loadThis) is False:
        if required is True:
            print(loadThis + " file not found")
            stop(1)
        else:
            return ""
    with open(loadThis, 'r') as inputfile:
        if ".yaml" in loadThis:
            try:
                return yaml.load(inputfile, Loader=yaml.FullLoader)
            except AttributeError:
                try:
                    return yaml.load(inputfile)
                except yaml.scanner.ScannerError:
                    print("Error loading yaml file " + loadThis)
                    stop(1)
            except yaml.scanner.ScannerError:
                print("Error loading yaml file " + loadThis)
                stop(1)
        else:
            return inputfile.read().strip()


def writeToFile(filePath, content, append):
    """ Writes stuff to a file.

    Parameters:
        filePath (str): Path to the file to load
        content (str): Content to write to the file
        append (bool): If true, the content has to be appended.
                       False overrides the file or creates if not existing
    """

    mode = 'w'
    if append is True:
        mode = 'a'
    with open(filePath, mode) as outfile:
        outfile.write(content + '\n')


def writeFail(resDir, file, msg, toLog):
    """Writes results file in case of errors.

    Parameters:
        file (str): Name of the results file.
        msg (str): Message to write to results file.
        toLog (str): File to which write the log msg.
    """

    writeToFile(toLog, msg, True)
    with open(resDir + "/" + file, 'w') as outfile:
        json.dump({"info": msg, "result": "fail"},
                  outfile, indent=4, sort_keys=True)


def logger(text, sym, file):
    """ Logs in a fancy way.

    Parameters:
        text (str): Text to log
        sym (bool): Symbol to use to create boxes and separation lines
        file (bool): File the logs should be sent to
    """

    size = 61  # longest msg on code
    frame = sym * (size + 6)
    blank = sym + "  " + " " * size + "  " + sym
    toPrint = frame + "\n" + blank
    if isinstance(text, list):
        for i in text:
            textLine = i.strip()
            toPrint += "\n" + sym + "  " + textLine + \
                " " * (size - len(textLine)) + "  " + sym
    else:
        text = text.strip()
        toPrint += "\n" + sym + "  " + text + \
            " " * (size - len(text)) + "  " + sym
    toPrint += "\n" + blank + "\n" + frame
    if file:
        runCMD("echo \"%s\" >> %s" %
               (toPrint, file))
    else:
        print(toPrint)
