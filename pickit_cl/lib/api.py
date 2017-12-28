"""The electron GUI uses this Script as interface
for the build_numbers.py Script (geting Buildnumbers)
and for the pickit_cl.py (create TurboHUD pickit Configuration
File for given Buildnumbers.)."""
from __future__ import print_function

import json
import sys
import traceback
from collections import namedtuple
from pprint import pprint as print

import simplejson as json
import zerorpc

from build_numbers import Build_numbers as Builds
from build_numbers import print_s


class get_build(object):
    """"""
    builds = ""

    def __init__(self):
        print('[python] get_build().__init__().')

    def init(self):
        """based on the input text, return the int result"""
        print('[python] Builds().init().')
        try:
            self.builds = Builds()
            return "[gui_html.py] init successful."
        except Exception as e:
            return "[api.py: exception] init(): [{}] {} with arg: {}".format(type(e), str(Exception.with_traceback(e)), [])

    def export_build_numbers(self):
        """invoke export"""
        print('[python] Builds().export_build_numbers().')
        try:
            return self.builds.export_build_numbers()
        except Exception as e:
            return "[api.py: exception] export_build_numbers(): [{}] {} with arg: {}".format(type(e), str(Exception.with_traceback(e)), [])
        else:
            return "[gui_html.py] export successful."

    def export_pickit_config(self, fourthree, buildtype):
        """invoke export"""
        print('[python] Builds().export_pickit_config().')
        try:
            self.builds.export_build_numbers()
            self.builds.export_pickit_config(fourthree, buildtype)
            return "[api.py] export_pickit_config successfull."
        except Exception as e:
            return "[api.py: exception] export_pickit_config(): [{}] {} with arg: {}".format(type(e), str(Exception.with_traceback(e)), [])
        else:
            return "[gui_html.py] export successful."

    def change_class(self, class_name):
        """Return page of the new class"""
        print('[python] Builds().class_name(): ' + class_name)
        try:
            self.builds.init_html_code(class_name)
            return self.builds.get_as_data_uri(class_name)
        except Exception as e:
            return "[api.py: exception] change_class(): [{}] {} with arg: {}".format(type(e), str(Exception.with_traceback(e)), [class_name])

    def update(self, class_name, new_selection_json):
        """update selection for the given class"""
        print('[python] Builds().update()')
        try:
            new_selection = json.loads(str(new_selection_json))
            print(new_selection)
            # new_selection = _jsonnet.evaluate_snippet(
            #     'snippet', new_selection_json)
            self.builds.update(class_name, new_selection)
            # return self.builds.get_as_data_uri(class_name)
        except Exception as e:
            return "[api.py: exception] update(): [{}] {} with arg: {}".format(type(e), str(Exception.with_traceback(e)), [class_name, new_selection_json, str(new_selection_json)])
        else:
            return "[gui_html.py] update successful."

    def echo(self, text):
        """echo any text"""
        print('python echo:' + text)
        return text


def parse_port():
    port = 4242
    try:
        port = int(sys.argv[1])
    except Exception as e:
        pass
    return '{}'.format(port)


def main():
    addr = 'tcp://127.0.0.1:' + parse_port()
    s = zerorpc.Server(get_build())
    s.bind(addr)
    print('start running on {}'.format(addr))
    s.run()


if __name__ == '__main__':
    main()
