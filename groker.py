#!/usr/bin/env python3

'''
This is a script for automatically parse the ***REMOVED*** gerrit site for repos
to add to the {OpenGrok cross-reference and history browser.

Author: Eric Ripa - eric.ripa@***REMOVED*** (2014-10-20)

'''

import argparse
import xml.etree.ElementTree as ET
from plumbum.cmd import git
import yaml
import os
import shutil
import sys

def parse_args():
    parser = argparse.ArgumentParser(description = "***REMOVED*** {OpenGrok helper")
    parser.add_argument('-c', '--config-file',
                        help='Use a non-default configuration (default is repos.yml)',
                        default='repos.yml')
    return parser.parse_args()

def read_config(file_name):
    if not os.path.isfile(file_name):
        print('Could not find configuration file (%s), will copy the template and use that.' % (file_name))
        shutil.copyfile('repos.yml-template', file_name)
    with open(file_name, 'r') as f:
        return yaml.load(f)

def fetch_repos(config):
    for name, details in config.items():
        print(name, details)

def main():
    args = parse_args()
    config = read_config(args.config_file)
    if config:
        fetch_repos(config)
    else:
        sys.exit('No repos found in %s, exiting...' % (args.config_file))

if __name__ == '__main__':
    main()
