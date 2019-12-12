import textwrap
import click
from typing import List


def format_indented_paragraph(text: str, line_width: int) -> list:
    """Wrap a paragraph of text with approriate indentation on subsequent lines.

    Parameters
    ----------
    text : str
        The text to format.
    line_width : int
        The maximum width a line can be.

    Returns
    -------
    list of str
        The wrapped lines of text.
    """
    return textwrap.wrap(text, width=line_width, tabsize=4, subsequent_indent="    ")


def wrap_lines_paragraph(lines: List[str], line_width: int) -> List[str]:
    """Wrap any lines which are too long, indenting subsequent lines.

    Parameters
    ----------
    lines : list of str
        The lines of strings to wrap.
    line_width : int
        The maximum width a line can be.

    Returns
    -------
    list of str
        The wrapped lines of text.
    """
    output_lines = list()
    for line in lines:
        output_lines.extend(
            textwrap.wrap(line, width=line_width, tabsize=4, subsequent_indent="    ")
        )

    return output_lines


def format_list(title: str, items: list, line_width: int) -> list:
    """Join items with commas to create a text list, wrapping when necessary.

    Parameters
    ----------
    title : str
        The title to place at the start of the list.
    items : list of str
        List of the items
    line_width : int
        The maximum width a line can be.

    Returns
    -------
    list of str
        The wrapped lines of text.
    """
    # Create a text list of the items separated by commas
    item_list = ", ".join(items)
    # Add the title
    full_text = f"{title}: {item_list}"
    # Wrap the text
    return format_indented_paragraph(full_text, line_width)


def centre_pad(s, line_width):
    """Pad a string with spaces, centre-aligned."""
    return "{:^{width}}".format(s, width=line_width)


def display_panes(panes: List[List[str]], columns: int, column_width: int):
    """Display a set of panes in columns on the screen via click.

    Parameters
    ----------
    panes : list of list of str
        Each pane is represented by a list of lines (strings). This is a list of the
        data for each pane to be displayed.
    columns : int
        How many columns to display.
    column_width : int
        The width of each column, in characters.
    """

    # This returns a generator that will produce all of the lines for a particular
    # column on the screen until there are no more; after that, it will produce None
    # forever
    def line_for_column(column_index):
        for pane_index in range(column_index, len(panes), columns):
            yield from panes[pane_index]
        while True:
            yield None

    # This takes a list of strings, extends them with spaces to the column width, and
    # joins them together to produce a single string: a line for the whole-screen
    # display. If any items in the list are None, it will replace them with spaces for
    # the column width.
    def format_screen_line(line_parts):
        return "".join(
            [
                part.ljust(column_width) if part else " " * column_width
                for part in line_parts
            ]
        )

    # List of generators for each of the columns
    column_generators = [line_for_column(column) for column in range(columns)]

    # List of whole-screen lines
    screen_lines = []
    # Keep going until all of the columns are done
    while True:
        # Create a list of the strings from each pane that will make up this line
        line_parts = [next(column_generator) for column_generator in column_generators]
        # If all of the generators have run out of lines, stop
        if all(part is None for part in line_parts):
            break
        # Join the parts of the line to make a whole-screen line and append
        screen_lines.append(format_screen_line(line_parts))

    # Display the result
    click.echo_via_pager("\n".join(screen_lines))


def slugify(text):
    """Returns slug format of text, e.g. "Mug Of Coffee" -> mug-of-coffee"""
    return text.strip().lower().replace(" ", "-")
