import json
import os
import sys
import inspect
import re
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from bs4 import BeautifulSoup
from collections import OrderedDict

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


js_script = """
function on_change(){
            if(this.checked){
                this.value = 1
                }
            else{
                this.value = 0
                }
                }
"""

class Builds(object):
    HTML_code = "";
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
        self.selected = {
            'crusaider': [],
            'demon hunter': [],
            'monk': [],
            'witch doctor': [],
            'wizard': [],
            'necromancer': [],
            'barbarian': []
            }
        self.HTML_code = self.init_HTML_code('crusaider')
        pass

    def init_HTML_code(self, class_name):
        """Get the HTML_code of the page for given class."""
        url = self.url_class[class_name]
        HTML_code = get_page(url)
        soup = BeautifulSoup(HTML_code, 'html.parser')

        head_soup = soup.select_one('head')
        base_tag = soup.new_tag(
            "base", href="http://www.diablofans.com", target="_blank")
        head_soup.insert(0, base_tag)
        head_soup.insert(0, "\n")
        script_tag = soup.new_tag(
            "script")
        script_tag.append(js_script)
        head_soup.insert(0, script_tag)
        # print_s(head_soup)
        # print_s(soup.select_one('head'))

        th_soup = soup.select('table th')
        # print_s(th_soup)
        th_tag = soup.new_tag("th")
        button = soup.new_tag(
            'button',
            onclick="builds.update('crusaider', document.documentElement.innerHTML)")
        button.insert(0, 'Update!')
        th_tag.insert(0, button)
        th_soup[-1].insert_after(th_tag)

        builds_td_soup = soup.select('td.col-updated')
        builds_soup = soup.select('tr a.d3build')
        group_type_soup = soup.select('td.col-group-type')
        group_rating_soup = soup.select('td.col-rating')
        count = 0
        p = re.compile('(?:\/builds\/)(\d+)(?:-)')
        for index, build in enumerate(builds_soup):
            count += 1
            name = build.get_text().strip()
            href = build.get('href')
            m = p.findall(href)
            if len(m) is 0:
                raise NotImplementedError('href does not contain a buildnumber.')
            buildnumber = m[0]
            type_name = group_type_soup[index].find('span').get_text().strip()
            rating = group_rating_soup[index].find('div').get_text().strip()
            # print('NAME={} | TYPE={} | RATING={}'.format(
            # name, type_name, rating))

            # Adding checkbox
            if (type_name == 'Solo' or type_name == 'Hybrid') and count <= 10:
                checkbox_tag = soup.new_tag(
                    "input", buildnumber=buildnumber,
                    checked=True,
                    type='checkbox',
                    onclick="on_change()")
                self.selected[class_name].append(
                    {'buildnumber': buildnumber,
                    'type_name': type_name,
                    'name': name,
                    'rating': rating
                    }
                )
            else:
                checkbox_tag = soup.new_tag(
                    "input", buildnumber=buildnumber,
                    type='checkbox', onclick="on_change(this)")

            td_tag = soup.new_tag("td")
            td_tag.insert(0, checkbox_tag)
            builds_td_soup[index].insert_after(td_tag)
        HTML_code = soup.prettify()
        return HTML_code

    def update(self, class_name, HTML_code):
        soup = BeautifulSoup(HTML_code, 'html.parser')

        builds_td_soup = soup.select('td.col-updated')
        builds_soup = soup.select('tr a.d3build')
        group_type_soup = soup.select('td.col-group-type')
        group_rating_soup = soup.select('td.col-rating')
        # checkbox_selected_soup = soup.select(
        #     'input[type="checkbox", selected="True"]')
        attrs = {"buildnumber": True, "checked": "True"}
        checkbox_selected_soup = soup.find_all(
            'input',
            attrs=attrs)
        print_s(checkbox_selected_soup)
        print_s(len(checkbox_selected_soup))
        p = re.compile('(?:\/builds\/)(\d+)(?:-)')
        self.selected[class_name] = []
        for index, build in enumerate(builds_soup):
            name = build.get_text().strip()
            href = build.get('href')
            m = p.findall(href)
            if len(m) is 0:
                raise NotImplementedError(
                    'href does not contain a buildnumber.')
            buildnumber = m[0]
            type_name = group_type_soup[index].find('span').get_text().strip()
            rating = group_rating_soup[index].find('div').get_text().strip()

            # Adding checkbox
            grep = [
                soup.get('buildnumber') for soup in
                checkbox_selected_soup if buildnumber == soup.get('buildnumber')]
            print_s(grep, len(grep))
            if len(grep) is not 0:
                self.selected[class_name].append(
                    {
                        'buildnumber': buildnumber,
                        'type_name': type_name,
                        'name': name,
                        'rating': rating
                    })
        print_s(len(self.selected[class_name]))
        sel = self.selected[class_name]
        print_s(sel)

    def write(self):
        f = open('build_numbers_p.txt', 'w')
        f.close()
        for class_name, build_list in self.selected:
            with open('build_numbers_p.txt', 'a') as file:
                file.write("# {}\n".format(class_name))
                for build in build_list:
                    file.write("{} # Rating: {} Name: {}\n".format(
                        build['buildnumber'],
                        build['rating'],
                        build['name']))
