# import py2exe
import os
import re
import sys
from distutils.util import convert_path
from fnmatch import fnmatchcase
from os.path import *
from pprint import pprint as print

import paver.setuputils
from paver.easy import *
from paver.setuputils import find_package_data, setup
from six import print_

standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
                                './dist', 'EGG-INFO', '*.egg-info')


def find_package_data(
        where='.', package='',
        exclude=standard_exclude,
        exclude_directories=standard_exclude_directories,
        only_in_packages=True,
        show_ignored=False, debug_exclude=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.
    The dictionary looks like::
        {'package': [files]}
    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.
    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).
    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.
    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).
    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.

    This function is by Ian Bicking.
    """

    out = {}
    stack = [(convert_path(where), '', package, only_in_packages)]

    # prints exclude before the fix
    [print_("%s, " % (ex), file=sys.stderr, end="") for ex in exclude]
    print_('', file=sys.stderr)

    # replace '/' with '\'
    exclude = [name.replace("/", "\\") for name in exclude]

    # Alternatives fail because './' will be cut off in './dist'
    # for example
    # exclude = convert_path(exclude)
    # exclude = [convert_path(name) for name in exclude]

    # print exclude after the fix
    [print_("%s, " % (ex), file=sys.stderr, end="") for ex in exclude]
    print_('', file=sys.stderr)

    # also fix exclude_directories
    exclude_directories = [name.replace("/", "\\")
                           for name in exclude_directories]

    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = join(where, name)
            if isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if debug:
                        print_("[Debug exclude: Directory] fn: '{}', pattern: '{}', name: '{}'".format(
                            fn, pattern, name), file=sys.stderr)
                    if (fnmatchcase(name, pattern)
                            or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print_("Directory %s ignored by pattern %s"
                                   % (fn, pattern), file=sys.stderr)
                        break
                if bad_name:
                    continue
                if isfile(join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                    stack.append((fn, '', new_package, False))
                else:
                    stack.append((fn, prefix + name + '/',
                                  package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if debug:
                        print_("[Debug exclude: File] fn: '{}', pattern: '{}', name: '{}'".format(
                            fn, pattern, name), file=sys.stderr)
                    if (fnmatchcase(name, pattern)
                            or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print_("File %s ignored by pattern %s"
                                   % (fn, pattern), file=sys.stderr)
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    if debug:
        print_("[Debug exclude: Info] fnmatchcase(name, pattern) or fn.lower() == pattern.lower() \
has to match to be excluded as file or directory.")
    return out


exclude = ['*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*',
           './pickit_cl/data/load.py', '.\pickit_cl\data\item-collector.py']
exclude_directories = ['.*', 'CVS', '_darcs', './build',
                       './dist', 'EGG-INFO', '*.egg-info', 'node_modules', '__pycache__']

# pdata = paver.setuputils.find_package_data
pdata = find_package_data(
    package='', exclude_directories=exclude_directories,
    exclude=exclude,
    show_ignored=True, only_in_packages=False, debug_exclude=True)
print(pdata)
pdata_include = {'pickit_cl': [
    '*.txt', 'data/*.txt', 'data/*.json', 'output/*.ini']}
pdata_exclude = {'pickit_cl': ['data/*.py']}
setup(
    name="pickit-cl",
    packages=['pickit_cl'],
    version="0.1.0",
    author="Thomas Kersten",
    author_email="tkersten09@gmail.com",
    install_requires=[],
    scripts=[],
    entry_points={
        'console_scripts': [
            'pickit-cl = pickit_cl.pickit_cl:run'
        ],
    },
    include_package_data=True,
    package_data=pdata_include,
    exclude_package_data=pdata_exclude,
    zip_safe=True,
)


@task
@needs('generate_setup', 'minilib')
def build():
    """Build the release and install it"""

    # sh('paver bdist_egg')
    # sh('paver sdist')
    # # sh('pyinstaller -y --clean lib/pickit_cl_own.spec')
    # # sh('python setup.py py2exe')
    # eggdir = path('.').glob('*.egg-info')
    # for p in eggdir:
    #     p.rmtree()
    # path('build').rmtree()

    pass


@task
@needs('generate_setup', 'minilib')
def dev():
    """Install the package in dev mode.

    This means that it installs this package while it stayed in the current
     folder. This way editing code and testing is a lot faster."""
    sh('python setup.py develop')
    eggdir = path('.').glob('*.egg-info')
    for p in eggdir:
        p.rmtree()
    path('build').rmtree()

    pass


# the pass that follows is to work around a weird bug. It looks like
# you can't compile a Python module that ends in a comment.
pass
