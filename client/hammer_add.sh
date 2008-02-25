#!/bin/sh
set -eu

echo $1
for foo in $(seq 1 10)

do
	python deleteProfile.py -s http://localhost:8080/ --uuidFile=uuid-sample$1
	python sendProfile.py -s http://localhost:8080/ -a --submitOnly --uuidFile=uuid-sample$1
	python sendProfile.py -s http://localhost:8080/ -a --submitOnly --uuidFile=uuid-sample$1
done
