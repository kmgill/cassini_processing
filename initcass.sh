#!/bin/bash

ulimit -n 2048

# NOTE: Edit this with the correct paths!

export PATH=$PATH:/absolute-path-to-cassini_processing-repo/cassini_processing
export ISISROOT=/absolute-path-to-ISIS3-installation/ISIS/isis
export ISIS3DATA=/absolute-path-to-ISIS3-installation/ISIS/data

. $ISISROOT/scripts/isis3Startup.sh
