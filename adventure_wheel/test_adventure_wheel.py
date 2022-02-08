#!/usr/bin/env python3

from adventure_wheel.adventure_wheel import add_escapes
from adventure_wheel.adventure_wheel import format_story_text
from adventure_wheel.adventure_wheel import get_characters
from adventure_wheel.adventure_wheel import get_color
from adventure_wheel.adventure_wheel import get_decision_text
from adventure_wheel.adventure_wheel import get_file_by_name
from adventure_wheel.adventure_wheel import get_file_list
from adventure_wheel.adventure_wheel import get_link_options
from adventure_wheel.adventure_wheel import read_file_as_lines
from adventure_wheel.adventure_wheel import replace_speed_markers
from adventure_wheel.adventure_wheel import split_into_lines
from adventure_wheel.adventure_wheel import split_markers
from os import mkdir, pardir
from os.path import abspath, basename, exists, join
from tempfile import gettempdir
from shutil import rmtree

def get_test_dir() -> str:
    """
    Creates and returns test directory.

    :return: File path of the test directory
    :rtype: str
    """
    test_dir = abspath(join(abspath(gettempdir()), "advwheel_test"))
    if(exists(test_dir)):
        rmtree(test_dir)
    mkdir(test_dir)
    return test_dir

def test_get_color():
    """
    Tests the get_color function.
    """
    # Test getting color escape values
    assert get_color("r") == "\033[31m"
    assert get_color("g") == "\033[32m"
    assert get_color("b") == "\033[34m"
    assert get_color("c") == "\033[36m"
    assert get_color("m") == "\033[35m"
    assert get_color("y") == "\033[93m"
    assert get_color("d") == "\033[0m"
    # Test getting invalid color
    assert get_color(None) == "\033[0m"
    assert get_color("blah") == "\033[0m"
    assert get_color("") == "\033[0m"
    assert get_color() == "\033[0m"

def test_split_markers():
    """
    Tests the split markers function.
    """
    # Test separating markers from text.
    marks = split_markers("{{0.5}}Things and {{y}}text{{g}}.")
    assert marks == ["{{0.5}}", "Things and ", "{{y}}", "text", "{{g}}", "."]
    marks = split_markers("Words{{inside}} thing.{{0.2}}")
    assert marks == ["Words", "{{inside}}", " thing.", "{{0.2}}"]
    # Test that single curly brackets aren't counted
    marks = split_markers("{Not} actually {markers}.")
    assert marks == ["{Not} actually {markers}."]
    marks = split_markers("{Only} One {{g}} marker")
    assert marks == ["{Only} One ", "{{g}}", " marker"]
    # Test separating marks that are incomplete
    marks = split_markers("{{r}}Word {{Incomplete")
    assert marks == ["{{r}}", "Word ", "{{Incomplete"]
    marks = split_markers("A{{b}} c {{D}")
    assert marks == ["A", "{{b}}", " c ", "{{D}"]
    marks = split_markers("Thing}} and {{d}}stuff")
    assert marks == ["Thing}} and ", "{{d}}", "stuff"]
    # Test separating marks with invalid parameters
    assert split_markers("") == []
    assert split_markers(None) == []
    assert split_markers() == []

def test_split_into_lines():
    """
    Tests the split_into_lines function.
    """
    # Test splitting text into lines
    lines = split_into_lines("Some words and stuff.", 10)
    assert lines == ["Some words", "and stuff."]
    lines = split_into_lines("How about a slightly longer sentence?", 10)
    assert lines == ["How about", "a slightly", "longer", "sentence?"]
    # Test splitting text with info markers included
    lines = split_into_lines("{{g}}What about this {{longer}}thing?", 12)
    assert lines == ["{{g}}What about", "this {{longer}}thing?"]
    # Test when individual word is too long for a line
    lines = split_into_lines("This humongous bit is just too lengthy.", 7)
    assert lines == ["This", "humong-", "ous bit", "is just", "too", "length-", "y."]
    lines = split_into_lines("Absolutely totally redicoulonculous.", 8)
    assert lines == ["Absolut-", "ely", "totally", "redicou-", "lonculo-", "us."]
    # Test splitting lines with invalid parameters
    assert split_into_lines("This is a sentence", 0) == []
    assert split_into_lines("This is a sentence", 1) == []
    assert split_into_lines("", 10) == []
    assert split_into_lines(None, 10) == []

def test_add_escapes():
    """
    Tests the add_escapes function.
    """
    # Test adding new line characters in text
    escaped = add_escapes("Some words and stuff", 10)
    assert escaped == "Some words\nand stuff"
    escaped = add_escapes("How about a slightly longer sentence?", 10)
    assert escaped == "How about\na slightly\nlonger\nsentence?"
    # Test replacing color markers with ANSI color codes
    escaped = add_escapes("{{r}}Word{{g}}Things{{b}}stuff", 40)
    assert escaped == "\033[31mWord\033[32mThings\033[34mstuff"
    escaped = add_escapes("{{c}}Word{{m}}Things{{y}}stuff", 40)
    assert escaped == "\033[36mWord\033[35mThings\033[93mstuff"
    escaped = add_escapes("{{d}}More {{r}}stuff.{{d}}", 30)
    assert escaped == "\033[0mMore \033[31mstuff.\033[0m"
    # Test replacing markers with new lines
    escaped = add_escapes("Some {{g}}words and stuff", 10)
    assert escaped == "Some \033[32mwords\nand stuff"
    # Test removing color markers if specified
    escaped = add_escapes("{{r}}Some{{g}}Words{{b}}Colored", 40, include_color=False)
    assert escaped == "SomeWordsColored"
    escaped = add_escapes("{{c}}More{{m}}Words{{y}}Colored{{d}}", 40, include_color=False)
    assert escaped == "MoreWordsColored"
    # Test removing text speed markers if specified
    escaped = add_escapes("{{2}}Speed {{1}}up?", 40, include_speed=True)
    assert escaped == "{{2}}Speed {{1}}up?"
    escaped = add_escapes("Speed {{4}}up{{22}}?", 40, include_speed=False)
    assert escaped == "{{0}}Speed {{0.0}}up{{0.0}}?"
    # Test adding escapes with invalid parameters
    assert add_escapes("Some words", 0) == ""
    assert add_escapes("Some words", 1) == ""
    assert add_escapes("", 10) == ""
    assert add_escapes(None, 10) == ""
    assert add_escapes(width=10) == ""

def test_get_characters():
    """
    Tests the get_characters function.
    """
    # Test getting characters with valid formatting
    chars = get_characters(["jn|John|b|1", "mg|Megan|y|0.5", "un|Unknown|m|2"])
    assert len(chars) == 3
    assert chars[0] == ["jn", "John", "b", 1]
    assert chars[1] == ["mg", "Megan", "y", 0.5]
    assert chars[2] == ["un", "Unknown", "m", 2]
    # Test getting characters with incorrect number of entries
    chars = get_characters(["John", "", "p|person", "mk|Mike|b|3", "b|Blah|thing|1|other"])
    assert len(chars) == 1
    assert chars[0] == ["mk", "Mike", "b", 3]
    # Test getting characters with invalid variable name
    chars = get_characters(["j|James|g|1.0", "|Person|r|4"])
    assert len(chars) == 1
    assert chars[0] == ["j", "James", "g", 1]
    # Test getting characters with invalid name
    chars = get_characters(["bl||r|0.25", "mk|Mike|m|0.125"])
    assert len(chars) == 1
    assert chars[0] == ["mk", "Mike", "m", 0.125]
    # Test getting characters with invalid color code
    chars = get_characters(["ps|Person|green|2", "j|Joe|r|2", "l|Liz||3"])
    assert len(chars) == 1
    assert chars[0] == ["j", "Joe", "r", 2]
    # Test getting characters with invalid text speed
    chars = get_characters(["jn|John|b|notnumber", "mk|Mike|r|", "s|Susan|g|3"])
    assert len(chars) == 1
    assert chars[0] == ["s", "Susan", "g", 3]
    # Test getting characters with invalid parameters
    assert get_characters([]) == []
    assert get_characters(None) == []
    assert get_characters() == []

def test_replace_multipliers():
    """
    Tests the replace_multipliers function.
    """
    # Test replacing the speed markers in text
    text = replace_speed_markers("{{1}}Here's some {{0.5}}text.", 2)
    assert text == "{{2.0}}Here's some {{1.0}}text."
    text = replace_speed_markers("{{0.5}}More {{5.25}} text!", 0.5)
    assert text == "{{0.25}}More {{2.625}} text!"
    text = replace_speed_markers("{{5}}Words.", 0)
    assert text == "{{0.0}}Words."
    # Test replacing speed markers when other markers are present
    text = replace_speed_markers("{{0}}Some{{g}}Colored {{2}} {{r}}text!", 3)
    assert text == "{{0.0}}Some{{g}}Colored {{6.0}} {{r}}text!"
    # Test replacing with invalid/incomplete markers
    text = replace_speed_markers("{{r}}{{2}}Thing! {{blah", 0.25)
    assert text == "{{r}}{{0.5}}Thing! {{blah"
    text = replace_speed_markers("{{4}}Word {{", 0.5)
    assert text == "{{2.0}}Word {{"
    text = replace_speed_markers("}} {{b}}Thing{{1.25}}.", 2)
    assert text == "}} {{b}}Thing{{2.5}}."
    # Test replacing speed markers with multiplier of 1
    text = replace_speed_markers("{{1}}Thing{{2}}Other{{2.4}}", 1)
    assert text == "{{1}}Thing{{2}}Other{{2.4}}"
    # Test replacing with no speed markers
    text = replace_speed_markers("{{r}}Words!{{g}} But no speed.", 2)
    assert text == "{{r}}Words!{{g}} But no speed."
    # Test replacing speed markers with invalid parameters
    assert replace_speed_markers("", 2) == ""
    assert replace_speed_markers(None, 2) == ""
    assert replace_speed_markers(multiplier=2) == ""

def test_format_story_text():
    """
    Tests the format_story_text function.
    """
    # Test formatting story text in quotes
    story = format_story_text(["\"Some words\"", "\"More words!\""], [])
    assert story == ["Some words", "More words!"]
    # Test formatting text with characters
    chars = [["jn", "John", "b", 1.0], ["lz", "Liz", "g", 2.0]]
    story = format_story_text(["jn\"Words!\"", "lz\"Other {{0.5}}words\""], chars)
    assert len(story) == 2
    assert story[0] == "{{0}}{{b}}John: {{d}}{{1.0}}Words!"
    assert story[1] == "{{0}}{{g}}Liz: {{d}}{{2.0}}Other {{1.0}}words"
    # Test formatting text with incomplete quotations
    story = format_story_text(["\"Incomplete line.", "Another incomplete\""], [])
    assert story == ["\"Incomplete line.", "Another incomplete\""]
    story = format_story_text(["lz\"Not closed"], chars)
    assert story == ["lz\"Not closed"]
    # Test formatting text with no matching character
    story = format_story_text(["nn\"No matching character\""], chars)
    assert story == ["nn\"No matching character\""]
    # Test formatting text with extraneous lines
    story = format_story_text(["\"Quote\"", "No quote", "[[Link]]"], [])
    assert story == ["Quote", "No quote", "[[Link]]"]
    # Test formatting text with empty lines
    story = format_story_text(["Some", "", None, "Lines"], chars)
    assert story == ["Some", "Lines"]
    # Test formatting text with invalid parameters
    assert format_story_text([], []) == []
    assert format_story_text([], chars) == []
    assert format_story_text(None, chars) == []
    assert format_story_text(["Word"], None) == []
    assert format_story_text() == []

def test_get_link_options():
    """
    Tests the get_link_options function.
    """
    # Test getting options
    text = ["[Not a link]", "[[word|Word!]]", "other", "[[thing|Thing?]]"]
    options = get_link_options(text, False)
    assert options == [["word", "Word!"], ["thing", "Thing?"]]
    # Test getting options when links aren't properly formatted
    text = ["[[link]]", "[[other|Thing|2]]", "[[next|Next.]]"]
    options = get_link_options(text, False)
    assert options == [["next", "Next."]]
    text = ["[[link|next", "other|link]]", "", "[[start|Start]]"]
    options = get_link_options(text, False)
    assert options == [["start", "Start"]]
    # Test geting options when none are available
    text = ["[[Not|link]", "[Not|link]]", "[Not|link]"]
    options = get_link_options(text, False)
    assert options == []
    # Test getting options with invalid parameters
    assert get_link_options([]) == []
    assert get_link_options(None) == []
    assert get_link_options() == []

def test_get_decision_text():
    """
    Tests the get_decision_text function.
    """
    # Test getting decision text with no visited links
    options = [["link", "Path 1"], ["other", "Path 2"], ["next", "Path 3"]]
    text = get_decision_text(options, [])
    assert len(text) == 3
    assert text[0] == "{{0}}1) {{b}}Path 1{{d}}"
    assert text[1] == "{{0}}2) {{b}}Path 2{{d}}"
    assert text[2] == "{{0}}3) {{b}}Path 3{{d}}"
    # Test getting decision text with visited links
    visited = ["not", "included", "Next", "link", "still"]
    text = get_decision_text(options, visited)
    assert len(text) == 3
    assert text[0] == "{{0}}1) {{g}}Path 1{{d}}"
    assert text[1] == "{{0}}2) {{b}}Path 2{{d}}"
    assert text[2] == "{{0}}3) {{b}}Path 3{{d}}"
    # Test getting decision text with invalid option links
    options.append([])
    options.append(None)
    options.append(["short"])
    options.append(["still", "Valid", "but", "long"])
    text = get_decision_text(options, visited)
    assert len(text) == 4
    assert text[0] == "{{0}}1) {{g}}Path 1{{d}}"
    assert text[1] == "{{0}}2) {{b}}Path 2{{d}}"
    assert text[2] == "{{0}}3) {{b}}Path 3{{d}}"
    assert text[3] == "{{0}}4) {{g}}Valid{{d}}"
    # Test getting desicion text with invalid visited links
    text = text = get_decision_text(options, None)
    assert len(text) == 4
    assert text[0] == "{{0}}1) {{b}}Path 1{{d}}"
    assert text[1] == "{{0}}2) {{b}}Path 2{{d}}"
    assert text[2] == "{{0}}3) {{b}}Path 3{{d}}"
    assert text[3] == "{{0}}4) {{b}}Valid{{d}}"
    # Test getting desision text with invalid parameters
    assert get_decision_text([], visited) == []
    assert get_decision_text(None, visited) == []

def test_get_file_list():
    """
    Tests the get_file_list function.
    """
    # Create test directories
    test_dir = get_test_dir()
    main_sub = abspath(join(test_dir, "sub"))
    mkdir(main_sub)
    inner_one = abspath(join(main_sub, "one"))
    mkdir(inner_one)
    inner_two = abspath(join(main_sub, "two"))
    mkdir(inner_two)
    # Create test files
    inner_file = abspath(join(inner_one, "inner.txt"))
    with open(inner_file, "w") as out_file:
        out_file.write("TEST")
    other_file = abspath(join(inner_one, "other.txt"))
    with open(other_file, "w") as out_file:
        out_file.write("TEST")
    not_text = abspath(join(inner_two, "not_text.png"))
    with open(not_text, "w") as out_file:
        out_file.write("TEST")
    sub_text = abspath(join(main_sub, "sub_text.txt"))
    with open(sub_text, "w") as out_file:
        out_file.write("TEST")
    main_text = abspath(join(test_dir, "main_text.txt"))
    with open(main_text, "w") as out_file:
        out_file.write("TEST")
    # Test that files were created
    assert exists(inner_file)
    assert exists(other_file)
    assert exists(not_text)
    assert exists(sub_text)
    assert exists(main_text)
    # Test getting files in single folder
    files = get_file_list(inner_one)
    assert len(files) == 2
    assert len(files[0]) == 2
    assert basename(files[0][0]) == "inner.txt"
    assert abspath(join(files[0][0], pardir)) == abspath(inner_one)
    assert files[0][1] == "inner"
    assert len(files[1]) == 2
    assert basename(files[1][0]) == "other.txt"
    assert abspath(join(files[1][0], pardir)) == abspath(inner_one)
    assert files[1][1] == "other"
    # Test getting files with some non-text files
    assert get_file_list(inner_two) == []
    # Test getting files in subfolders
    files = get_file_list(test_dir)
    assert len(files) == 4
    print(files)
    assert basename(files[0][0]) == "main_text.txt"
    assert abspath(join(files[0][0], pardir)) == abspath(test_dir)
    assert files[0][1] == "main_text"
    assert basename(files[1][0]) == "inner.txt"
    assert abspath(join(files[1][0], pardir)) == abspath(inner_one)
    assert files[1][1] == "inner"
    assert basename(files[2][0]) == "other.txt"
    assert abspath(join(files[2][0], pardir)) == abspath(inner_one)
    assert files[2][1] == "other"
    assert basename(files[3][0]) == "sub_text.txt"
    assert abspath(join(files[3][0], pardir)) == abspath(main_sub)
    assert files[3][1] == "sub_text"
    # Test getting files from non-existant folder
    non_dir = abspath(join(main_sub, "non_dir"))
    assert get_file_list(non_dir) == []
    # Test getting files with invalid parameters
    assert get_file_list(None) == []
    assert get_file_list() == []

def test_read_file_as_lines():
    """
    Tests the read_file_as_lines function.
    """
    # Create test files
    test_dir = get_test_dir()
    one_line = abspath(join(test_dir, "one.txt"))
    with open(one_line, "w") as out_file:
        out_file.write("text")
    multiline = abspath(join(test_dir, "multi.txt"))
    with open(multiline, "w") as out_file:
        out_file.write("Line One\nNext\nThird")
    carriage = abspath(join(test_dir, "carriage.txt"))
    with open(carriage, "w") as out_file:
        out_file.write("Carriage\r\nReturn\n\rThings\r")
    # Test that files were created
    assert exists(one_line)
    assert exists(multiline)
    assert exists(carriage)
    # Test reading file with only one line
    lines = read_file_as_lines(one_line)
    assert lines == ["text"]
    # Test reading file with multiple lines
    lines = read_file_as_lines(multiline)
    assert lines == ["Line One", "Next", "Third"]
    # Test reading file with carriage returns
    lines = read_file_as_lines(carriage)
    assert lines == ["Carriage", "Return", "Things"]
    # Test reading non-existant file
    non_existant = abspath(join(test_dir, "non.txt"))
    assert read_file_as_lines(non_existant) == []
    # Test reading file with invalid parameters
    assert read_file_as_lines(None) == []
    assert read_file_as_lines() == []

def test_get_file_by_name():
    """
    Tests the get_file_by_name function.
    """
    # Create test files
    test_dir = get_test_dir()
    one_line = abspath(join(test_dir, "one.txt"))
    with open(one_line, "w") as out_file:
        out_file.write("text")
    multiline = abspath(join(test_dir, "multi.txt"))
    with open(multiline, "w") as out_file:
        out_file.write("Line One\nNext\nThird")
    carriage = abspath(join(test_dir, "carriage.txt"))
    with open(carriage, "w") as out_file:
        out_file.write("Carriage\r\nReturn\n\rThings\r")
    # Test that files were created
    assert exists(one_line)
    assert exists(multiline)
    assert exists(carriage)
    # Test getting file by name
    files = get_file_list(test_dir)
    lines = get_file_by_name("one", files)
    assert lines == ["text"]
    lines = get_file_by_name("multi", files)
    assert lines == ["Line One", "Next", "Third"]
    lines = get_file_by_name("carriage", files)
    assert lines == ["Carriage", "Return", "Things"]
    # Test getting file if name isn't included
    lines = get_file_by_name("not_included", files)
    assert lines == []
    # Test getting file if file doesn't exist
    files.append(["/non/existant/name.txt", "name"])
    lines = get_file_by_name("name", files)
    assert lines == []
    # Test getting file with invalid parameters
    assert get_file_by_name("one", None) == []
    assert get_file_by_name(None, files) == []
    assert get_file_by_name(None, None) == []
    assert get_file_by_name("", files) == []
