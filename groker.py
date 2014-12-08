#!/usr/bin/env python3

'''
A basic script that is used to fetch and update defined repositories(YAML format)
into an OpenGrok source location.

The main feature is (compared to running it in crontab) is that it provides an
easy-to-read and easy-to-use YAML configuration file that even non-operation
people or other services can use.

Author: Eric Ripa - eric@ripa.io (2014-12-08)
'''

import argparse
from plumbum import local
from plumbum.cmd import git
from plumbum.cmd import repo
from plumbum.commands.processes import ProcessExecutionError
import subprocess, shlex
import yaml
import os
import shutil

def parse_args():
    parser = argparse.ArgumentParser(description = "groker - {OpenGrok helper")
    parser.add_argument('-c', '--config-file',
                        help='Use a non-default configuration (default is repos.yml)',
                        default='repos.yml')
    parser.add_argument('-o', '--output-dir',
                        help='Where to put the repositories (usually under OpenGroks src directory, default=/var/opengrok/src)',
                        default='/var/opengrok/src')
    parser.add_argument('-g', '--opengrok',
                        help='Path to the OpenGrok tool, default=/opt/opengrok/bin/OpenGrok)',
                        default='/opt/opengrok/bin/OpenGrok')
    parser.add_argument('-p', '--python2',
                        help='*NOT IMPLEMENTED* Path to python2 (might be needed for Repo YMMV), default=/usr/bin/python2)',
                        default='/usr/bin/python2')
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

def target_name(name, target):
    return name + '-' + target

def git_clone(url, tag, target):
    clone_cmd = git['clone', '-b', tag, url, target]
    try:
        res = clone_cmd()
    except ProcessExecutionError as e:
        print('Error cloning %s with tag %s, message was:\n%s' % (url, tag, e.stderr))

def git_update(tag, target):
    update_command = git['pull']
    try:
        with local.cwd(target):
            res = update_command()
    except ProcessExecutionError as e:
        print('Error updating %s with tag %s, message was:\n%s' % (target, tag, e.stderr))

def repo_init(url, tag, target):
    if not os.path.isdir(target):
        os.makedirs(target)
    # use subprocess instead of plumbum as repo requires python2
    init_cmd = shlex.split('/usr/bin/python2 %s init -u %s  -b %s' % (repo.__str__(), url, tag))
    try:
        with local.cwd(target):
            res = subprocess.check_call(init_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            repo_sync(target)
    except subprocess.CalledProcessError as e:
        print('Error initializing repo %s at %s with tag %s, message was:\n%s' % (url, target, tag, e.output))
        shutil.rmtree(target, ignore_errors=True)

def repo_sync(target):
    # use subprocess instead of plumbum as repo requires python2
    sync_cmd = shlex.split('/usr/bin/python2 %s sync -j8' % (repo.__str__()))
    try:
        with local.cwd(target):
            res = subprocess.check_call(sync_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print('Error syncing %s, message was:\n%s' % (target, e.output))

def fetch_repo(name, details, output_dir):
    print('processing %s source at %s' % (details['type'], details['url']))
    for tag in details['tags']:
        target_directory = os.path.join(output_dir, target_name(name, tag))
        if os.path.isdir(target_directory):
            print('  updating tag: %s, target: %s' % (tag, target_directory))
            if details['type'] == 'git':
                git_update(tag, target_directory)
            elif details['type'] == 'repo':
                repo_sync(target_directory)
        else:
            print('  fetching tag: %s, target: %s' % (tag, target_directory))
            if details['type'] == 'git':
                git_clone(details['url'], tag, target_directory)
            elif details['type'] == 'repo':
                repo_init(details['url'], tag, target_directory)

def fetch_repos(output_dir, config):
    for name, details in config.items():
        if details['type'] == 'repo' or details['type'] == 'git':
            fetch_repo(name, details, output_dir)
        else:
            print('WARNING: Selected type %s for %s is not yet implemented' % (details['type'], name))

def reindex_opengrok(opengrok):
    opengrok_cmd = shlex.split('%s index' % opengrok)
    print('Starting OpenGrok index operation...')
    try:
        subprocess.check_call(opengrok_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print('Done!')
    except subprocess.CalledProcessError as e:
        print('Could not index, error running OpenGrok index, message was:\n%s' % (e.output))
    except FileNotFoundError:
        print('Could not index, unable to find OpenGrok tool at %s, you can specify a path with -g/--opengroup <path>' % opengrok)

def main():
    args = parse_args()
    config = read_config(args.config_file)
    if not os.path.isdir(args.output_dir):
        print('Output directory did not exist, creating.. (%s)' % args.output_dir)
        os.makedirs(args.output_dir)
    if config:
        fetch_repos(args.output_dir, config)
        reindex_opengrok(args.opengrok)
    else:
        sys.exit('No repos found in %s, exiting...' % (args.config_file))

if __name__ == '__main__':
    main()
