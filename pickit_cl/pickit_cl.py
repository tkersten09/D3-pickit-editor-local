#!/usr/bin/env python
#
# Upload videos to Youtube from the command-line using APIv3.
#
# Author: Arnau Sanchez <pyarnau@gmail.com>
# Project: https://github.com/tokland/youtube-upload
"""
Download Builds from http://www.diablofans.com/builds/BUILDNUMBER \
with the given Buildnumber (like 57405).
And stores them into output/*.ini for TurboHUD as Pickit Configuration Files \
(like pickit_sc_70.ini).
Use it like this:
    $ pickit-cl --use-number-file --fourthree=4 --buildtype="full"
or
    $ pickit-cl -f --number-file="build_numbers_export.txt" -4 3 -b build
"""
import optparse
import os
import re
import sys
import urllib
import urllib.request as urllib2

import zerorpc

import lib.pickit_cl_ori_py3 as pickit_cl_ori
from lib.build_numbers import print_s
from youtube_upload.lib import catch_exceptions, retriable_exceptions

abs_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, abs_dir_path)
# print(sys.path)

retriable_exceptions_list = {
    urllib.error.HTTPError,
}


class OptionsError(Exception):
    pass


EXIT_CODES = {
    OptionsError: 2,
    NotImplementedError: 5,
}

progress_client = zerorpc.Client()
progress_client.connect("tcp://127.0.0.1:4243")


def delete_empty_elements(old_list):
    count = 0
    for element in old_list:
        if element == '':
            count += 1
    for i in range(count):
        old_list.remove('')
    return old_list


def run_pickit(build_numbers, options, args):
    """Parse all files in file_list by using tokland / youtube - upload script."""
    print(progress_client.addProgressBar(len(build_numbers)))
    pickitList_list = []
    i = 0
    for buildnumber in build_numbers:
        pick = pickit_cl_ori.main(
            buildnumber=buildnumber,
            fourthree=options.fourthree,
            buildtype=options.buildtype)
        i += 1
        print(progress_client.updateProgressBar(i))
        pickitList_list.append(pick)
    if options.onefile:
        builds_string = "\n".join(pickitList_list)
        pickit_cl_ori.write_output(
            buildnumber='builds',
            buildtype=options.buildtype,
            pickitList=builds_string)
    else:
        for buildnumber in build_numbers:
            pickit_cl_ori.write_output(
                buildnumber=buildnumber,
                buildtype=options.buildtype,
                pickitList=pickitList_list)


def parse_options_error(parser, options, args):
    """Check errors in options."""
    required_options = []
    missing = [opt for opt in required_options if not getattr(options, opt)]
    if missing:
        parser.print_usage()
        msg = "Some required option are missing: {0}".format(
            ", ".join(missing))
        raise OptionsError(msg)


def run_main(parser, options, args, output=sys.stdout):
    """Run the main scripts from the parsed options / args. \
       It read in buildnumbers from args or from the build_numbers.txt file. \
       And checks if the Builds for them exists on the site."""
    parse_options_error(parser, options, args)
    # args = '53544'
    # print("args: {}".format(args))
    build_numbers = []
    if options.use_number_file:
        pattern = re.compile('([^#]*)(#)(.*)')
        # print(os.getcwd())
        # print(sys.path)
        # print(abs_dir_path)
        # print("stack[1]: {}".format(inspect.stack()[1]))
        # print("stack: {}".format(inspect.stack()))
        with open('{}'.format(options.number_file), 'r') as number_file:
            splited = str(number_file.read()).split('\n')
            # print('splited: {}'.format(splited))
            for string in splited:
                f = pattern.findall(string)
                if len(f) is 0:
                    build_numbers.append(string.strip())
                else:
                    # print("f[0][0]: {}".format(f[0][0]))
                    build_numbers.append(f[0][0].strip())

    else:
        for string in args:
            build_numbers.append(string.strip())

    # removes empty elements
    build_numbers = delete_empty_elements(build_numbers)

    # raise exception if no buildnumbers were given
    if len(build_numbers) is 0:
        raise OptionsError("No existing Buildnumbers given.")

    # print_s(build_numbers)
    for buildnumber in build_numbers:

        url = 'http://www.diablofans.com/builds/{}'.format(buildnumber)

        def func(): return urllib2.urlopen(url)
        retriable_exceptions(func, retriable_exceptions_list, 4)

    run_pickit(build_numbers, options, args)


def main(arguments):
    """Define the usage and the options. And then parses the given \
     options / args and give this to run_main()."""

    usage = """Usage: % prog[OPTIONS] BUILDNUMBER[BUILDNUMBER2 ...]

Download Builds from http://www.diablofans.com/builds/BUILDNUMBER \
with the given Buildnumber (like 57405).
And stores them into output/*.ini for TurboHUD as Pickit Configuration Files \
(like pickit_sc_70.ini).
Use it like this:
    $ pickit-cl --use-number-file --fourthree="4" --buildtype="full"
or
    $ pickit-cl -f --number-file="build_numbers_export.txt" -4 3 -b build"""
    parser = optparse.OptionParser(usage=usage)

    parser.add_option(
        '', '--number-file', dest='number_file',
        default='build_numbers.txt',
        help='Path to a file containing a list of Buildnumbers. The path \
is relative to the pickit_cl.py Script. [build_numbers.txt]')
    parser.add_option(
        '-f', '--use-number-file', action="store_true",
        dest='use_number_file', default=False,
        help=r'Use "build_numers.txt" from above as input. [False]')
    parser.add_option(
        '-4', '--fourthree', dest='fourthree', type="int",
        default=3, help='Items must roll with all stats or (stats - 1)? \
E.G. If a helm needs Socket, CHC, Int, Vit - go with all 4 or just 3? (4/3) [3]')
    parser.add_option(
        '-b', '--buildtype', dest='buildtype', metavar="STRING",
        default="build",
        help=r'Full file or just the build? (Full\Build) [Build]')
    parser.add_option(
        '-s', '--severalfiles',
        action="store_false", dest='onefile',
        default=True, help='Write all Builds in several Files. Default is \
just one File. [True]')

    # Fixes bug for the .exe in windows: The help will be displayed, when no
    # arguments are given.
    if len(arguments) == 0:
        parser.print_help()
        return 0

    options, args = parser.parse_args(arguments)
    options.buildtype = options.buildtype.lower()

    # print(options)

    run_main(parser, options, args)


def run():
    sys.exit(catch_exceptions(EXIT_CODES, main, sys.argv[1:]))


if __name__ == '__main__':
    run()
