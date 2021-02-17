#!/usr/bin/env python3

import enum
import pcbfile4.types
import pcbfile4.element_factory

class Element:
    type = None

    def set_type(self, type):
        self.type = type

    def split_line_to_ints(self, line, name, token_count):
        s = line.split()
        if len(s) != token_count:
            raise RuntimeError("Expected %s parameters to have %u tokens, got %u (\"%s\")" % (name, token_count, len(s), line))

        list = []
        for token in s:
            list.append(int(token))

        return list

class ElementXY(Element):
    x = None
    y = None

class ElementXYRange(Element):
    x1 = None
    y1 = None
    x2 = None
    y2 = None

class ElementLineWidth(Element):
    line_width = None

class ElementLayer(Element):
    layer = None

class ElementHoleSize(Element):
    hole_size = None

class ElementText(Element):
    text = None

# Arc format:
# - FA or CA
# - x, y, radius, quadrants, line width, layer

class Arc(ElementXY, ElementLineWidth, ElementLayer):
    radius      = None
    quadrants   = None

    def __init__(self):
        super().set_type(pcbfile4.types.ElementType.ARC)

    def parse_line(self, line):
        list = self.split_line_to_ints(line, "arc", 6)

        self.x          = list.pop(0)
        self.y          = list.pop(0)
        self.radius     = list.pop(0)
        self.quadrants  = pcbfile4.types.Quadrants(list.pop(0))
        self.line_width = list.pop(0)
        self.layer      = pcbfile4.types.Layer(list.pop(0))

        return False

# Fill format:
# - FF or CF
# - x1, y1, x2, y2, layer

class Fill(ElementXYRange, ElementLayer):
    def __init__(self):
        super().set_type(pcbfile4.types.ElementType.FILL)

    def parse_line(self, line):
        list = self.split_line_to_ints(line, "fill", 5)

        self.x1         = list.pop(0)
        self.y1         = list.pop(0)
        self.x2         = list.pop(0)
        self.y2         = list.pop(0)
        self.layer      = pcbfile4.types.Layer(list.pop(0))

        return False

# Pad format:
# - FP or CP
# - x, y, x size, y size, shape, hole size, plane, layer
# - name

class Pad(ElementXY, ElementHoleSize, ElementLayer, ElementText):
    x_size      = None
    y_size      = None
    shape       = None
    plane       = None

    in_name     = False

    def __init__(self):
        super().set_type(pcbfile4.types.ElementType.PAD)

    def parse_line(self, line):
        if self.in_name:
            self.text = line
            return False

        list = self.split_line_to_ints(line, "pad", 8)

        self.x              = list.pop(0)
        self.y              = list.pop(0)
        self.x_size         = list.pop(0)
        self.y_size         = list.pop(0)
        self.shape          = pcbfile4.types.Shape(list.pop(0))
        self.hole_size      = list.pop(0)
        self.plane          = pcbfile4.types.Plane(list.pop(0))
        self.layer          = pcbfile4.types.Layer(list.pop(0))

        self.in_name = True
        return True

# String format:
# - FS or CS
# - x, y, height, rotation + flip, line width, layer
# - string text

class String(ElementXY, ElementLineWidth, ElementLayer, ElementText):
    height      = None
    rotation    = None
    flip        = None

    in_text     = False

    def __init__(self):
        super().set_type(pcbfile4.types.ElementType.STRING)

    def parse_line(self, line):
        if self.in_text:
            self.text = line
            return False

        list = self.split_line_to_ints(line, "string", 6)

        self.x          = list.pop(0)
        self.y          = list.pop(0)
        self.height     = list.pop(0)
        self.rotation   = pcbfile4.types.Rotation(list[0] & 3)
        self.flip       = (list.pop(0) & 16) == 16
        self.line_width = list.pop(0)
        self.layer      = pcbfile4.types.Layer(list.pop(0))

        self.in_text = True
        return True

# Track format:
# - FT or CT
# - x1, y1, x2, y2, width, layer, user-routed

class Track(ElementXYRange, ElementLineWidth, ElementLayer):
    user_routed = None

    def __init__(self):
        super().set_type(pcbfile4.types.ElementType.TRACK)

    def parse_line(self, line):
        list = self.split_line_to_ints(line, "track", 7)

        self.x1             = list.pop(0)
        self.x2             = list.pop(0)
        self.y1             = list.pop(0)
        self.y2             = list.pop(0)
        self.line_width     = list.pop(0)
        self.layer          = pcbfile4.types.Layer(list.pop(0))
        self.user_routed    = list.pop(0) == 1

        return False

# Via format:
# - FV or CV
# - x, y, diameter, hole size

class Via(ElementXY, ElementHoleSize):
    diameter    = None

    def __init__(self):
        super().set_type(pcbfile4.types.ElementType.VIA)

    def parse_line(self, line):
        list = self.split_line_to_ints(line, "via", 4)

        idx = 0
        self.x              = list.pop(0)
        self.y              = list.pop(0)
        self.diameter       = list.pop(0)
        self.hole_size      = list.pop(0)

        return False

# Component format:
# - COMP
# - designator
# - pattern
# - comment
# - comment string data
# - designator string data
# - x, y, designator status, comment status, placement status
# - zero or more primitives
# - ENDCOMP

class Component(ElementXY):
    class ParserState(enum.Enum):
        DESIGNATOR      = 1     # Designator, for example D1
        PATTERN         = 2     # Pattern, for example AXIAL0.3
        COMMENT         = 3     # Comment, for example 1N4148
        COMMENT_PARM    = 4     # Comment parameters, as in string
        DESIGNATOR_PARM = 5     # Designator parameters, as in string
        COMPONENT_PARM  = 6     # Component parameters: x, y, designator status, comment status, placement status
        PRIMITIVE       = 7     # One or more primitives, or ENDCOMP

    parser_state        = ParserState(ParserState.DESIGNATOR)
    designator          = None  # String element
    pattern             = None
    comment             = None  # String element
    show_designator     = None
    show_comment        = None
    fixed_in_place      = None
    primitives          = None

    # temporary during designator and comment parsing
    designator_text     = None
    comment_text        = None

    current_primitive   = None

    def __init__(self):
        self.primitives = []
        super().set_type(pcbfile4.types.ElementType.COMP)

    def parse_designator(self, line):
        self.designator_text = line
        self.parser_state = self.ParserState(self.ParserState.PATTERN)
        return True

    def parse_pattern(self, line):
        self.pattern = line
        self.parser_state = self.ParserState(self.ParserState.COMMENT)
        return True

    def parse_comment(self, line):
        self.comment_text = line
        self.parser_state = self.ParserState(self.ParserState.COMMENT_PARM)
        return True

    def parse_comment_parm(self, line):
        self.comment = String()
        self.comment.parse_line(line)
        self.comment.parse_line(self.comment_text)
        self.comment_text = None
        self.parser_state = self.ParserState(self.ParserState.DESIGNATOR_PARM)
        return True

    def parse_designator_parm(self, line):
        self.designator = String()
        self.designator.parse_line(line)
        self.designator.parse_line(self.designator_text)
        self.designator_text = None
        self.parser_state = self.ParserState(self.ParserState.COMPONENT_PARM)
        return True

    def parse_component_parm(self, line):
        list = self.split_line_to_ints(line, "component", 5)

        self.x                      = list.pop(0)
        self.y                      = list.pop(0)
        self.show_designator        = list.pop(0) == 1
        self.show_comment           = list.pop(0) == 1
        self.fixed_in_place         = list.pop(0) == 2

        self.parser_state = self.ParserState(self.ParserState.PRIMITIVE)
        return True

    def parse_primitive(self, line):
        if self.current_primitive == None:
            if line == "ENDCOMP":
                return False
            self.current_primitive = pcbfile4.element_factory.create_element(line, True)
            return True

        if not self.current_primitive.parse_line(line):
            self.primitives.append(self.current_primitive)
            self.current_primitive = None

        return True

    def parse_line(self, line):
        return {
            self.ParserState.DESIGNATOR         : self.parse_designator,
            self.ParserState.PATTERN            : self.parse_pattern,
            self.ParserState.COMMENT            : self.parse_comment,
            self.ParserState.COMMENT_PARM       : self.parse_comment_parm,
            self.ParserState.DESIGNATOR_PARM    : self.parse_designator_parm,
            self.ParserState.COMPONENT_PARM     : self.parse_component_parm,
            self.ParserState.PRIMITIVE          : self.parse_primitive
        }[self.parser_state](line)
