#!/bin/sh
set -e

mkdir -p system
mkdir -p archive

mkdir temp

vesyla component assemble -a ../arch.json -o temp
cp -r temp/arch system
cp -r temp/rtl system
cp -r temp/isa system
cp -r temp/sst system
mv temp archive/assemble
