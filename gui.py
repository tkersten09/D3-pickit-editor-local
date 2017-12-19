# Tutorial example. Doesn't depend on any third party GUI framework.
# Tested with CEF Python v56.2+

import base64
import platform
import sys
import threading
import re
from cefpython3 import cefpython as cef
from bs4 import BeautifulSoup
import inspect
from lib.gui_html import Builds

# HTML code. Browser will navigate to a Data uri created
# from this html code.
# HTML_code = ''
# with open('build_crusaider.html') as file:
#     print('read code')
#     HTML_code = file.read()


def print_s(*vars):
    for var in vars:
        callers_local_vars = inspect.currentframe().f_back.f_locals.items()
        var_name = [
            var_name for var_name, var_val in
            callers_local_vars if var_val is var]
        print('{}: {}'.format(var_name, var))


def main():
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    # To change user agent use either "product_version"
    # or "user_agent" options. Explained in Tutorial in
    # "Change user agent string" section.
    settings = {
    # "product_version": "MyProduct/10.00",
    # "user_agent": "MyAgent/20.00 MyProduct/10.00",
    # "debug": True,
    # "log_severity": cef.LOGSEVERITY_INFO,
    "log_file": "debug.log",
    }
    cef.Initialize(settings=settings)

    # Create Browser
    builds = Builds()
    browser = cef.CreateBrowserSync(url=html_to_data_uri(builds.HTML_code),
                                    window_title="Tutorial")
    # set_client_handlers(browser)
    print('lol')
    set_javascript_bindings(browser, builds)
    cef.MessageLoop()
    cef.Shutdown()


def check_versions():
    print("[tutorial.py] CEF Python {ver}".format(ver=cef.__version__))
    print("[tutorial.py] Python {ver} {arch}".format(
          ver=platform.python_version(), arch=platform.architecture()[0]))
    assert cef.__version__ >= "56.2", "CEF Python v56.2+ required to run this"


def html_to_data_uri(html, js_callback=None):
    """Function defined in Python, that is exported to Javascript.

    It uses Python Code to process data given from Javascript (html),
    and it sends its result to Javascript via the variable 'ret'.
    """
    # 1. From Python: in this case value is returned
    # 2. From Javascript: in this case value cannot be returned because
    #    inter-process messaging is asynchronous, so must return value
    #    by calling js_callback.
    html = html.encode("utf-8", "replace")
    b64 = base64.b64encode(html).decode("utf-8", "replace")
    ret = "data:text/html;base64,{data}".format(data=b64)
    return ret


def set_client_handlers(browser):
    client_handlers = [LoadHandler(), DisplayHandler()]
    for handler in client_handlers:
        browser.SetClientHandler(handler)


def set_javascript_bindings(browser, builds):
    bindings = cef.JavascriptBindings(
        bindToFrames=False, bindToPopups=False)
    # bindings.SetProperty("python_property", "This property was set in Python")
    # bindings.SetProperty("cefpython_version", cef.GetVersion())
    # bindings.SetFunction("html_to_data_uri", html_to_data_uri)
    # bindings.SetFunction("update", update)
    bindings.SetObject("builds", builds)
    browser.SetJavascriptBindings(bindings)


if __name__ == '__main__':
    main()
