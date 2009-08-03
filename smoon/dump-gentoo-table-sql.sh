#!/bin/sh
python playmodel.py 2>/dev/null | grep --color=never -v '^[0-9][0-9][0-9][0-9]-'
