#!/usr/bin/env python3

from adventure_wheel.adventure_wheel import load_story
from os import getcwd

if __name__ == "__main__":
    load_story(getcwd())
