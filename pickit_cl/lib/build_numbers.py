"""Download Buildnumbers for all classes from
http://www.diablofans.com/builds/.

The electron gui uses this Python Script via the
api.py to get a selection of Buildnumbers from
the user. It stores this in the build_numbers_export.txt.
Which then can be used as input for the pickit-cl
Script."""
import base64
import inspect
import json
import os
import re
import sys
from collections import OrderedDict
from pprint import pprint as print

from bs4 import BeautifulSoup

from youtube_upload.lib import retriable_exceptions

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
    import urllib


abs_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, abs_dir_path)

# change working directory to one folder up
os.chdir(abs_dir_path + "/../")

# GLOBAL VARIABLES */

retriable_exceptions_list = {
    urllib.error.HTTPError,
}

FANS_BASEURL = 'http://www.diablofans.com/builds/'


def get_page(url):
    def func():
        return urllib2.urlopen(url)

    return retriable_exceptions(func, retriable_exceptions_list, 4)


def print_s(*vars):
    for var in vars:
        callers_local_vars = inspect.currentframe().f_back.f_locals.items()
        var_name = [
            var_name for var_name, var_val in
            callers_local_vars if var_val is var]
        print(var_name)
        print(var)


class_name_list = ['barbarian',
                   'crusaider',
                   'demon hunter',
                   'monk',
                   'witch doctor',
                   'wizard',
                   'necromancer'
                   ]


class Build_numbers(object):
    builds_dict = {}
    builds_selected = {}
    html_soup_dict = {}
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

        self.html_soup_dict = {
            'crusaider': "",
            'demon hunter': "",
            'monk': "",
            'witch doctor': "",
            'wizard': "",
            'necromancer': "",
            'barbarian': ""
        }
        # fast = False
        # if fast:
        #     self.init_html_code('crusaider')
        # else:
        #     for class_name in class_name_list:
        #         self.init_html_code(class_name)

    def load_class_page(self, class_name):
        """Loads content of the page from the given class into builds_dict."""
        url = self.url_class[class_name]
        html_code = get_page(url)

        soup = BeautifulSoup(html_code, 'html.parser')

        # Remove all javascript from the page
        # by deleting all <script /> tags
        scripts_soup = soup.find_all('script')
        # print_s(scripts_soup)
        for script_tag in scripts_soup:
            script_tag.decompose()
        scripts_soup_after = soup.find_all('script')

        # print_s(scripts_soup_after)
        builds_soup = soup.select('tr a.d3build')
        group_type_soup = soup.select('td.col-group-type')
        group_rating_soup = soup.select('td.col-rating')
        s = u"\u005C"  # backslash
        link_soup = soup.select('fieldset.class ul li label')
        for index, link in enumerate(link_soup):
            link_tag = soup.new_tag(
                'a', href=r'file:///C:\Users\Thomas\Documents\GitHub\pickit-cl\gui\temp' + s + class_name_list[index] + ".html", onclick='navigateTo("' + class_name_list[index] + '")')
            link.wrap(link_tag)
        # print_s(link_soup)

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
        self.html_soup_dict[class_name] = soup
        pass

    def init_class_page(self, class_name):
        soup = self.html_soup_dict[class_name]

        head_soup = soup.select_one('head')

        self.head_script = """
let className = '""" + class_name + """'
"""
        script_tag = soup.new_tag(
            "script", src="C:/Users/Thomas/Documents/GitHub/pickit-cl/gui/reload_buildnumbers.js", type="text/javascript")
        head_soup.insert(0, script_tag)

        script_tag = soup.new_tag(
            "script", type="text/javascript")
        script_tag.append(self.head_script)
        head_soup.insert(0, script_tag)

        base_tag = soup.new_tag(
            "base", href="http://www.diablofans.com", target="_blank")
        head_soup.insert(0, base_tag)
        head_soup.insert(0, "\n")

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
        self.html_soup_dict[class_name] = soup
        pass

    def update_class_page(self, class_name, init=False):
        """Apply the checked state of the builds to the HTML page (soup)."""
        soup = self.html_soup_dict[class_name]

        buildnumber_checkboxes = soup.select('input[buildnumber]')
        count = 0
        if init:
            self.builds_selected[class_name] = {}
        for index, checkbox in enumerate(buildnumber_checkboxes):
            buildnumber = checkbox['buildnumber'].strip()
            build = self.builds_dict[class_name][index]
            if init:
                """Mark 10 Builds that are of type
                'Solo' or 'Hybrid' as selected."""
                count += 1
                type_name = build['type_name'].strip()
                if (type_name == 'Solo' or
                        type_name == 'Hybrid') and count <= 10:
                    checkbox['checked'] = True
                    self.builds_selected[class_name][buildnumber] = True
            else:
                """Update the checked state of the checkbox."""
                if buildnumber in self.builds_selected[class_name]:
                    checkbox['checked'] = True
                else:
                    try:
                        del checkbox['checked']
                    except Exception as e:
                        pass
        self.html_soup_dict[class_name] = soup

    def init_html_code(self, class_name, init=False):
        """Get the html_code of the page for given class."""

        if len(self.builds_dict[class_name]) is 0:
            self.load_class_page(class_name)
            self.init_class_page(class_name)
            init = True
        self.update_class_page(class_name, init=init)

    def update(self, class_name, new_selection):
        self.builds_selected[class_name] = {}
        # print(new_selection)
        for buildnumber, checked in new_selection.items():
            if checked:
                self.builds_selected[class_name][buildnumber] = True
        # return self.update_class_page(class_name)

    def get_as_data_uri(self, class_name, html_code=""):
        """Converts HTML code to a url for a import of html as an url."""
        # 1. From Python: in this case value is returned
        # 2. From Javascript: in this case value cannot be returned because
        #    inter-process messaging is asynchronous, so must return value
        #    by calling js_callback.
        if class_name == '':
            class_name = 'crusaider'
        if html_code == '':
            html = self.html_soup_dict[class_name].prettify()
        #html = html.encode("utf-8", "replace")
        # b64 = base64.b64encode(html).decode("utf-8", "replace")
        # ret = "data:text/html;base64,{data}".format(data=b64)
        # ret = "data:text/html,{data}".format(data=html)
        with open(r'data\init.html', 'w') as file:
            file.write(str(html))
        return html

    def export_build_numbers(self):
        self.write_build_numbers()

    def export_pickit_config(self, fourthree, buildtype):
        os.system('python pickit_cl.py -f --number-file="build_numbers_export.txt" -4 ' +
                  str(fourthree) + ' -b ' + buildtype)

    def write_build_numbers(self):
        # Create or empty the file
        with open('build_numbers_export.txt', 'w') as file:
            file.close()
        # Go through all classes
        for class_name in class_name_list:
            # Get all builds for one class
            build_list = self.builds_dict[class_name]
            with open('build_numbers_export.txt', 'a') as file:
                # First write the class name on top
                file.write("# {}\n".format(class_name))

                # then write all the builds for that class
                for build in build_list:
                    buildnumber = build['buildnumber']

                    # but write only if the build is selected
                    if buildnumber in self.builds_selected[class_name]:
                        file.write("{} # Rating: {} Name: {}\n".format(
                            buildnumber,
                            build['rating'],
                            build['name']))
