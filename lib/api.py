from __future__ import print_function

import json
import sys
import traceback
from collections import namedtuple

import simplejson as json
import zerorpc

from gui_html import Builds as Builds


class Get_Build(object):
    builds = ""

    def __init__(self):
        self.builds = Builds()
        print('[python] Builds() __init__.')

    def init(self):
        """based on the input text, return the int result"""
        print('[python] Builds() init().')
        try:
            return self.builds.get_as_data_uri('')
        except Exception as e:
            return "Exception in api.py init(): [{}] {} with arg: {}".format(type(e), str(Exception.with_traceback(e)), [])

    def export(self):
        """invoke export"""
        try:
            return self.builds.export()
        except Exception as e:
            return "Exception in api.py export(): [{}] {} with arg: {}".format(type(e), str(Exception.with_traceback(e)), [])

    def change_class(self, class_name):
        """Return page of the new class"""
        try:
            print(class_name)
            # new_selection = _jsonnet.evaluate_snippet(
            #     'snippet', new_selection_json)
            return self.builds.get_as_data_uri(class_name)
        except Exception as e:
            return "Exception in api.py change_class(): [{}] {} with arg: {}".format(type(e), str(Exception.with_traceback(e)), [class_name, new_selection_json, str(new_selection_json)])

    def update(self, class_name, new_selection_json):
        """update selection for the given class"""
        try:
            new_selection = json.loads(str(new_selection_json))
            print(new_selection)
            # new_selection = _jsonnet.evaluate_snippet(
            #     'snippet', new_selection_json)
            self.builds.update(class_name, new_selection)
            return self.builds.get_as_data_uri(class_name)
        except Exception as e:
            return "Exception in api.py update(): [{}] {} with arg: {}".format(type(e), str(Exception.with_traceback(e)), [class_name, new_selection_json, str(new_selection_json)])

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
    s = zerorpc.Server(Get_Build())
    s.bind(addr)
    print('start running on {}'.format(addr))
    s.run()


if __name__ == '__main__':
    main()
