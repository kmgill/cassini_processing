

function process_jno() {
  d=$1

  pushd $d > /dev/null

  numcubs=`ls *_Mosaic_RGB.cub 2> /dev/null | wc -l `
  if [ $numcubs == 0 ]; then
    echo Processing $d
    process_junocam.py -fFdvlL -o vt=2 projection=jupiterequirectangular -s 0.001 -p
  else
    echo Skipping $d
  fi



  popd > /dev/null
}

for d in `ls -1d JNCE*C00*`; do


  if [ ! -d $d ]; then
    continue
  fi

  process_jno $d


done
