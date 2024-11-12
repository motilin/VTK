#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <filename>"
  exit 1
fi

FILE=$1

# Watch the specified file and restart the script on changes
while true; do
  ls "$FILE" | entr -r python "$FILE"
done
