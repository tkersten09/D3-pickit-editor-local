from paver.easy import *
from paver.setuputils import setup
import py2exe

# pdata = paver.setuputils.find_package_data(package='pickit_cl', only_in_packages=False)
pdata_include = {'': ['*.txt', 'data/*.txt', 'data/*.json', 'output/*.ini']}
pdata_exclude = {'': ['data/*.py']}
setup(
    name="pickit-cl",
    packages=['', 'lib'],
    version="0.1.0",
    author="Thomas Kersten",
    author_email="tkersten09@gmail.com",
    install_requires=[],
    scripts=[],
    entry_points={
        'console_scripts': [
            'pickit-cl = pickit_cl:run'
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

    sh('paver bdist_egg')
    sh('paver sdist')
    # sh('pyinstaller -y --clean lib/pickit_cl_own.spec')
    sh('python setup.py py2exe')
    eggdir = path('.').glob('*.egg-info')
    for p in eggdir:
        p.rmtree()
    path('build').rmtree()

    pass

# the pass that follows is to work around a weird bug. It looks like
# you can't compile a Python module that ends in a comment.
pass
