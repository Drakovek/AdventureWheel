#!/usr/bin/env python3

from os import get_terminal_size, listdir, system, walk
from os import name as os_name
from os.path import abspath, basename, isdir, join
from time import sleep
from typing import List

def get_color(color:str=None) -> str:
    """
    Returns the ANSI escape character for turning text a given color.
    If a valid color character is not given, sets to the default terminal color.

    :param color: Character representing color, defaults to None
    :type color: str, optional
    :return: ANSI color character
    :rtype: str
    """
    if color == "r":
        # Red
        return "\033[31m"
    elif color == "g":
        # Green
        return "\033[32m"
    elif color == "b":
        # Blue
        return "\033[34m"
    elif color == "c":
        # Cyan
        return "\033[36m"
    elif color == "m":
        # Magenta
        return "\033[35m"
    elif color == "y":
        # Bright Yellow
        return "\033[93m"
    else:
        # Default
        return "\033[0m"

def wait_for_key_press():
    """
    Waits for a key press in the terminal.
    """
    input()

def clear_screen():
    """
    Clears the terminal of text.
    """
    if os_name == "nt":
        system("cls")
    else:
        system("clear")

def get_file_list(directory:str=None) -> List[List[str]]:
    """
    Returns a list of text files in a given directory and its subdirectories.
    Entries are listed as [AbsolutePath, Filename Minus Extension]

    :param directory: Directory in which to search for files, defaults to None
    :type directory: str, optional
    :return: List of text files in the given directory
    :rtype: list[list[str]]
    """
    # Return empty list if directory is invalid
    if directory is None:
        return []
    # Get all subdirectories within the given directory
    dirs = []
    path = abspath(directory)
    for p in walk(path):
        dirs.append(abspath(p[0]))
    # Get list of text files
    files = []
    for folder in dirs:
        for file in listdir(folder):
            if str(file).endswith(".txt"):
                files.append(abspath(join(folder, file)))
    # Add basenames to get file, filename pair
    files.sort()
    pairs = []
    for file in files:
        pairs.append([str(file), basename(file)[:-4]])
    # Return list of files
    return pairs

def read_file_as_lines(file:str=None) -> List[str]:
    """
    Reads a given text file and separates lines into separate list entries.

    :param file: Text file to read, defaults to None
    :type file: str, optional
    :return: List of lines in the given text file
    :rtype: str
    """
    # Return empty list if given file is invalid
    if file is None:
        return []
    # Read text file
    try:
        with open(file) as f:
            contents = f.read()
    except FileNotFoundError:
        # Return empty list if file doesn't exist
        return []
    # Separate into separate lines
    lines = contents.split("\n")
    # Remove any carriage return characters
    for i in range(0, len(lines)):
        lines[i] = lines[i].replace("\r", "")
    # Remove empty entries
    for i in range(len(lines)-1, -1, -1):
        if lines[i] == "":
            del lines[i]
    # Return lines
    return lines

def split_markers(string:str=None) -> List[str]:
    """
    Splits text into info markers and normal text.

    :param string: Text with info markers, defaults to None
    :type string: str, optional
    :return: List of strings with text and info markers separated
    :rtype: list[str]
    """
    # Return empty string if parameters are invalid
    if string is None:
        return []
    blocks = []
    left = string
    while len(left) > 0:
        # Find first marker start if available
        start = left.find("{{")
        if start == -1:
            start = len(left)
        # Add non-marker if available
        if start > 0:
            blocks.append(left[:start])
            left = left[start:]
        # Add marker block if available
        end = left.find("}}")
        if end == -1:
            end = len(left)
        else:
            end +=2
        blocks.append(left[:end])
        left = left[end:]
    # Remove empty entries
    size = len(blocks)
    for i in range(0, size):
        if blocks[i] == "":
            del blocks[i]
            i -= 1
    # Return blocks
    return blocks

def split_into_lines(string:str=None, width:int=5) -> List[str]:
    """
    Splits text into lines that fit the given width in characters.
    Ignores any info markers

    :param string: String to devide into lines, defaults to None
    :type string: str, optional
    :param width: Maximum width of a line in characters, defaults to 5
    :type width: int, optional
    :return: List of divided string lines
    :rtype: list[str]
    """
    # Return empty list if parameters are invalid
    if width < 2 or string is None:
        return []
    # Split out the speed and color markers
    blocks = split_markers(string)
    # Split text into sections based on spaces
    words = []
    for block in blocks:
        # Add spaces
        sections = block.split(" ")
        words.append(sections[0])
        size = len(sections)
        for i in range(1, size):
            words.append(" " + sections[i])
    # Set lines
    lines = [""]
    size = 0
    while len(words) > 0:
        # Check if line is already too long
        if size > width:
            size = (size - width) + 1
            leftover = lines[-1][-1*size:]
            lines[-1] = lines[-1][:-1*size] + "-"
            lines.append(leftover)
            continue
        # Add mark without counting towards line size if present
        if words[0].startswith("{{"):
            lines[-1] = lines[-1] + words[0]
            del words[0]
            continue
        # Check if current line is full
        new_total = size + len(words[0])
        if new_total > width:
            # Create new line if line is too long
            lines.append(words[0])
            if lines[-1].startswith(" "):
                lines[-1] = lines[-1][1:]
            size = len(lines[-1])
        else:
            # Add word to line
            lines[-1] = lines[-1] + words[0]
            size = new_total
        del words[0]
    # Make sure last line isn't too long
    while size > width:
        size = (size - width) + 1
        leftover = lines[-1][-1*size:]
        lines[-1] = lines[-1][:-1*size] + "-"
        lines.append(leftover)
    # Remove empty lines
    i = 0
    while i < len(lines):
        if lines[i] == "":
            del lines[i]
            continue
        i += 1
    # Return lines
    return lines

def replace_speed_markers(string:str=None, multiplier:float=1) -> str:
    """
    Replaces the text speed markers in given text.
    Multiplies the speed values by a given multiplier.

    :param string: String in which to replace speed markers, defaults to None
    :type string: str, optional
    :param multiplier: Value to multiply existing speed markers by, defaults to 1
    :type multiplier: float, optional
    :return: Text with speed markers replaced
    :rtype: str
    """
    # Don't bother replacing markers if multiplyer is 1
    if multiplier == 1:
        return string
    # Split into markers and non-markers
    chunks = split_markers(string)
    # Replace text speed markers using the multiplier
    replaced = ""
    for chunk in chunks:
        if chunk.startswith("{{"):
            try:
                value = float(chunk[2:-2]) * multiplier
                replaced = replaced + "{{" + str(value) + "}}"
            except ValueError:
                replaced = replaced + chunk
        else:
            replaced = replaced + chunk
    # Returns the replaced string
    return replaced

def add_escapes(string:str=None, width:int=5,
                include_color:bool=True,
                include_speed:bool=True) -> str:
    """
    Adds new line and color escape characters to a given string.

    :param string: String to modify, defaults to None
    :type string: str, optional
    :param width: Width of each line in characters, defaults to 5
    :type width: int, optional
    :param include_color: Whether to include color escape characters, defaults to True
    :type include_color: bool, optional
    :param include_speed: Whether to include variable text speed, defaults to True
    :type include_speed: bool, optional
    :return: String with new line and color escape characters added
    :rtype: str
    """
    # Split into lines
    lines = split_into_lines(string, width)
    # Return empty string if lines are empty
    if lines == []:
        return ""
    # Combine lines with new line characters
    escaped = lines[0]
    size = len(lines)
    for i in range(1, size):
        escaped = escaped + "\n" + lines[i]
    # Replace color markers
    if include_color:
        escaped = escaped.replace("{{r}}", get_color("r"))
        escaped = escaped.replace("{{g}}", get_color("g"))
        escaped = escaped.replace("{{b}}", get_color("b"))
        escaped = escaped.replace("{{c}}", get_color("c"))
        escaped = escaped.replace("{{m}}", get_color("m"))
        escaped = escaped.replace("{{y}}", get_color("y"))
        escaped = escaped.replace("{{d}}", get_color("d"))
    else:
        escaped = escaped.replace("{{r}}", "")
        escaped = escaped.replace("{{g}}", "")
        escaped = escaped.replace("{{b}}", "")
        escaped = escaped.replace("{{c}}", "")
        escaped = escaped.replace("{{m}}", "")
        escaped = escaped.replace("{{y}}", "")
        escaped = escaped.replace("{{d}}", "")
    # Remove speed markers if specified
    if not include_speed:
        escaped = "{{0}}" + replace_speed_markers(escaped, 0)
    # Return text with escape characters
    return escaped

def get_characters(lines:List[str]=None) -> List[List]:
    """
    Returns a list of character entries based list of strings read from characters file.
    Character entries are returned as [variable-name(str), name(str), color(str), text-speed(float)]

    :param lines: Lines of text read from characters file, defaults to None
    :type lines: str, optional
    :return: List of character entries
    :rtype: list[list]
    """
    # Return empty string if parameters are invalid
    if lines is None:
        return []
    characters = []
    # Run through each line
    for line in lines:
        # split info in the line into sections
        info = line.split("|")
        # Skip character if number of entries is incorrect
        if not len(info) == 4:
            continue
        # Get the variable name for the character
        if info[0] == "":
            continue
        character = [str(info[0])]
        # Get the character name
        if info[1] == "":
            continue
        character.append(str(info[1]))
        # Get the character color
        if not len(info[2]) == 1:
            continue
        character.append(str(info[2]))
        # Get the character text speed
        try:
            character.append(float(info[3]))
        except ValueError:
            continue
        # Append the character to the list of characters
        characters.append(character)
    # Return the list of characters
    return characters

def format_story_text(lines:List[str]=None,
                chars:List[list]=None) -> List[str]:
    """
    Formats story text by adding character info and removing whitespace.

    :param lines: Lines read from a story text file, defaults to None
    :type lines: list[str], optional
    :param chars: Character list as gotten from get_characters(), defaults to None
    :type chars: list[list], optional
    :return: List of formatted text in lines
    :rtype: list[str]
    """
    # Return empty list if parameters are invalid
    if lines is None or chars is None:
        return []
    # Run through each line
    formatted = []
    prev_char = ""
    next_line = ""
    for line in lines:
        cur_char = ""
        if line is None or line == "":
            # Skip over line if it is empty
            continue
        elif line.endswith("\""):
            # Treat as standard text if line starts with quote
            if line.startswith("\""):
                next_line = line[1:-1]
            else:
                # Split character var name and text
                index = line.find("\"")
                cur_char = line[:index]
                text = line[index+1:-1]
                # Get character information
                character = None
                for char in chars:
                    if char[0] == cur_char:
                        character = char
                        break
                if character is None:
                    formatted.append(line)
                    continue
                # Combine into text
                text = replace_speed_markers(text, character[3])
                final_text = "{{0}}{{" + character[2] + "}}"
                final_text = final_text + character[1] + ": {{d}}"
                final_text = final_text + "{{" + str(character[3]) + "}}"
                final_text = final_text + text
                next_line = final_text
        else:
            # Add current line unaltered if not quoted text
            next_line = line
        # Add empty line if characters aren't equal
        if not cur_char == prev_char:
            formatted.append("{{0}}")
        prev_char = cur_char
        formatted.append(next_line)
    # Remove empty lines from beginning of list
    while len(formatted) > 0 and formatted[0] == "{{0}}":
        del formatted[0]
    # Return formatted list of text
    return formatted

def print_by_char(string:str=None):
    """
    Prints a given string character by character.
    Divides into lines that fit in terminal and follows text markers.

    :param string: String to print character by character, defaults to None
    :type string: str, optional
    """
    # Add escape characters to text
    width = get_terminal_size()[0]
    escaped = add_escapes(string, width)
    # Split into markers
    blocks = split_markers(escaped)
    timeout = 0.02
    # Print character by character
    for block in blocks:
        if block.startswith("{{"):
            try:
                timeout = float(block[2:-2]) * 0.02
            except ValueError:
                timeout = 0.02
            continue
        else:
            size = len(block)
            for i in range(0, size):
                print(block[i], end="", flush=True)
                sleep(timeout)
    # Move to a new line and reset default color
    print(get_color("d"))

def get_link_options(lines:List[str]=None, print_lines:bool=True) -> List[List[str]]:
    """
    Returns a list of the available options from given story text.
    Options formatted [filename|display name]

    :param lines: Story text read from file, defaults to None
    :type lines: list[str], optional
    :param print_lines: Whether to print given text, defaults to True
    :type ptint_lines: bool, optional
    :return: Available options for a user to choose
    :rtype: list[list[str]]
    """
    # Return empty list if parameters are invalid
    if lines is None:
        return []
    # Run through all lines
    text = []
    options = []
    for line in lines:
        if line.startswith("[[") and line.endswith("]]"):
            # Add option to the list of options
            options.append(line[2:-2])
        else:
            # Add standard story text to the list of text
            text.append(line)
    # Split into full options
    full_options = []
    for option in options:
        split = option.split("|")
        if len(split) == 2:
            full_options.append(split)
    # Print string if specified
    if print_lines:
        for line in text:
            if line == "{{0}}":
                wait_for_key_press()
                continue
            print_by_char(line)
    # Return full options
    return full_options

def get_decision_text(options:List[List[str]]=None,
                visited_links:List[str]=None) -> List[str]:
    """
    Returns text to show for the user to make a decision.
    Based on options list, formated [link, name]
    Colors options based on whether links have been visited already.

    :param options: Options list, defaults to None
    :type options: list[list[str]], optional
    :param visited_links: List of link names that have been visited, defaults to None
    :type visited_links: list[str], optional
    :return: List of lines containing each option
    :rtype: list[str]
    """
    # Return empty list if options are invalid
    if options is None:
        return []
    # Get colors based on whether links have been visited
    colors = []
    for option in options:
        try:
            link = option[0]
            if link in visited_links:
                # Set color to green if visited
                colors.append("{{g}}")
                continue      
        except (IndexError, TypeError): pass
        # Set color to blue if not visited or invalid
        colors.append("{{b}}")
    # Create text based on decisions available
    text = []
    link_num = 1
    for i in range(0, len(options)):
        try:
            name = options[i][1]
            text.append("{{0}}" + str(link_num) + ") " + colors[i] + name + "{{d}}")
        except (IndexError, TypeError):
            continue
        link_num += 1
    # Return the text
    return text

def get_file_by_name(name:str=None, files:List[List[str]]=None) -> List[str]:
    """
    Returns the contents of the text file in the file list with a given name.
    Name should not include the .txt extension.

    :param name: Name to search for in file list, defaults to None
    :type name: str, optional
    :param files: List of files as gotten from get_file_list, defaults to None
    :type files: list[list[str]]
    :return: Contents of the text file with given name.
    :rtype: list[str]
    """
    # Return empty list if paramaters are invalid
    if name is None or files is None:
        return []
    # Get the path of the file with the given name
    path = None
    for file in files:
        if file[1] == name:
            path = file[0]
            break
    # Read the text file and return the contents
    lines = read_file_as_lines(path)
    return lines

def get_next_story(lines:List[str]=None, characters:List[List[str]]=None) -> str:
    """
    Prints the next part of the story, and returns which choice the user picked.

    :param lines: Lines of story text to print, defaults to None
    :type lines: list[str], optional
    :param characters: Character info as gotten from get_characters, defaults to None
    :type characters: list[list[str]]
    :return: File name of the option chosen by the user, without extension
    :rtype: str
    """
    # Format the story text
    new_lines = format_story_text(lines, characters)
    # Get link options and print text
    options = get_link_options(new_lines, True)
    # Print decision text, if necessary
    if len(options) > 1:
        print()
        decision_lines = get_decision_text(options, [])
        for line in decision_lines:
            print_by_char(line)
    # Return empty string if there are no options to choose
    if options == []:
        return ""
    # Get player decision
    decision = 0
    if len(options) > 1:
        decision = None
        while decision is None:
            try:
                decision = int(input("> ")) - 1
                if decision < 0 or decision > (len(options)-1):
                    decision = None
            except ValueError:
                decision = None
        clear_screen()
    else:
        print()
    # Return name of the chosen decision
    return options[decision][0]

def load_story(directory:str=None) -> bool:
    """
    Loads the story and starts the game.

    :param directory: Directory in which to look for story files, defualts to None
    :type directory: str, optional
    :return: Whether reading story files was successful or not.
    :rtype: bool
    """
    # Return False if directory is invalid
    if directory is None or not isdir(directory):
        return False
    # Get list of story files
    files = get_file_list(directory)
    # Read character file
    lines = get_file_by_name("characters", files)
    characters = get_characters(lines)
    # Return False if no character info was found
    if characters == []:
        print("Invalid character file.")
        return False
    # Start running the story
    clear_screen()
    next_story = "start"
    while not next_story == "":
        lines = get_file_by_name(next_story, files)
        next_story = get_next_story(lines, characters)
    # Return True once story has completed
    return True
