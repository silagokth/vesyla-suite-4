#!/bin/sh
set -e

# check the number of arguments
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <id>"
  exit 1
fi

################################################################################
# We by pass this process for now since the instr simulator is not ready

cp -r mem/sram_image_m0.bin mem/sram_image_m1.bin
exit 0

################################################################################

# get the id of the code segment from the first argument
id=$1

# check the necessary directories
if [ ! -d "system/arch" ]; then
  echo "system/arch directory does not exist"
  exit 1
fi
if [ ! -d "system/isa" ]; then
  echo "system/isa directory does not exist"
  exit 1
fi
if [ ! -d "system/instr/${id}" ]; then
  echo "system/instr/${id} directory does not exist"
  exit 1
fi
if [ ! -d "mem" ]; then
  echo "mem directory does not exist"
  exit 1
fi
mkdir -p archive
mkdir -p system/metric
mkdir -p system/state

# create the necessary directories
mkdir -p temp
mkdir -p archive/instr_sim_${id}

# simulate the code segment
vesyla-suite alimpsim \
    --arch system/arch/arch.json \
    --instr system/instr/${id}/instr.bin \
    --isa system/isa/isa.json \
    --input mem/sram_image_in.bin \
    --output mem/sram_image_m1.bin \
    --metric system/metric/metric.json \
    --state_reg system/state/state_reg.json

# archive everything
mv temp archive/instr_sim_${id}