# import py2exe
from pprint import pprint as print

from paver.easy import *
from paver.setuputils import (find_package_data, setup, standard_exclude,
                              standard_exclude_directories)

# change from tuple to list, otherwise .extend and fix_path_names()
# do not work.
standard_exclude = list(standard_exclude)
standard_exclude_directories = list(standard_exclude_directories)

# add directories to exclude
standard_exclude_directories.extend(
    ['node_modules', '__pycache__'])

# fix: directories now also work for windows


def fix_path_names(path_list):
    """Replaces "/" with "\"."""
    return [name.replace("/", "\\") for name in path_list]


standard_exclude = fix_path_names(standard_exclude)
standard_exclude_directories = fix_path_names(standard_exclude_directories)


pdata_include = find_package_data(
    package='', exclude_directories=standard_exclude_directories,
    exclude=standard_exclude, only_in_packages=False)
print(pdata_include)
print(pdata_include[""])

setup(
    name="pickit-cl",
    packages=['pickit_cl', 'gui'],
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
    # data_files=pdata_include,
    # exclude_package_data=pdata_exclude,
    zip_safe=True,
)


@task
@needs('generate_setup', 'minilib')
def build():
    """Build the release and install it"""

    sh('paver bdist_egg')
    sh('paver sdist')
    # sh('pyinstaller -y --clean lib/pickit_cl_own.spec')
    # sh('python setup.py py2exe')
    eggdir = path('.').glob('*.egg-info')
    for p in eggdir:
        p.rmtree()
    path('build').rmtree()

    pass


@task
@needs('generate_setup', 'minilib')
def dev():
    """Install the package in dev mode.

    This means that it installs this package while it stayed in the current
     folder. This way editing code and testing is a lot faster."""
    sh('python setup.py develop')
    # eggdir = path('.').glob('*.egg-info')
    # for p in eggdir:
    #     p.rmtree()
    # path('build').rmtree()

    pass


# the pass that follows is to work around a weird bug. It looks like
# you can't compile a Python module that ends in a comment.
pass
