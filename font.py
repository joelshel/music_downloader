#!/usr/bin/env python3

from sys import platform

__all__ = ("font", )

def get_font():
    if platform == "linux":
        return "FreeSans"
    else:
        #TODO: Need to test with this font
        return "Helvetica"

font = get_font()
