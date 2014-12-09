#!/usr/bin/env bash
#
# Bash wrapper for running groker.py in crontab
#

test_python () {
    if ! ${PYTHON_BIN} -c 'import yaml ; import plumbum' &> /dev/null ; then
        echo 'Error: Could not find pyyaml or plumbum modules!' >&2
        echo 'Info:  Tip: install them in a virtualenv, with:' >&2
        echo 'Info:    pip install -r requirements.txt' >&2
        echo 'Info:  See README.md for more details.' >&2
        exit 1
    fi
}

usage () {
    echo 'Usage:'
    echo "${SCRIPT} [virtualenv_path] [groker.py options]"
    exit 0
}

# First check for --help or -h and print usage if requested
args="$@"
if [ -z "${args##*"--help"*}" ] || [ -z "${args##*"-h"*}" ] ; then
    usage
fi

# Setup some variables to support more flexible execution
SCRIPT_DIR=$(dirname $0)
SCRIPT="${SCRIPT_DIR%%/}/groker.py"
SCRIPT_ARGUMENTS=""
VIRTUALENV_PATH="${SCRIPT_DIR%%/}/virtualenv"

# Argument handling, make wrapper aware or virtualenv and argument passing
if [ "$#" -gt 0 ] ; then
    if [ -d "${1}" ] ; then
        VIRTUALENV_PATH="${1}"
        shift
        SCRIPT_ARGUMENTS="$@"
    else
        SCRIPT_ARGUMENTS="$@"
    fi
fi

# If provided path contains a python exec, use it, else use system python
if [ -x "${VIRTUALENV_PATH%%/}/bin/python" ] ; then
    PYTHON_BIN="${VIRTUALENV_PATH%%/}/bin/python"
else
    PYTHON_BIN=$(which python)
fi

# Verify that provided python environment have our required modules
test_python

# Execute!
"${PYTHON_BIN}" "${SCRIPT}" ${SCRIPT_ARGUMENTS}
