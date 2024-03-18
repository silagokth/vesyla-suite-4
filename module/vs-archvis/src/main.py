#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import DataStructure_pb2 as ds
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

SLOT_WIDTH = 5
SLOT_HEIGHT = 2
CELL_WIDTH = 10
CELL_HEIGHT = 10

def draw_resource(ax, base_x, base_y, slot, size, name, color):
    print('Draw resource {} at ({}, {}) slot {} with size {}'.format(name, base_x, base_y, slot, size))
    # compute the starting point of the resource
    x = base_x
    y = base_y + slot * SLOT_HEIGHT
    # draw the resource
    ax.add_patch(patches.Rectangle((x, y), SLOT_WIDTH, size*SLOT_HEIGHT, color=color))
    # draw the resource name
    ax.text(x + size * SLOT_WIDTH / 2, y + SLOT_HEIGHT / 2, name, ha='center', va='center')

def main(args):
    # parse the input arguments:
    # -a, --arch: the architecture file
    # -o, --output: the output file
    parser = argparse.ArgumentParser(description='Visualize the architecture')
    parser.add_argument('-a', '--arch', help='The architecture file')
    parser.add_argument('-o', '--output', help='The output file')
    args = parser.parse_args(args)

    # read the input file as a protobuf message, the input file is a json file.
    # the json file is generated by the protobuf message.
    arch = ds.ArchitectureDescription()
    with open(args.arch, 'r') as f:
        Parse(f.read(), arch)
    
    # create a database for the resources
    resources = {}
    for res in arch.resources:
        resources[res.name] = res
    
    # draw the first resource
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    ax.add_patch(patches.Rectangle((10, 10), 20, 20, color='red'))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    for res in arch.resources:
        draw_resource(ax, 10, 10, 0, res.size, res.name, 'red')
        break

    # save the figure to the output file
    plt.savefig(args.output, format='pdf', bbox_inches='tight')

if __name__ == '__main__':
    main(sys.argv[1:])

    
