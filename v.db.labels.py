#!/usr/bin/env python

############################################################################
#
# MODULE:    v.db.labels
# AUTHOR(S): Vaclav Petras
# PURPOSE:   Creates paint labels for a vector map from attributes
# COPYRIGHT: (C) 2014 by Vaclav Petras, and the GRASS Development Team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
############################################################################

#%module
#% description: Creates paint labels for a vector map from attributes
#% keywords: vector, databse, cartography, paint labels
#%end
#%option G_OPT_V_MAP
#%  key: input
#%  description: Input vector map (attribut table required)
#%  required: yes
#%end
#%option
#% key: output
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% label: Name for new paint-label file
#% description: If not given the name of the input map is used
#%end
#%option
#% key: layer
#% type: string
#% required: no
#% multiple: no
#% label: Layer number or name
#% description: A single vector map can be connected to multiple database tables. This number determines which table to use. When used with direct OGR access this is the layer name.
#% answer: 1
#% gisprompt: old,layer_all,layer
#% guisection: Selection
#%end
#%option
#% key: type
#% type: string
#% required: no
#% multiple: yes
#% options: point,line,boundary,centroid,area,face,kernel
#% description: Input feature type
#% answer: point,line,boundary,centroid,area,face,kernel
#% guisection: Selection
#%end
#%option
#% key: cats
#% type: string
#% required: no
#% multiple: no
#% key_desc: range
#% label: Category values
#% description: Example: 1,3,7-9,13
#% guisection: Selection
#%end
#%option
#% key: where
#% type: string
#% required: no
#% multiple: no
#% key_desc: sql_query
#% label: WHERE conditions of SQL statement without 'where' keyword
#% description: Example: income < 1000 and inhab >= 10000
#% guisection: Selection
#%end
#%option
#% key: dp
#% type: integer
#% required: no
#% multiple: no
#% options: 0-32
#% description: Number of significant digits (floating point only) (NOT IMPLEMENTED)
#% answer: 8
#% guisection: Points
#%end
#%option
#% key: xoffset
#% type: double
#% required: no
#% multiple: no
#% description: Offset label in x-direction
#% answer: 0
#% guisection: Placement
#%end
#%option
#% key: yoffset
#% type: double
#% required: no
#% multiple: no
#% description: Offset label in y-direction
#% answer: 0
#% guisection: Placement
#%end
#%option
#% key: reference
#% type: string
#% required: no
#% multiple: yes
#% options: center,left,right,upper,lower
#% description: Reference position
#% answer: center
#% guisection: Placement
#%end
#%option
#% key: font
#% type: string
#% required: no
#% multiple: no
#% description: Font name
#% answer: standard
#% guisection: Font
#%end
#%option
#% key: size
#% type: double
#% required: no
#% multiple: no
#% description: Label size (in map-units)
#% answer: 100
#% guisection: Font
#%end
#%option
#% key: color
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% label: Text color
#% description: Either a standard color name or R:G:B triplet
#% answer: black
#% gisprompt: old,color,color
#% guisection: Colors
#%end
#%option
#% key: rotation
#% type: double
#% required: no
#% multiple: no
#% options: 0-360
#% key_desc: angle
#% description: Rotation angle in degrees (counter-clockwise)
#% answer: 0
#% guisection: Placement
#%end
#%option
#% key: width
#% type: double
#% required: no
#% multiple: no
#% options: 0-25
#% description: Border width
#% answer: 1
#% guisection: Effects
#%end
#%option
#% key: hcolor
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% label: Highlight color for text
#% description: Either a standard color name, R:G:B triplet, or "none"
#% answer: none
#% gisprompt: old,color_none,color
#% guisection: Colors
#%end
#%option
#% key: hwidth
#% type: double
#% required: no
#% multiple: no
#% description: Width of highlight coloring
#% answer: 0
#% guisection: Effects
#%end
#%option
#% key: background
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% label: Background color
#% description: Either a standard color name, R:G:B triplet, or "none"
#% answer: none
#% gisprompt: old,color_none,color
#% guisection: Colors
#%end
#%option
#% key: border
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% label: Border color
#% description: Either a standard color name, R:G:B triplet, or "none"
#% answer: none
#% gisprompt: old,color_none,color
#% guisection: Colors
#%end
#%option
#% key: opaque
#% type: string
#% required: no
#% multiple: no
#% options: yes,no
#% key_desc: yes|no
#% description: Opaque to vector (only relevant if background color is selected)
#% answer: yes
#% guisection: Colors
#%end


# TODO: replace with std option
# TODO: order of options?
# TODO: should the lable file name be required?
# TODO: v.label is using map and labels, here: input and output
# TODO: v.db.labels or v.db.label
# TODO: add fontsize
# TODO: how to handle case in column names?

import sys

import grass.script as gscript


def main():
    options, unused = gscript.parser()

    map_name = options['input']
    layer = options['layer']
    types = options['type']
    where = options['where']
    cats = options['cats']

    # horizontal separator for xyz, using enough special string
    separator = '<--->'

    # if layer is number (non-OGR), represent it as number
    try:
        layer = int(layer)
    except ValueError:
        pass

    kwargs = {}
    if cats:
        kwargs['cats'] = cats
    if where:
        kwargs['where'] = where
    # TODO: this can fail for large maps
    ascii = gscript.read_command('v.out.ascii', input=map_name, layer=layer,
                                  type=types,
                                  output='-', format='point', separator=separator,
                                  **kwargs)
    if cats:
        del kwargs['cats']
    result = gscript.vector_db_select(map=map_name, layer=layer, **kwargs)
    column_names = result['columns']
    column_indexes = {}
    for i, name in enumerate(column_names):
        column_indexes[name] = i
    table = result['values']
    label_attributes = ['east', 'north', 'xoffset', 'yoffset', 'ref', 'font', 'color', 'size', 'width', 'hcolor', 'hwidth', 'background', 'border', 'opaque', 'rotate', 'text']
    option_label_attributes = ['reference', 'rotation']
    label_attribute_to_option = {'ref': 'reference', 'rotate': 'rotation'}
    label_attributes.extend(option_label_attributes)

    for line in ascii.splitlines():
        if not line:
            continue
        values = line.split(separator)
        east = values[0]
        north = values[1]
        cat = int(values[2])  # must be int to search in dictionaries
        # TODO: this might be costly since we go through whole table
        row = table[cat]
        for attribute in label_attributes:
            # try to find label attribute in the attribute table
            if attribute in column_names:
                value = row[column_indexes[attribute]]
            # if east and north are not in attribute table, use geometry
            elif attribute == 'east':
                value = east
            elif attribute == 'north':
                value = north
            # if text is not in attribute table, try to guess the column
            elif attribute == 'text':
                for n in ['name', 'label']:
                    if n in column_names:
                        value = row[column_indexes[n]]
                        break
            else:
                option_key = label_attribute_to_option.get(attribute, attribute)
                value = options[option_key]
            sys.stdout.write('{key}: {value}\n'.format(key=attribute, value=value))
        # TODO: should \n be platform speficic?
        sys.stdout.write('\n')


if __name__ == "__main__":
    main()
