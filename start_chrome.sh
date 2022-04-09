#!/bin/bash

chromePath="$1"
port="$2"
chromeProfile="$3"

export DISPLAY=:0
"$chromePath" --remote-debugging-port="$port" --user-data-dir="$chromeProfile"