v.db.labels
===========

GRASS GIS module to creates paint labels from attributes

This code will be moved to GRASS GIS addons once it is turned to a proper module.

Run using:

    mkdir $LOCATION/paint
    mkdir $LOCATION/paint/labels

    python v.db.labels.py input=points size=2500 color=blue hcolor=white hwidth=200 reference=left > $LOCATION/paint/labels/points

    d.labels labels=points
