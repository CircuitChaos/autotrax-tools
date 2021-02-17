#!/usr/bin/env python3

import pcbfile4.elements

def create_element(line, in_component):
    if line == "COMP":
        return pcbfile4.elements.Component()

    if len(line) != 2:
        raise RuntimeError("Expected primitive type, got \"%s\"" % line)

    if in_component:
        if line[0] != 'C':
            raise RuntimeError("Expected component primitive type, got \"%s\"" % line)
    else:
        if line[0] != 'F':
            raise RuntimeError("Expected non-component primitive type, got \"%s\"" % line)

    dict = {
        "A": pcbfile4.elements.Arc,
        "F": pcbfile4.elements.Fill,
        "P": pcbfile4.elements.Pad,
        "S": pcbfile4.elements.String,
        "T": pcbfile4.elements.Track,
        "V": pcbfile4.elements.Via
    }

    for key in dict:
        if key == line[1]:
            e = dict[key]()
            return e

    raise RuntimeError("Unknown primitive type \"%s\"" % line)
