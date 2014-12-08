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
import tempfile

def parse_args():
    parser = argparse.ArgumentParser(description = "***REMOVED*** {OpenGrok helper")
    parser.add_argument('-c', '--config-file',
                        help='Use a non-default configuration (default is repos.yml)',
                        default='repos.yml')
    parser.add_argument('-o', '--output-dir',
                        help='Where to put the repositories (usually under OpenGroks src directory, default=/var/opengrok/src)',
                        default='/var/opengrok/src')
    return parser.parse_args()

def read_config(file_name):
    if not os.path.isfile(file_name):
        print('Could not find configuration file (%s), will copy the template and use that.' % (file_name))
        shutil.copyfile('repos.yml-template', file_name)
    with open(file_name, 'r') as f:
        return yaml.load(f)

def interesting_ref(ref, tags):
    if 'heads' or 'HEAD' in ref:
        return True
    else:
        ref_split = ref.split()
        if ref_split[-2] == 'tags' and ref_split[-1] in tags:
            print('OK!')
            return True
    return False

def read_remote_repo_refs(url, tags=[]):
    print(tags)
    read_cmd = git['ls-remote', url]
    res = read_cmd().split('\n')
    refs_lines = [x.split('\t') for x in res if x]
    refs_dict = dict([(d[1], d[0]) for d in refs_lines if interesting_ref(d[1], tags)])
    for ref, sha in refs_dict.items():
        print(ref, sha)
        pass

def fetch_repos(output_dir, config):
    for name, details in config.items():
        if details['type'] == 'repo':
            print('Fetching individual repos from %s Repo manifest with URL %s to %s' % (name, details['url'], output_dir))
            if 'tags' in details.keys():
                read_remote_repo_refs(details['url'], details['tags'])
            else:
                read_remote_repo_refs(details['url'])
        else:
            print('WARNING: Selected type %s for %s is not yet implemented' % (details['type'], name))

def main():
    args = parse_args()
    config = read_config(args.config_file)
    if config:
        fetch_repos(args.output_dir, config)
    else:
        sys.exit('No repos found in %s, exiting...' % (args.config_file))

if __name__ == '__main__':
    main()
