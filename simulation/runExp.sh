#!/bin/bash 

echo "Bash version ${BASH_VERSION}..."
for i in {1..30}
do
   echo "Welcome $i times"
   pipenv run python ./simulation.py
done
