# groker - {OpenGrok updater and re-indexer

A basic script that is used to fetch and update defined repositories (YAML format) into an OpenGrok source location.

The main feature is (compared to running it in crontab) is that it provides an easy-to-read and easy-to-use YAML configuration file that even non-operation people or other services can use.

# Concept

Clones and/or syncs git and/or repo projects into an [{OpenGrok](http://opengrok.github.io/OpenGrok/) friendly format.

First time it will get the data (`git clone -b <tag/branch> <url> <name-tag/branch>` or `repo init -u <manifest> -b <tag/branch> && repo sync`) If the repository or project already exists a `git pull` or `repo sync` will be done instead.

Secondly the script will also initiate opengrok reindex procedure.

# Todo

  - Refactor code to support --python2 argument for repo tool execution using user-provided python2 path

# Configuration

There is a configuration template in the repository, repos.yml-template, copy/rename to repos.yml and edit as needed.

# Usage

After cloning you should run `pip install -r requirements.txt`, use a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) if you want to isolate it. Tested with Python **3.4.2**.

    $ ./groker.py --help
    usage: groker.py [-h] [-c CONFIG_FILE] [-o OUTPUT_DIR]

    {OpenGrok helper

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            Use a non-default configuration (default is repos.yml)
      -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                            Where to put the repositories (usually under OpenGroks
                            src directory, default=/var/opengrok/src)
# License

The MIT License (MIT)

Copyright (c) 2015 Eric Ripa
