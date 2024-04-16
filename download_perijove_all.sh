#!/bin/bash
# download_perijove_all.sh
# Page scrapes the JunoCam mission website and downloads all image data
# for a specified perijove.


if [ $# -ne 1 ]; then
    echo "Please supply only a valid perijove number"
    echo "Ex: download_perijove_all.sh 29"
    exit 1
fi

PJ="$1"

echo Downloading Perijove $PJ...

function make_id_list() {
    url="https://www.missionjuno.swri.edu/junocam/processing?source=junocam&ob_from=&ob_to=&phases%5B%5D=PERIJOVE+${PJ}&perpage=100"
    curl -s "$url" | grep "/junocam/processing?id=" | grep -o '/junocam/processing?id=[^"]*' | cut -d = -f 2 > id.lis
}

function get_product_page() {
    page_id=$1
    pageurl="https://www.missionjuno.swri.edu/?ajax=markup&path=/junocam/processing&id=${page_id}&partial&redirect=%2Fjunocam%2Fprocessing%3Fsource%3Djunocam%26p%3D1&ts=1599154107"
    curl -s "$pageurl" > page.${page_id}.html
}

function get_product_id_from_page_id() {
    page_id=$1
    page_path=page.${page_id}.html
    product_id=`cat $page_path | grep -o "JNCE_[^<]*"`
    echo $product_id
}

function get_metadata_download() {
    page_id=$1
    page_path=page.${page_id}.html
    md_url=https://www.missionjuno.swri.edu/Vault`cat $page_path | grep -o '/VaultDownload[^"]*' | head -n 1`
    echo $md_url
}

function get_image_download() {
    page_id=$1
    page_path=page.${page_id}.html
    img_url=https://www.missionjuno.swri.edu/Vault`cat $page_path | grep -o '/VaultDownload[^"]*' | head -n 2 | tail -n 1`
    echo $img_url
}

make_id_list

if [ `cat id.lis | wc -l` -eq 0 ]; then
    echo "No data found for Perijove $PJ"
    rm id.lis
    exit
fi


for id in `cat id.lis`; do

    get_product_page $id

    product_id=`get_product_id_from_page_id $id`

    if [ "x$product_id" == "x" ]; then
        echo No product id associated with page id $id, skipping
        rm page.${id}.html
        continue
    fi

    echo Fetching Product ID: $product_id -- $id
    if [ ! -d $product_id ]; then
        mkdir $product_id
        md_url=`get_metadata_download $id`
        img_url=`get_image_download $id`

        echo ${product_id} Metadata URL: $md_url
        echo ${product_id} ImageSet URL: $img_url
        pushd $product_id > /dev/null
            curl -o "$id-Data.zip" "$md_url"
            curl -o "$id-ImageSet.zip" "$img_url"
        popd > /dev/null

        rm page.${id}.html
    else
        echo Already have $product_id, skipping
    fi


done

rm id.lis
