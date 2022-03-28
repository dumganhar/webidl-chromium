#!/usr/bin/env python
# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Print a diff generated by generate_idl_diff.py.
Before printing, sort the diff in the alphabetical order or the order of
diffing tags.
Usage: print_idl_diff.py diff_file.json order
    diff.json:
        Output of generate_idl_diff.py. The json file contains a dictionary
        that represents a diff between two different Chromium versions. The
        structure of the dictionary is like below.
    order:
        Specify how to sort. Either by "ALPHABET" or "TAG".
"""

from collections import OrderedDict
import sys

from blinkpy.bindings.generate_idl_diff import load_json_file
from blinkpy.bindings.generate_idl_diff import EXTATTRIBUTES_AND_MEMBER_TYPES
from blinkpy.bindings.generate_idl_diff import DIFF_TAG
from blinkpy.bindings.generate_idl_diff import DIFF_TAG_ADDED
from blinkpy.bindings.generate_idl_diff import DIFF_TAG_DELETED


# pylint: disable=W0105
"""Refer to the explanation of generate_idl_diff.py's input files.
The deffference between the input structure of generate_idl_diff.py and
that of print_diff.py is whether diffing tags are included or not.
    {'Interface': {
            'diff_tag': 'deleted'
            'ExtAttributes': [{'Name': '...'
                               'diff_tag': 'deleted'},
                               ...,
                             ],
            'Consts': [{'Type': '...',
                        'Name': '...',
                        'Value': '...'
                        'diff_tag': 'deleted'},
                        ...,
                      ],
            'Attributes': [{'Type': '...',
                            'Name': '...',
                            'ExtAttributes':[{'Name': '...'},
                                              ...,
                                            ]
                            'diff_tag': 'deleted'},
                            ...,
                          ],
            'Operations': [{'Type': '...',
                            'Name': '...',
                            'ExtAttributes':[{'Name': '...'},
                                              ...,
                                            ],
                            'Arguments': [{'Type': '...',
                                           'Name': '...'},
                                           ...,
                                         ]
                            'diff_tag': 'deleted'},
                            ...,
                          ],
            'Name': '...'
        },
        {
            'ExtAttributes': [{'Name': '...'},
                               ...,
                             ],
            'Consts': [{'Type': '...',
                        'Name': '...',
                        'Value': '...'
                        'diff_tag': 'added'},
                        ...,
                      ],
            'Attributes': [{'Type': '...',
                            'Name': '...',
                            'ExtAttributes':[{'Name': '...'},
                                              ...,
                                            ]},
                            ...,
                          ],
            'Operations': [{'Type': '...',
                            'Name': '...',
                            'ExtAttributes':[{'Name': '...'},
                                              ...,
                                            ],
                            'Arguments': [{'Type': '...',
                                           'Name': '...'},
                                           ...,
                                         ]
                            'diff_tag': 'deleted'},
                            ...,
                           ],
            'Name': '...'
        },
        ...,
    }
"""


class Colorize(object):
    """This class outputs a colored text to sys.stdout.
    TODO(bashi): This class doesn't work on Windows. Provide a way to suppress
    escape sequences.
    """

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    COLORS = (BLACK, RED, GREEN, YELLOW)

    def __init__(self, out):
        self.out = out

    def reset_color(self):
        """Reset text's color to default."""
        self.out.write('\033[0m')

    def change_color(self, color):
        """Change text's color by specifing arguments.
            Args:
                color: A new color to change. It should be one of |COLORS|.
        """
        if color in self.COLORS:
            self.out.write('\033[' + str(color) + 'm')
        else:
            raise Exception('Unsupported color.')

    def writeln(self, string):
        """Print text with a line-break."""
        self.out.write(string + '\n')

    def write(self, string):
        """Print text without a line-break."""
        self.out.write(string)


def sort_member_types(interface):
    """Sort the members in the order of EXTATTRIBUTES_AND_MEMBER_TYPES.
    Args:
        interface: An "interface" object
    Returns:
        A sorted "interface" object
    """
    sorted_interface = OrderedDict()
    for member_type in EXTATTRIBUTES_AND_MEMBER_TYPES:
        sorted_interface[member_type] = interface.get(member_type)
    sorted_interface[DIFF_TAG] = interface.get(DIFF_TAG)
    return sorted_interface


def group_by_tag(interface_or_member_list):
    """Group members of |interface_or_member_list| by tags.
    Args:
        interface_or_member_list: A list of interface names or a list of "members"
    Returns:
        A tuple of (removed, added, unchanged) where
        removed: A list of removed members
        added: A list of added members
        unspecified: A list of other members
    """
    removed = []
    added = []
    unspecified = []
    for interface_or_member in interface_or_member_list:
        if DIFF_TAG in interface_or_member:
            if interface_or_member[DIFF_TAG] == DIFF_TAG_DELETED:
                removed.append(interface_or_member)
            elif interface_or_member[DIFF_TAG] == DIFF_TAG_ADDED:
                added.append(interface_or_member)
        else:
            unspecified.append(interface_or_member)
    return (removed, added, unspecified)


def sort_interface_names_by_tags(interfaces):
    """Sort interface names as follows.
    [names of deleted "interface"s
    -> names of added "interface"s
    -> names of other "interface"s]
    Args:
        interfaces: "interface" objects.
    Returns:
        A list of sorted interface names
    """
    interface_list = interfaces.values()
    removed, added, unspecified = group_by_tag(interface_list)
    # pylint: disable=W0110
    removed = map(lambda interface: interface['Name'], removed)
    # pylint: disable=W0110
    added = map(lambda interface: interface['Name'], added)
    # pylint: disable=W0110
    unspecified = map(lambda interface: interface['Name'], unspecified)
    sorted_interface_names = removed + added + unspecified
    return sorted_interface_names


def sort_members_by_tags(interface):
    """Sort members of a given interface in the order of diffing tags.
    Args:
        An "interface" object
    Returns:
        A sorted "interface" object
    """
    sorted_interface = OrderedDict()
    if DIFF_TAG in interface:
        return interface
    for member_type in EXTATTRIBUTES_AND_MEMBER_TYPES:
        member_list = interface[member_type]
        removed, added, unspecified = group_by_tag(member_list)
        sorted_interface[member_type] = removed + added + unspecified
    return sorted_interface


def sort_diff_by_tags(interfaces):
    """Sort an "interfaces" object in the order of diffing tags.
    Args:
        An "interfaces" object loaded by load_json_data().
    Returns:
        A sorted "interfaces" object
    """
    sorted_interfaces = OrderedDict()
    sorted_interface_names = sort_interface_names_by_tags(interfaces)
    for interface_name in sorted_interface_names:
        interface = sort_members_by_tags(interfaces[interface_name])
        sorted_interfaces[interface_name] = sort_member_types(interface)
    return sorted_interfaces


def sort_members_in_alphabetical_order(interface):
    """Sort a "members" object in the alphabetical order.
    Args:
        An "interface" object
    Returns:
        A sorted "interface" object
    """
    sorted_interface = OrderedDict()
    for member_type in EXTATTRIBUTES_AND_MEMBER_TYPES:
        sorted_members = sorted(interface[member_type],
                                key=lambda member: member['Name'])
        sorted_interface[member_type] = sorted_members
    return sorted_interface


def sort_diff_in_alphabetical_order(interfaces):
    """Sort an "interfaces" object in the alphabetical order.
    Args:
        An "interfaces" object.
    Returns:
        A sorted "interfaces" object
    """
    sorted_interfaces = OrderedDict()
    for interface_name in sorted(interfaces.keys()):
        interface = interfaces[interface_name]
        sorted_interface = sort_members_in_alphabetical_order(interface)
        sorted_interface[DIFF_TAG] = interface.get(DIFF_TAG)
        sorted_interfaces[interface_name] = sorted_interface
    return sorted_interfaces


def print_member_with_color(member, out):
    """Print the "member" with a colored text. '+' is added to an added
    "member". '-' is added to a removed "member".
    Args:
        member: A "member" object
    """
    if DIFF_TAG in member:
        if member[DIFF_TAG] == DIFF_TAG_DELETED:
            out.change_color(Colorize.RED)
            out.write('- ')
        elif member[DIFF_TAG] == DIFF_TAG_ADDED:
            out.change_color(Colorize.GREEN)
            out.write('+ ')
    else:
        out.change_color(Colorize.BLACK)
        out.write('  ')


def print_extattributes(extattributes, out):
    """Print extattributes in an "interface" object.
    Args:
        A list of "ExtAttributes" in the "interface" object
    """
    for extattribute in extattributes:
        out.write('    ')
        print_member_with_color(extattribute, out)
        out.writeln(extattribute['Name'])


def print_consts(consts, out):
    """Print consts in an "interface" object.
    Args:
        A list of "Consts" of the "interface" object
    """
    for const in consts:
        out.write('    ')
        print_member_with_color(const, out)
        out.write(str(const['Type']))
        out.write(' ')
        out.write(const['Name'])
        out.write(' ')
        out.writeln(const['Value'])


def print_items(items, callback, out):
    """Calls |callback| for each item in |items|, printing commas between
    |callback| calls.
    Args:
        items: extattributes or arguments
    """
    count = 0
    for item in items:
        callback(item)
        count += 1
        if count < len(items):
            out.write(', ')


def print_extattributes_in_member(extattributes, out):
    """Print extattributes in a "member" object.
    Args:
        A list of "ExtAttributes" in the "member" object
    """
    def callback(extattribute):
        out.write(extattribute['Name'])

    out.write('[')
    print_items(extattributes, callback, out)
    out.write(']')


def print_attributes(attributes, out):
    """Print attributes in an "interface" object.
    Args:
        A list of "Attributes" in the "interface" object
    """
    for attribute in attributes:
        out.write('    ')
        print_member_with_color(attribute, out)
        if attribute['ExtAttributes']:
            print_extattributes_in_member(attribute['ExtAttributes'], out)
        out.write(str(attribute['Type']))
        out.write(' ')
        out.writeln(attribute['Name'])


def print_arguments(arguments, out):
    """Print arguments in a "members" object named "Operations".
    Args: A list of "Arguments"
    """
    def callback(argument):
        out.write(argument['Name'])

    out.write('(')
    print_items(arguments, callback, out)
    out.writeln(')')


def print_operations(operations, out):
    """Print operations in a "member" object.
    Args:
        A list of "Operations"
    """
    for operation in operations:
        out.write('    ')
        print_member_with_color(operation, out)
        if operation['ExtAttributes']:
            print_extattributes_in_member(operation['ExtAttributes'], out)
        out.write(str(operation['Type']))
        out.write(' ')
        if operation['Arguments']:
            out.write(operation['Name'])
            print_arguments(operation['Arguments'], out)
        else:
            out.writeln(operation['Name'])


def print_diff(diff, out):
    """Print the diff on a shell.
    Args:
        A sorted diff
    """
    for interface_name, interface in diff.iteritems():
        print_member_with_color(interface, out)
        out.change_color(Colorize.YELLOW)
        out.write('[[')
        out.write(interface_name)
        out.writeln(']]')
        out.reset_color()
        for member_name, member in interface.iteritems():
            if member_name == 'ExtAttributes':
                out.writeln('ExtAttributes')
                print_extattributes(member, out)
            elif member_name == 'Consts':
                out.writeln('  Consts')
                print_consts(member, out)
            elif member_name == 'Attributes':
                out.writeln('  Attributes')
                print_attributes(member, out)
            elif member_name == 'Operations':
                out.writeln('  Operations')
                print_operations(member, out)
            out.reset_color()


def print_usage():
    """Show usage."""
    sys.stdout.write('Usage: print_diff.py <diff_file.json> <"TAG"|"ALPHABET">\n')


def main(argv):
    if len(argv) != 2:
        print_usage()
        exit(1)
    json_data = argv[0]
    order = argv[1]
    diff = load_json_file(json_data)
    if order == 'TAG':
        sort_func = sort_diff_by_tags
    elif order == 'ALPHABET':
        sort_func = sort_diff_in_alphabetical_order
    else:
        print_usage()
        exit(1)
    sorted_diff = sort_func(diff)
    out = Colorize(sys.stdout)
    print_diff(sorted_diff, out)


if __name__ == '__main__':
    main(sys.argv[1:])
