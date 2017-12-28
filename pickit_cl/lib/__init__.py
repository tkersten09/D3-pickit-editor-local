import os.path
import sys
from pprint import pprint as print

abs_dir_path = os.path.dirname(os.path.realpath(__file__))
new_path = os.path.abspath(os.path.join(abs_dir_path, ".."))
sys.path.insert(0, new_path)
# print("lib:")
# print(new_path)
# print(sys.path)
