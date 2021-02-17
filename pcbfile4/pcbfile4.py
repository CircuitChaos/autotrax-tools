#!/usr/bin/env python3
#
# PCB file structure:
# - PCB FILE 4
# - zero or more primitives and components (named here as "elements")
# - ENDPCB
#
# Primitive structure:
# - primitive name (FP, FV, FA, ...)
# - zero or more primitive arguments
#
# Component structure:
# - COMP
# - component parameters
# - zero or more primitives
# - ENDCOMP

import pcbfile4.element_factory
import enum
import sys

class PcbFile4:
    class ParserState(enum.Enum):
        HEADER      = 1
        CONTENT     = 2
        END         = 3

    parser_state = ParserState(ParserState.HEADER)
    current_element = None
    elements = []

    def parse_header(self, line):
        if line != "PCB FILE 4":
            raise RuntimeError("Expected header, got \"%s\"" % line)
        self.parser_state = self.ParserState.CONTENT

    def parse_content(self, line):
        if line == "ENDPCB":
            if self.current_element != None:
                raise RuntimeError("Expected primitive or component data, got ENDPCB")
            self.parser_state = self.ParserState.END
            return

        if self.current_element == None:
            self.current_element = pcbfile4.element_factory.create_element(line, False)
        else:
            if not self.current_element.parse_line(line):
                self.elements.append(self.current_element)
                self.current_element = None

    def parse_end(self, line):
        raise RuntimeError("Expected end of file, got \"%s\"" % line)

    def clear(self):
        self.parser_state = self.ParserState(self.ParserState.HEADER)
        self.current_primitive = None
        self.current_component = None
        self.primitives = []

    def parse_line(self, line):
        line = line.rstrip("\n").rstrip("\r")

        {
            self.ParserState.HEADER     : self.parse_header,
            self.ParserState.CONTENT    : self.parse_content,
            self.ParserState.END        : self.parse_end
        }[self.parser_state](line)

    def load_stdin(self):
        self.clear()
        for line in sys.stdin:
            self.parse_line(line)

    def load_file(self, file):
        self.clear()
        f = open(file, "r")
        for line in f:
            self.parse_line(line)
        f.close()

    def get_elements(self):
        return self.elements
