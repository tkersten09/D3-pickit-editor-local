import base64
import inspect
import json
import os
import re
import sys
from collections import OrderedDict

from bs4 import BeautifulSoup

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2


abs_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, abs_dir_path)

# change working directory to one folder up
os.chdir(abs_dir_path + "/../")

# GLOBAL VARIABLES */

FANS_BASEURL = 'http://www.diablofans.com/builds/'

with open(r'data\itemlist.json', 'r') as f:
    itemList = json.load(f)

with open(r'data\statlist2.json', 'r') as f1:
    statList = {int(k): v for k, v in json.load(f1).items()}

with open(r'data\typelist.json', 'r') as f2:
    typeList = json.load(f2)


def get_page(url):
    while True:
        try:
            url = page = urllib2.urlopen(url)
            break
        except urllib2.URLError:
            print('Url not found check build number')
        except Exception:
            print('Exception')
    return page


def print_s(*vars):
    for var in vars:
        callers_local_vars = inspect.currentframe().f_back.f_locals.items()
        var_name = [
            var_name for var_name, var_val in
            callers_local_vars if var_val is var]
        print('{}: {}'.format(var_name, var))


class_name_list = ['crusaider',
                   'demon hunter',
                   'monk',
                   'witch doctor',
                   'wizard',
                   'necromancer',
                   'barbarian']


class Builds(object):
    builds_dict = {}
    builds_selected = {}
    HTML_code_dict = {}
    head_script = ""
    selected = {}
    url_class = {}
    url_class['crusaider'] = 'http://www.diablofans.com/builds?filter-build-type=1&filter-build=13&filter-has-spell-2=-1&filter-build-tag=5&filter-class=64'
    url_class['demon hunter'] = 'http://www.diablofans.com/builds?filter-build-type=1&filter-build=13&filter-has-spell-2=-1&filter-build-tag=5&filter-class=4'
    url_class['monk'] = 'http://www.diablofans.com/builds?filter-build-type=1&filter-build=13&filter-has-spell-2=-1&filter-build-tag=5&filter-class=16'
    url_class['witch doctor'] = 'http://www.diablofans.com/builds?filter-build-type=1&filter-build=13&filter-has-spell-2=-1&filter-build-tag=5&filter-class=8'
    url_class['wizard'] = 'http://www.diablofans.com/builds?filter-build-type=1&filter-build=13&filter-has-spell-2=-1&filter-build-tag=5&filter-class=32'
    url_class['necromancer'] = 'http://www.diablofans.com/builds?filter-build-type=1&filter-build=13&filter-has-spell-2=-1&filter-build-tag=5&filter-class=128'
    url_class['barbarian'] = 'http://www.diablofans.com/builds?filter-build-type=1&filter-build=13&filter-has-spell-2=-1&filter-build-tag=5&filter-class=2'

    def __init__(self):
        self.builds_selected = {
            'crusaider': [],
            'demon hunter': [],
            'monk': [],
            'witch doctor': [],
            'wizard': [],
            'necromancer': [],
            'barbarian': []
        }
        self.builds_dict = self.builds_selected.copy()
        self.head_script = """
let class_name = "crusaider"
const {ipcRenderer} = require('electron')
const webview = document.querySelector('webview')
webview.addEventListener('dom-ready', () => {
webview.openDevTools()
buildnumber_checkboxes = document.querySelectorAll('input[buildnumber]');
buildnumber_checkboxes.forEach(function(currentValue, currentIndex, listObj) {
    currentValue.addEventListener('Change', () => {
    buildnumber_checkboxes = document.querySelectorAll('input[buildnumber]');
    let new_selection = new Map()
    let checked = false
    buildnumber_checkboxes.forEach(function(currentValue, currentIndex, listObj) {
        checked = false
        buildnumber = currentValue.getAttribute('buildnumber')
        if(currentValue.checked){
            checked = true
        }
        new_selection = new_selection.set(buildnumber, checked)
    }

    ipcRenderer.sendToHost('update_buildnumbers', class_name, new_selection)
    })
  }
)
})
"""
        self.HTML_code_dict = {
            'crusaider': "",
            'demon hunter': "",
            'monk': "",
            'witch doctor': "",
            'wizard': "",
            'necromancer': "",
            'barbarian': ""
        }
        fast = True
        if fast:
            self.load_class_page('crusaider')
        else:
            for class_name in class_name_list:
                self.init_HTML_code(class_name)

    def load_class_page(self, class_name):
        """Loads content of the page from the given class into builds_dict."""
        url = self.url_class[class_name]
        HTML_code = get_page(url)

        soup = BeautifulSoup(HTML_code, 'html.parser')

        builds_soup = soup.select('tr a.d3build')
        group_type_soup = soup.select('td.col-group-type')
        group_rating_soup = soup.select('td.col-rating')

        self.builds_dict[class_name] = []

        p = re.compile('(?:\/builds\/)(\d+)(?:-)')
        for index, build in enumerate(builds_soup):
            name = build.get_text().strip()
            href = build.get('href')
            type_name = group_type_soup[index].find('span').get_text().strip()
            rating = group_rating_soup[index].find('div').get_text().strip()

            # Get buildnumber from the link in href
            m = p.findall(href)
            if len(m) is 0:
                raise NotImplementedError(
                    'href does not contain a buildnumber.')
            buildnumber = m[0]

            # Adding builds to builds_dict
            self.builds_dict[class_name].append(
                {'buildnumber': buildnumber,
                 'type_name': type_name,
                 'name': name,
                 'rating': rating
                 })
        HTML_code = soup.prettify()
        self.HTML_code_dict[class_name] = soup.prettify()
        return self.HTML_code_dict[class_name]

    def init_class_page(self, class_name):
        HTML_code = self.HTML_code_dict[class_name]
        soup = BeautifulSoup(HTML_code, 'html.parser')

        head_soup = soup.select('head')
        base_tag = soup.new_tag(
            "base", href="http://www.diablofans.com", target="_blank")
        head_soup.insert(0, base_tag)
        head_soup.insert(0, "\n")
        script_tag = soup.new_tag(
            "script")
        script_tag.append(self.head_script)
        head_soup.insert(0, script_tag)
        # print_s(head_soup)
        # print_s(soup.select_one('head'))

        th_soup = soup.select('table th')
        # print_s(th_soup)
        th_tag = soup.new_tag("th")
        button = soup.new_tag(
            'button',
            onclick="builds.update('" + class_name + "', document.documentElement.innerHTML)")
        button.insert(0, 'Update!')
        th_tag.insert(0, button)
        th_soup.pop().insert_after(th_tag)

        # Go through every build on the page
        builds_soup = soup.select('tr a.d3build')
        builds_td_soup = soup.select('td.col-updated')
        p = re.compile('(?:\/builds\/)(\d+)(?:-)')
        for index, build in enumerate(builds_soup):
            # Use RegExp to get buildnumber of build
            href = build.get('href')
            m = p.findall(href)
            if len(m) is 0:
                raise NotImplementedError(
                    'href does not contain a buildnumber.')
            buildnumber = m[0]

            # Add checkbox to build
            checkbox_tag = soup.new_tag(
                "input", buildnumber=buildnumber,
                type='checkbox')
            td_tag = soup.new_tag("td")
            td_tag.insert(0, checkbox_tag)
            builds_td_soup[index].insert_after(td_tag)
        HTML_code = soup.prettify()
        self.HTML_code_dict[class_name] = HTML_code
        return self.HTML_code_dict[class_name]

    def update_class_page(self, class_name, init=False):
        HTML_code = self.HTML_code_dict[class_name]
        soup = BeautifulSoup(HTML_code, 'html.parser')

        buildnumber_checkboxes = soup.select('input[buildnumber]')
        count = 0
        if init:
            self.builds_selected[class_name] = []
        for index, checkbox in enumerate(buildnumber_checkboxes):
            buildnumber = checkbox['buildnumber'].strip()
            build = self.builds_dict[class_name][index]
            if init:
                count += 1
                type_name = build['type_name'].strip()
                if (type_name == 'Solo' or type_name == 'Hybrid') and count <= 10:
                    checkbox['checked'] = True
                    self.builds_selected[class_name].append(build)
            else:
                selected = [build_s['buildnumber']
                            for build_s in self.builds_selected[class_name]]
                comp = [True for buildnumber in selected if buildnumber ==
                        build['buildnumber']]
                if len(comp) is 1:
                    checkbox['checked'] = True
                else:
                    try:
                        del checkbox['checked']
                    except Exception as e:
                        pass
        HTML_code = soup.prettify()
        self.HTML_code_dict[class_name] = HTML_code
        return self.HTML_code_dict[class_name]

    def init_HTML_code(self, class_name):
        """Get the HTML_code of the page for given class."""
        self.load_class_page(class_name)
        self.init_class_page(class_name)
        self.update_class_page(class_name, init=True)

    def update(self, class_name, new_selection):
        self.builds_selected[class_name] = []
        for buildnumber, checked in new_selection:
            if checked:
                self.builds_selected[class_name]['buildnumber'] = buildnumber
        return self.update_class_page(class_name)

    def get_as_data_uri(self, class_name, HTML_code=""):
        """Converts HTML code to a url for a import of html as an url."""
        # 1. From Python: in this case value is returned
        # 2. From Javascript: in this case value cannot be returned because
        #    inter-process messaging is asynchronous, so must return value
        #    by calling js_callback.
        if class_name == '':
            class_name = 'crusaider'
        if HTML_code is "":
            html = self.HTML_code_dict[class_name]
        html = html.encode("utf-8", "replace")
        print()
        b64 = base64.b64encode(html).decode("utf-8", "replace")
        ret = "data:text/html;base64,{data}".format(data=b64)
        return ret

    def export(self):
        self.write()

    def write(self):
        f = open('build_numbers_p.txt', 'w')
        f.close()
        for class_name, build_list in self.builds_dict:
            with open('build_numbers_p.txt', 'a') as file:
                file.write("# {}\n".format(class_name))
                for index, build in enumerate(build_list):
                    buildnumber = build['buildnumber']
                    if builds_selected[class_name][index]['buildnumber'] == buildnumber:
                        file.write("{} # Rating: {} Name: {}\n".format(
                            buildnumber,
                            build['rating'],
                            build['name']))
