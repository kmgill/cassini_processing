#!/bin/bash

# Make sure ISIS3 is initialized before running this

function process_dir() {
  dir=$1
  pushd naif.jpl.nasa.gov/pub/naif/JUNO/kernels/${dir}/
  cp -r -v * $ISISDATA/juno/kernels/${dir}/
  pushd $ISISDATA/juno/kernels/${dir}/
  if [ -f makedb ]; then
    echo "Updating db for ${dir}"
    ./makedb
  fi
  popd
  popd
}

. ~/initcass.sh

wget --mirror --no-parent -N ftp://naif.jpl.nasa.gov/pub/naif/JUNO/

process_dir sclk
process_dir lsk
process_dir ck
process_dir spk
process_dir ik
