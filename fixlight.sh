#!/bin/bash

list=$1
outputdir=$2

if [ "x$outputdir" == "x" ]; then
	outputdir=photomet
fi

if [ ! -d $outputdir ]; then
	mkdir $outputdir
fi

for f in `cat $list`; do
  echo $f
  photomet from=$f to=$outputdir/$f maxemission=60.0 maxincidence=75 phtname=hapkehen theta=9 wh=0.218651 hg1=0.178965 hg2=0.971493 hh=0.085 b0=2.7 normname=albedo incref=0 thresh=1e+31 albedo=1
done
