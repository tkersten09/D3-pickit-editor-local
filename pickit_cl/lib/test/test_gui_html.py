import os.path
import sys

import pytest

abs_dir_path = sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.insert(0, abs_dir_path)
print(sys.path)

import pickit_cl.lib.gui_html






@pytest.fixure
def initBuilds():
    builds = lib.gui_html.Builds()
    return builds


def test_script_in_header(initBuilds):
    assert initBuilds.head_script is not None
