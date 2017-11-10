#
# Copy this into
# ~/.ipython/extensions/
# In the ipython shell do:
# %load_ext drilsdown
# or
# %reload_ext drilsdown
#
# This needs to have IDV_HOME pointing to the IDV install directory
# This will execute IDV_HOME/runIdv
#

import sys
import os
import os.path
import re
import subprocess
import json
from base64 import b64encode
from IPython.display import HTML
from IPython.display import Image
from IPython.display import IFrame
from IPython.display import display
from IPython.display import Javascript
from IPython.display import clear_output
import tempfile
from tempfile import NamedTemporaryFile
from tempfile import gettempdir
from IPython.display import FileLink
import time
from IPython import get_ipython
from ipywidgets import *
import ipywidgets as widgets
from  zipfile import *
import requests
import xml.etree.ElementTree
from glob import glob
from os import listdir
from os.path import isfile, join
import IPython 
from IPython.lib import kernel


try:
    from urllib.request import urlopen
    from urllib.parse import urlparse, urlencode, urljoin
except ImportError:
    from urlparse import urljoin
    from urlparse import urlparse
    from urllib import urlopen, urlencode

idv_debug = 0


def read_url(url):
    """Utility to read a URL. Returns the text of the result"""
    try:
        return urlopen(url).read().decode("utf-8")
    except:
        print("Error reading url:" + url)


def testit(line, cell=None):
    print( os.listdir("."))


#
# Here are the magic commands
#

def idv_help(line, cell=None):
    DrilsdownUI.status("")
    html = "<pre>idv_help  Show this help message<br>" \
           + "run_idv<br>" \
           + "make_ui<br>" \
           + "load_bundle <bundle url or file path><br>" \
           + "           If no bundle given and if set_ramadda has been called the bundle will be fetched from RAMADDA<br>" \
           + "load_bundle_make_image <bundle url or file path><br>" \
           + "load_catalog Load the case study catalog into the IDV<br>" \
           + "make_image <-publish> <-caption ImageName> Capture an IDV image and optionally publish it to RAMADDA<br>" \
           + "make_movie <-publish> <-caption MovieName> Capture an IDV movie and optionally publish it to RAMADDA<br>" \
           + "save_bundle <xidv or zidv filename> <-publish> - write out the bundle and optionally publish to RAMADDA<br>" \
           + "publish_bundle  <xidv or zidv filename> - write out the bundle and publish it to RAMADDA<br>" \
           + "publish_notebook <notebook file name> - publish the current notebook to RAMADDA via the IDV<br>" \
           + "set_ramadda <ramadda url to a Drilsdown case study><br>" \
           + "createCaseStudy <case study name><br>" \
           + "set_bbox &lt;north west south east&gt; No arguments to clear the bbox<br></pre>"
    DrilsdownUI.do_display(HTML(html))


def run_idv(line=None, cell=None):
    """Magic hook to start the IDV"""
    Idv.run_idv(fromUser=True)


def load_catalog(line, cell=None):
    Idv.load_catalog(line)


def load_bundle_make_image(line, cell=None):
    load_bundle(line, cell)
    return make_image(line, cell)


def create_case_study(line, cell=None):
    url = Repository.theRepository.makeUrl("/entry/form?parentof="
                                           + Repository.theRepository.entryId
                                           + "&type=type_drilsdown_casestudy&name=" + line)
    url = url.replace(" ","%20")
    print("Go to this link to create the Case Study:")
    print(url)
    print("Then call %set_ramadda with the new Case Study URL")


def load_data(line, cell=None, name=None):
    Idv.load_data(line,name)
    

def load_bundle(line, cell=None):
    if line is None or line == "":
        if Repository.theRepository is not None:
            line = Repository.theRepository.makeUrl("/drilsdown/getbundle?entryid=" + Repository.theRepository.entryId)

    if line is None or line == "":
        print("No bundle argument provided")
        return

    Idv.load_bundle(line)


def make_image(line, cell=None):
    toks = line.split(" ")
    skip = 0
    publish = False
    caption = None
    display_id = None
    for i in range(len(toks)):
        if skip>0:
            skip = skip-1
            continue
        tok = toks[i].strip()
        if tok == "":
            continue
        if tok == "-publish":
            publish = True
        elif tok == "-caption":
            skip = 1
            caption = toks[i+1]
        elif tok == "-display":
            skip = 1
            display_id = toks[i+1]
        elif tok == "-help":
            print("%make_image <-display displayid> <-caption caption> <-publish>")
            return
        else:
            print("Unknown argument:" + tok)
            print("%make_image <-display displayid> <-caption caption> <-publish>")
            return
        
    return Idv.make_image(publish, caption, displayId=display_id)


def publish_notebook(line, cell=None):
    Idv.publish_notebook()


def make_movie(line, cell=None):
    toks = line.split(" ")
    skip = 0
    publish = False
    display_id = None
    for i in range(len(toks)):
        if skip > 0:
            skip = skip-1
            continue
        tok = toks[i]
        if tok == "-publish":
            publish = True
        elif tok == "-display":
            skip = 1
            display_id = toks[i+1]

    return Idv.make_movie(publish, displayId=display_id)


def set_ramadda(line, cell=None):
    """Set the ramadda to be used. The arg should be the normal /entry/view URL for a RAMADDA entry"""
    line_toks = line.split(" ")
    should_list = len(line_toks) == 1
    line = line_toks[0]
    Repository.setRepository(Ramadda(line), should_list)


def list_repository(entryId=None, repository=None):
    """List the entries held by the entry id"""
    if repository is None:
        repository = Repository.theRepository
    repository.list_entry(entryId)


def save_bundle(line, cell=None):
    extra = ""
    filename = "idv.xidv"
    publish = False
    toks = line.split(" ")
    for i in range(len(toks)):
        tok = toks[i]
        if tok!="":
            if tok == "-publish":
                publish= True
            else:
                filename = tok
    Idv.save_bundle(filename, publish)


def publish_bundle(line, cell=None):
    extra = " publish=\"true\" "
    filename = "idv.xidv"
    if line != "" and line is not None:
        filename = line
    Idv.publish_bundle(filename)


def set_bbox(line, cell=None):
    Idv.setBBOX(line)


def make_ui(line):
    DrilsdownUI.make_ui()


def load_ipython_extension(shell):
    """Define the magics"""
    magic_type = "line"
    shell.register_magic_function(testit, magic_type)
    shell.register_magic_function(idv_help, magic_type)
    shell.register_magic_function(run_idv, magic_type)
    shell.register_magic_function(make_ui, magic_type)
    shell.register_magic_function(load_bundle, magic_type)
    shell.register_magic_function(load_bundle_make_image, magic_type)
    shell.register_magic_function(load_catalog, magic_type)
    shell.register_magic_function(make_image, magic_type)
    shell.register_magic_function(make_movie, magic_type)
    shell.register_magic_function(set_ramadda, magic_type)
    shell.register_magic_function(create_case_study, magic_type)
    shell.register_magic_function(set_bbox, magic_type)
    shell.register_magic_function(save_bundle, magic_type)
    shell.register_magic_function(publish_bundle, magic_type)
    shell.register_magic_function(publish_notebook, magic_type)


class DrilsdownUI:
    """Handles all of the UI callbacks """
    idToRepository = {}

    @staticmethod
    def make_ui():
        global repositories
        name_map = {}
        names = []
        first = None
        for i in range(len(repositories)):
            repository = repositories[i]
            if i == 0:
                first = repository.getId()
            DrilsdownUI.idToRepository[repository.getId()] = repository
            name_map[repository.getName()] = repository.getId()
            names.append(repository.getName())


        text_layout=Layout(width='150px')
        repository_selector = widgets.Dropdown(
            options=name_map,
            value=first,
            )

        search = widgets.Text(
            layout=text_layout,
            value='',
            placeholder='IDV bundle',
            description='',
            disabled=False)

        search.on_submit(DrilsdownUI.handle_search)
        search.type = "type_idv_bundle"

        cssearch = widgets.Text(
            value='',
            layout=text_layout,
            placeholder='Case Study or folder',
            description='',
            disabled=False)
        cssearch.on_submit(DrilsdownUI.handle_search)
        cssearch.type = "type_drilsdown_casestudy"

        gridsearch = widgets.Text(
            value='',
            layout=text_layout,
            placeholder='Gridded data files',
            description='',
            disabled=False)
        gridsearch.on_submit(DrilsdownUI.handle_search)
        gridsearch.type = "cdm_grid"

        allsearch = widgets.Text(
            value='',
            layout=text_layout,
            placeholder='All',
            description='',
            disabled=False)
        allsearch.on_submit(DrilsdownUI.handle_search)
        allsearch.type = ""

        list_btn = DrilsdownUI.make_button("List", DrilsdownUI.list_repository_clicked)
        list_btn.entry = None
    
        cbx = widgets.Checkbox(
            value=False,
            description='Publish',
            disabled=False)

        repository_selector.observe(DrilsdownUI.repository_selector_changed, names='value')
        DrilsdownUI.statusLabel = Label("")
        display(VBox(
                [HTML("<h3>iPython-IDV Control Panel</h3>"),
                    HBox([HTML("<b>Resources:</b>"),
                            repository_selector,
                            list_btn]),
                    HBox([HTML("<b>Search for:</b>"), search,
                          cssearch, gridsearch, allsearch]),
                    HBox([DrilsdownUI.make_button("Run IDV",DrilsdownUI.run_idv_clicked),
                          DrilsdownUI.make_button("Make Image",DrilsdownUI.make_image_clicked, cbx),
                          DrilsdownUI.make_button("Make Movie",DrilsdownUI.make_movie_clicked,cbx),
                          DrilsdownUI.make_button("Save Bundle",DrilsdownUI.save_bundle_clicked,cbx),
                          DrilsdownUI.make_button("Publish Notebook",Idv.publish_notebook),
                          cbx]),
                    HBox([
                          # Label("Outputs append below until Cleared:"),
                          DrilsdownUI.make_button("Clear Outputs", DrilsdownUI.clear_clicked),
                          DrilsdownUI.make_button("Commands Help",idv_help),
                          DrilsdownUI.statusLabel
                    ]),
                 ]))

    displayedItems = []

    @staticmethod
    def do_display(comp):
        """Call this to display a component that can later be cleared with the Clear button"""
        display(comp)
        DrilsdownUI.displayedItems.append(comp)

    @staticmethod
    def status(text):
        DrilsdownUI.statusLabel.value = text

    @staticmethod
    def make_button(label, callback, extra=None):
        """Utility to make a button widget"""
        b = widgets.Button(
            description=label,
            disabled=False,
            button_style='',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip=label,
            )
        b.extra = extra
        b.on_click(callback)
        return b

    @staticmethod
    def handle_search(widget):
        type = widget.type
        value = widget.value.replace(" ", "%20")
        if hasattr(Repository.theRepository,"doSearch"):
            DrilsdownUI.status("Searching...")
            entries = Repository.theRepository.doSearch(value, type)
            Repository.theRepository.displayEntries("<b>Search Results:</b> " + widget.value + " <br>", entries)
            DrilsdownUI.status("")
        else:
            DrilsdownUI.status("Search not available")

    @staticmethod
    def run_idv_clicked(b):
        Idv.run_idv(fromUser=True)

    @staticmethod
    def save_bundle_clicked(b):
        extra = ""
        if b.extra.value:
            extra = "-publish"
        save_bundle(extra)

    @staticmethod
    def make_image_clicked(b):
        DrilsdownUI.status("")
        extra = ""
        if b.extra.value:
            extra = "-publish"
        image = make_image(extra)
        if image is not None:
            DrilsdownUI.do_display(image)

    @staticmethod
    def make_movie_clicked(b):
        DrilsdownUI.status("")
        if b.extra.value:
            movie = Idv.make_movie(True)
        else:
            movie = Idv.make_movie(False)
        if movie is not None:
            DrilsdownUI.do_display(movie)

    @staticmethod
    def load_bundle_clicked(b):
        load_bundle(b.entry.getFilePath())

    @staticmethod
    def view_url_clicked(b):
        DrilsdownUI.do_display(HTML("<a target=ramadda href=" + b.url + ">" + b.name + "</a>"))
        display(IFrame(src=b.url,width=800, height=400))

    @staticmethod
    def load_data_clicked(b):
        load_data(b.entry.getDataPath(), None, b.name)

    @staticmethod
    def set_data_clicked(b):
        url = b.entry.getDataPath()
        Idv.data_url = url
        print('To access the data use the variable: Idv.data_url or:\n' + url)

    @staticmethod
    def set_url_clicked(b):
        url = b.entry.makeGetFileUrl()
        Idv.file_url = url
        print('To access the URL use the variable: Idv.file_url or:\n' + url)

    @staticmethod
    def list_repository_clicked(b):
        if b.entry is None:
            list_repository(None)
        else:
            list_repository(b.entry.getId(), b.entry.getRepository())

    @staticmethod
    def load_catalog_clicked(b):
        load_catalog(b.url)

    @staticmethod
    def repository_selector_changed(s):
        repository = DrilsdownUI.idToRepository[s['new']]
        Repository.setRepository(repository)

    @staticmethod
    def clear_clicked(b):
        DrilsdownUI.status("")
        clear_output()
        for i in range(len(DrilsdownUI.displayedItems)):
            item = DrilsdownUI.displayedItems[i]
            if hasattr(item, "close"):
                item.close()
        DrilsdownUI.displayedItems = []
        clear_output()


class Idv:
    bbox = None
    data_url = None
    file_url = None
    path = None

# These correspond to the commands in ucar.unidata.idv.IdvMonitor
    cmd_ping = "/ping"
    cmd_loadisl = "/loadisl"

    base_url = None

# The port is defined by the idv.monitorport = 8765 in the .unidata/idv/DefaultIdv/idv.properties
    base_urls = ["http://127.0.0.1:8788", "http://127.0.0.1:8765"]

    @staticmethod
    def get_base_url():
        if Idv.base_url is not None:
            return Idv.base_url
        # Try the different ports
        for url in Idv.base_urls:
            try:
                urlopen(url + Idv.cmd_ping).read()
                Idv.base_url = url
                # print("Idv base url:"+ url)
                return Idv.base_url
            except:
                dummy = None
        return None

    @staticmethod
    def idv_ping():
        """This function checks if the IDV is running"""
# NOTE: Don't call idv_call here because idv_call calls run_idv which calls ping
        try:
            return urlopen(Idv.get_base_url() + Idv.cmd_ping).read()
        except:
            return None

    @staticmethod
    def set_path(path):
        """This function directly sets the path to the IDV executable"""
        Idv.path = path

    @staticmethod
    def set_port(port):
        """This function sets the port the IDV listens on"""
        Idv.base_url = "http://127.0.0.1:" + port

    @staticmethod
    def sniff_out_path():
        roots = ["/Applications", "C:\\Program Files"]
        majors = ["IDV_6", "IDV_5"]
        dots = ["9", "8", "7", "6", "5", "4", "3", "2", "1"]
        minors = ["u10", "u9", "u8", "u7", "u6", "u5", "u4", "u3", "u2", "u1", ""]
        for root in roots:
            for major in majors:
                for dot in dots:
                    for minor in minors:
                        dir = os.path.join(root, major + "." + dot + minor)
                        # print(dir)
                        if os.path.isdir(dir):
                            return dir
        return None

    @staticmethod
    def run_idv(fromUser=False):
        """Check if the IDV is running"""
        idvRunning = Idv.idv_ping()
        if idvRunning:
            if fromUser:
                DrilsdownUI.status("IDV is running")
            return

# path might have been set directly by set_path
        path = Idv.path
# Check if the env is defined
        if path is None:
            idvDir = None
            if "IDV_HOME" in os.environ:
                idvDir = os.environ['IDV_HOME']
            else:
                idvDir = Idv.sniff_out_path()

            if idvDir is None:
                print("No IDV_HOME environment variable set")
                Idv.print_set_path()
                return
            path = os.path.join(idvDir, "runIDV")
            # check for windows
            if not os.path.isfile(path):
                path = os.path.join(idvDir,"runIDV.bat")
            if not os.path.isfile(path):
                print("Could not find an executable IDV script in:")
                print(idvDir)
                Idv.print_set_path()
                return
        else:
            if not os.path.isfile(path):
                print("IDV exectuable does not exist:")
                print(path)
                return
                
        print("Starting IDV: " + path)
        cwd = os.path.dirname(path)
        subprocess.Popen([path], cwd=cwd)

    # Give the IDV a chance to get going
        suffix = ""
        for x in range(0, 60):
            if Idv.idv_ping() is not None:
                DrilsdownUI.status("IDV started")
                return
            if x % 2 == 0:
                DrilsdownUI.status("Waiting on the IDV " + suffix)
                suffix = suffix+"."
            time.sleep(1)
        DrilsdownUI.status("IDV failed to start (or is slow in starting)")

    @staticmethod
    def print_set_path():
        print("You can set the path to the IDV script with:")
        print("from drilsdown import Idv")
        print('Idv.set_path("/path to idv executable")')
        print('#e.g.:')
        print('Idv.set_path("/Applications/IDV_5.3u1/runIDV")')

    @staticmethod
    def idv_call(command, args=None):
        """
        Will start up the IDV if needed then call the command
        If args is non-null then this is a map of the url arguments to pass to the IDV
        """
        Idv.run_idv(fromUser = False)
# TODO: add better error handling
        try:
            url = Idv.get_base_url() +command
            if args:
                url += "?" + urlencode(args)
            if idv_debug:
                print("Calling " + url)
            html = urlopen(url).read()
            return html.decode("utf-8")
        except:
            return None

    @staticmethod
    def load_data(url, name=None):
        extra1 = ""
        extra2 = ""
        if name is not None:
            extra1 += ' name="' + name + '" '
        isl = '<isl>\n<datasource url="' + url + '" ' + extra1 + '/>' + extra2 + '\n</isl>'
        if Idv.idv_call(Idv.cmd_loadisl, {"isl": isl}) is None:
            print("load_data failed")
            return
        print("data loaded")

    theNotebook = "xx"

    def test():
        Idv.theNotebook = "yy"

    def setname(name):
        Idv.theNotebook = name
        print("NAME = " + name)

    @staticmethod
    def getname():
        # A hack from https://stackoverflow.com/questions/12544056/how-do-i-get-the-current-ipython-notebook-name to get the
        # name of the notebook file
        connection_file_path = kernel.get_connection_file()
        connection_file = os.path.basename(connection_file_path)
        kernel_id = connection_file.split('-', 1)[1].split('.')[0]
        print("connection file:" + connection_file_path)
        response = requests.get('http://127.0.0.1:{port}/api/sessions'.format(port=8888))
        print(response.text)
        matching = [s for s in json.loads(response.text) if s['kernel']['id'] == kernel_id]
        if matching:
            return os.getcwd() + "/" + matching[0]['notebook']['path']
        else:
            print("Could not find notebook filename")
            None

    @staticmethod
    def publish_notebook(extra=None):
        # If we do this then the Javascript object shows up in the notebook
        # js = Javascript('IPython.notebook.save_checkpoint();')
        # display(js)
        file = Idv.getname()
        if file is None:
            return
        isl = '<isl><publish file="' + file + '"/></isl>'
        DrilsdownUI.status("Make sure you do 'File->Save and Checkpoint'. Check your IDV to publish the file")
        result = Idv.idv_call(Idv.cmd_loadisl, {"isl": isl})
        if result is None:
            print("Publication failed")
            return
        if result.strip()!="":
            print("Publication successful")
            print("URL: " + result)
            return
        print("Publication failed")

    @staticmethod
    def setBBOX(line):
        toks = line.split()
        if len(toks) == 0:
            Idv.bbox = None
            print("BBOX is cleared")
            return
        Idv.bbox = []
        for i in range(len(toks)):
            Idv.bbox.append(float(toks[i]))
        print("BBOX is set")



    @staticmethod
    def load_catalog(url=None):
        if url is  None or url == "":
            url = Repository.theRepository.makeUrl("/entry/show?parentof=" + Repository.theRepository.entryId +"&amp;output=thredds.catalog")
        else:
            url = url.replace("&","&amp;")
        isl = '<isl>\n<loadcatalog url="' + url+'"/></isl>'
        if Idv.idv_call(Idv.cmd_loadisl, {"isl": isl}) == None:
            print("load_catalog failed")
            return

        print("Catalog loaded")

    @staticmethod
    def save_bundle(filename, publish=False):
        extra = ""
        filename = "idv.xidv"
        if publish:
            extra += ' publish="true" '
        isl = '<isl><save file="' + filename +'"' + extra +'/></isl>'
        result = Idv.idv_call(Idv.cmd_loadisl, {"isl": isl})
        if result is None:
            print("save failed")
            return
        if os.path.isfile(filename):
            DrilsdownUI.status("Bundle saved:" + filename)
            return FileLink(filename)
        DrilsdownUI.status("Bundle not saved")

    @staticmethod
    def load_bundle(bundleUrl, bbox=None):
        extra1 = ""
        extra2 = ""
        if bbox is None:
            bbox = Idv.bbox
        if bbox is not None:
            extra1 += 'bbox="' + repr(bbox[0]) + "," + repr(bbox[1]) + "," + repr(bbox[2]) + "," + repr(bbox[3]) + '"'
        # The padding is to reset the viewpoint to a bit larger area than the bbox
            padding = (float(bbox[0]) - float(bbox[2]))*0.1
            north = float(bbox[0])+padding
            west = float(bbox[1])-padding
        # For some reason we need to pad south a bit more
            south = float(bbox[2])-1.5*padding
            east = float(bbox[3])+padding
            extra2 += '<pause/><center north="' + repr(north) + '" west="' + repr(west) + '" south="'\
                      + repr(south) + '" east="' + repr(east) + '" />'
        isl = '<isl>\n<bundle file="' + bundleUrl + '" ' + extra1 + '/>' + extra2 + '\n</isl>'
        if Idv.idv_call(Idv.cmd_loadisl, {"isl": isl}) is None:
            DrilsdownUI.status("Bundle load failed")
            return
        DrilsdownUI.status("Bundle loaded")

    @staticmethod
    def publish_bundle(filename):
        extra = " publish=\"true\" "
        isl = '<isl><save file="' + filename + '"' + extra + '/></isl>'
        result = Idv.idv_call(Idv.cmd_loadisl, {"isl": isl})
        if result is None:
            print("save failed")
            return
        if result.strip() != "":
            print("Publication successful")
            print("URL: " + result)
        if os.path.isfile(filename):
            print("bundle saved:" + filename)
            return FileLink(filename)
        print("Publication failed")

    @staticmethod
    def make_movie(publish=False, caption=None, display=True, displayId=None):
        return Idv.make_imageOrMovie(False, publish, caption, display, displayId)

    @staticmethod
    def make_image(publish=False, caption=None, display=True, displayId=None):
        return Idv.make_imageOrMovie(True, publish, caption, display, displayId)

    @staticmethod
    def make_imageOrMovie(image, publish=False, caption=None, display=True, displayId=None):
        what = "movie"
        if image:
            what = "image"
        DrilsdownUI.status("Making " + what + "...")
        selfPublish = False
        idvPublish = False
        parent = None
        extra = ""
        extra2 = ""
        name = None
        ramadda = Repository.theRepository
        if type(publish) is bool:
            if publish:
                idvPublish = True
                extra = " publish=\"true\" "
        elif publish is not None:
            selfPublish = True
            if 'ramadda' in publish:
                ramadda = Ramadda(publish['ramadda'])
            if 'parent' in publish:
                parent = publish['parent']
            else:
                parent = ramadda.getId()
            if 'name' in publish:
                name = publish['name']
        if caption is not None:
            extra2 += '<matte bottom="50" background="white"/>'
            label = caption
            label = label.replace("-", " ")
            extra2 += '<overlay text="' + label + '"  place="LM,0,-10" anchor="LM"  color="black" fontsize="16"/>'
            extra2 += '<matte space="1"  background="black"/>'
        if name is None:
            name = caption

        if displayId is not None:
            extra += ' display="' + displayId + '" '
        with NamedTemporaryFile(suffix='.gif', delete=False) as f:
            isl = '<isl><' + what + ' combine="true" file="' + f.name + '"' \
                  + extra + '>' + extra2 + '</' + what + '></isl>'
            result = Idv.idv_call(Idv.cmd_loadisl, {"isl": isl})
            f.seek(0)
            if idvPublish:
                if result is None or result.strip() == "":
                    DrilsdownUI.status("make " + what + " failed")
                    return
                print("Publication successful " + "URL: " + result)
            if selfPublish:
                ramadda.publish(name, file=f.name, parent=parent)
            data = open(f.name, "rb").read()
            f.close()
            # data = b64encode(data).decode('ascii')
            # img = '<img src="data:image/gif;base64,{0}">'
            if display:
                DrilsdownUI.status("")
                return IPython.core.display.Image(data)
        DrilsdownUI.status("")


class Repository:
    theRepository = None

    def __init__(self, id):
        self.id = id

    def setRepository(repository, shouldList=False):
        """Set the repository to be used. The arg should be the normal /entry/view URL for a REPOSITORY entry"""
        Repository.theRepository = repository
        if shouldList:
            list_repository(Repository.theRepository.entryId, repository)
        return  Repository.theRepository

    def getId(self):
        return self.entryId

    def displayEntries(self, label="Entries", entries=[]):
        cnt = 0
        indent = HTML("&nbsp;&nbsp;&nbsp;")
        rows = [HTML(label)]
        for i in range(len(entries)):
            if cnt > 100:
                break
            cnt = cnt+1
            entry = entries[i]
            name = entry.getName()
            id = entry.getId()
            icon = entry.getIcon()
            fullName = name
            maxLength = 25
            if len(name)>maxLength:
                name = name[:maxLength-len(name)]
            name = name.ljust(maxLength," ")
            name = name.replace(" ","&nbsp;")
            row = []
            if entry.getUrl() is not None:
                href = self.makeEntryHref(id,  name, icon, fullName)
                href = "<span style=font-family:monospace;>" + href +"</span>"
                href = HTML(href)
                row = [indent, href]
            else:
                label = "<span style=font-family:monospace;>" + name + "</span>"
                row = [indent, HTML(label)]

            if entry.isBundle():
                b = DrilsdownUI.make_button("Load bundle", DrilsdownUI.load_bundle_clicked)
                b.entry = entry
                row.append(b)
                entry.addDisplayWidget(row)
            elif entry.isGrid():
                b = DrilsdownUI.make_button("Load data", DrilsdownUI.load_data_clicked)
                b.name = fullName
                b.entry = entry
                row.append(b)
                b = DrilsdownUI.make_button("Set data", DrilsdownUI.set_data_clicked)
                b.entry = entry
                row.append(b)
            elif entry.isGroup():
                b = DrilsdownUI.make_button("List", DrilsdownUI.list_repository_clicked)
                b.entry = entry
                row.append(b)
                catalogUrl = entry.getCatalogUrl()
                if catalogUrl is not None:
                    load_catalog = DrilsdownUI.make_button("Load Catalog", DrilsdownUI.load_catalog_clicked)
                    load_catalog.url = catalogUrl
                    row.append(load_catalog)
            else:
                if entry.getUrl() is not None:
                    b = DrilsdownUI.make_button("View", DrilsdownUI.view_url_clicked)
                    b.url = self.makeUrl("/entry/show?entryid=" + id)
                    b.name = name
                    row.append(b)
                    fileSize = entry.getFileSize()
                    if fileSize > 0:
                        link = self.makeUrl("/entry/get?entryid=" + id)
                        row.append(HTML('&nbsp;&nbsp;<a target=ramadda href="' + link+'">Download ('
                                        + repr(fileSize) + ' bytes) </a>'))
                else:
                    row.append(HTML('<a target=_filedownload href="' + entry.path + '">' + entry.path + '</>'))
            rows.append(HBox(row))

        DrilsdownUI.do_display(VBox(rows))
        if cnt == 0:
            DrilsdownUI.do_display(HTML("<b>No entries found</b>"))


class LocalFiles(Repository):
    def __init__(self, dir):
        if dir is None:
            self.dir = "."
        else:
            self.dir = dir
        self.cwd = self.dir
        self.name = "Local Files"
        self.searchCnt = 0

    def list_entry(self, entryId):
        """List the entries held by the entry id"""
        entries = self.doList(entryId)
        self.displayEntries("<b></b><br>", entries)

    def getId(self):
        return self.dir

    def getName(self):
        return self.name

    def getBase(self):
        return self.dir

    def doList(self, dir=None, display=False, label="Entries"):
        """make a list of RamaddaEntry objects that are children of the given entryId"""
        if dir is None:
            dir = self.dir
        files = os.listdir(dir)
        entries = []
        prefix = dir+"/"
        if prefix == "./":
            prefix = ""
        for i in range(len(files)):
            if files[i].startswith(".") is not True:
                entries.append(FileEntry(self, prefix + files[i]))

        if display:
            self.displayEntries(label, entries)
        else:
            return entries

    def doSearch(self, value, type=None):
        """Do a search for the text value and (optionally) the entry type. Return a list of RamaddaEntry objects"""
        self.searchCnt = 0
        # print("Search not supported for local files")
        files = []
        self.doSearchInner(value, self.dir, files, type)
        return files

    def doSearchInner(self, value, dir, list, type):
        # Only check so many files - should make this breadth firs
        if self.searchCnt > 5000:
            return
        files = os.listdir(dir)
        for i in range(len(files)):
            File = files[i]
            file = File.lower()
            if file.startswith("."):
                continue
            if re.match(value, File) or value in File or re.match(value, file) or value in file:
                ok = True
                if type is not None:
                    if type == "type_idv_bundle":
                        if not File.endswith(".xidv") and not File.endswith(".zidv"):
                            ok = False
                        
                    if type == "type_drilsdown_casestudy":
                        if not os.path.isdir(dir + "/" + file):
                            ok = False
                    if type == "cdm_grid":
                        if not File.endswith(".nc"):
                            ok = False
                if ok:
                    list.append(FileEntry(self,dir+"/" + file))
            if os.path.isdir(dir +"/" + file):
                self.doSearchInner(value, dir+"/" + file,list, type)


class TDS(Repository):
    def __init__(self, url,  name=None):
        self.url = url
        catalog = read_url(url)
        if name is not None:
            self.name = name
        else:
            root = xml.etree.ElementTree.fromstring(catalog)
            self.name = root.attrib['name']

    def list_entry(self, entryId):
        """List the entries held by the entry id"""
        entries = self.doList(entryId)
        self.displayEntries("<b></b><br>", entries)

    def getId(self):
        return self.url

    def getName(self):
        return self.name

    def getBase(self):
        return self.url

    def doList(self, url=None, display=False, label="Entries"):
        """make a list of RamaddaEntry objects that are children of the given entryId"""
        if url is None:
            url = self.url
        catalog = read_url(url)
        root = xml.etree.ElementTree.fromstring(catalog)
        entries = []
        for child in root:
            # print("child:" + child.tag)
            self.getEntries(root, url, child, entries)

        if display:
            self.displayEntries(label, entries)
        else:
            return entries

    def clean_tag(self, tag):
        tag = re.sub("{.*}", "", tag)
        return tag

    def getEntries(self, root, url, element, entries):
        tag = self.clean_tag(element.tag)

        if tag == "dataset":
            for child in element:
                self.getEntries(root, url, child, entries)
            serviceName = self.findServiceName(root)
            if serviceName is not None:
                print("dataset:" + element.attrib["name"])
                return
            return
        if tag == "catalogRef":
            href = element.attrib["{http://www.w3.org/1999/xlink}href"]
            title = element.attrib["{http://www.w3.org/1999/xlink}title"]
            url = urljoin(url, href)
            entries.append(TDSCatalogEntry(self, url, title))
            return
            
        return

    def findOpendapServices(self, parentService, element, map):
        # serviceType="OPENDAP"
        return

    def findServiceName(self, element):

        if element.tag == "serviceName":
            return element.text
        for child in element:
            name = self.findServiceName(child)
            if name is not None:
                return name
        return None


class Ramadda(Repository):
    theRamadda = None
    def __init__(self, url, name=None):
        self.url = url
        toks = urlparse(url)
        self.host = toks.scheme +"://" + toks.netloc
        self.base = toks.scheme +"://" + toks.netloc
        path = re.sub("/entry.*","", toks.path)
        self.base += path
        self.entryId = re.search("entryid=([^&]+)", toks.query).group(1)
        if name is not None:
            self.name = name
        else:
            toks = read_url(self.makeUrl("/entry/show?output=entry.csv&escapecommas=true&fields=name,icon&entryid="
                                         + self.entryId)).split("\n")[1].split(",")
            self.name = toks[0].replace("_comma_", ",")

    def getId(self):
        return self.entryId

    def getName(self):
        return self.name

    def getBase(self):
        return self.base

    def list_entry(self, entryId):
        if entryId is None:
            entryId = self.entryId
        """List the entries held by the entry id"""
#        print(self.makeUrl("/entry/show?output=entry.csv&escapecommas=true&fields=name,icon&entryid=" + entryId))
        toks = read_url(self.makeUrl("/entry/show?output=entry.csv&escapecommas=true&fields=name,icon&entryid="
                                     + entryId)).split("\n")[1].split(",")
        baseName = toks[0]
        baseName = baseName.replace("_comma_",",")
        icon = toks[1]
        entries = self.doList(entryId)
        self.displayEntries("<b>" + "<img src=" + self.host + icon+"> "
                            + "<a target=self href=" + self.base + "/entry/show?entryid="
                            + entryId + ">" + baseName+"</a></b><br>", entries)

    def doList(self, entryId=None, display=False, label="Entries"):
        """make a list of RamaddaEntry objects that are children of the given entryId"""
        if entryId is None:
            entryId = self.entryId
        csv = read_url(self.makeUrl("/entry/show?entryid=" + entryId
                                    + "&output=default.csv&escapecommas=true&fields=name,id,type,icon,url,size&orderby=name"))
        entries = self.makeEntries(csv)
        if display:
            self.displayEntries(label, entries)
        else:
            return  entries

    def doSearch(self, value, type=None):
        """Do a search for the text value and (optionally) the entry type. Return a list of RamaddaEntry objects"""
        entries =[]
        if type is None or type == "":
            url = self.makeUrl(
                "/search/do?output=default.csv&escapecommas=true&fields=name,id,type,icon,url,size&orderby=name&text="
                + value)
        else:
            url = self.makeUrl(
                "/search/type/" + type
                + "?output=default.csv&escapecommas=true&orderby=name&fields=name,id,type,icon,url,size&text="
                + value)
        csv = read_url(url)
        return self.makeEntries(csv)

    def makeEntries(self, csv):
        """Convert the RAMADDA csv into a list of RamaddaEntry objects """
        entries =[]
        lines = csv.split("\n")
        cnt = 0
        for i in range(len(lines)):
            if i == 0:
                continue
            line2 = lines[i]
            line2 = line2.split(",")
            if len(line2) >= 5:
                cnt = cnt+1
                name = line2[0]
                name = name.replace("_comma_",",")
                id = line2[1]
                type = line2[2]
                icon = line2[3]
                url = line2[4]
                fileSize = 0
                try:
                    fileSize = float(line2[5])
                except:
                    print("bad line:" + line2[5])
                entry = RamaddaEntry(self, name, id, type,icon, url, fileSize)
                entries.append(entry)
        return entries

    def makeUrl(self, path):
        """Add the ramadda base path to the given url path"""
        return self.base + path

    def makeEntryUrl(self, entryId):
        """make a href for the given entry"""
        return self.base + '/entry/show?entryid=' + entryId

    def makeEntryHref(self, entryId, name, icon=None, alt=""):
        """make a href for the given entry"""
        html = '<a target=ramadda title="' + alt + '" href="' + self.base + '/entry/show?entryid=' + entryId + '">' + name + '</a>'
        if icon is not None:
            html = "<img src=" + self.host + icon+"> " + html
        return html

    def publish(self, name, file=None, parent=None):
        if "RAMADDA_USER" not in os.environ:
            print("No RAMADDA_USER environment variable set")
            return

        if "RAMADDA_PASSWORD" not in os.environ:
            print("No RAMADDA_PASSWORD environment variable set")
            return

        user = os.environ['RAMADDA_USER']
        password = os.environ['RAMADDA_PASSWORD']

        if parent is None:
            parent = self.entryId

        extra = ""
        if file is not None:
            extra += ' file="' + os.path.basename(file) + '" '
        entryXml = '<entry name="' + name + '" ' + extra + '/>'
        with NamedTemporaryFile(suffix='.zip') as tmpZip:
            with ZipFile(tmpZip.name, 'w') as myzip:
                with NamedTemporaryFile(suffix='.xml') as tmpFile:
                    entriesFile = open(tmpFile.name, 'w')
                    entriesFile.write(entryXml)
                    entriesFile.close()
                    myzip.write(tmpFile.name, arcname='entries.xml')
                if file is not None:
                    myzip.write(file)
            files = {'file': open(tmpZip.name, 'rb')}
            # TODO: change http to https
            url = self.makeUrl("/entry/xmlcreate")
            r = requests.post(url, files=files,
                              data={'group': parent,'auth.user': user,'auth.password': password,'response': 'xml'})
            root = xml.etree.ElementTree.fromstring(r.text)
            if root.attrib['code'] == 'ok':
                for child in root:
                    display(HTML("Published file: " + self.makeEntryHref(child.attrib['id'],name)))
            else:
                print('Error publishing file')
                print(r.text)


class RepositoryEntry:
    def __init__(self, repository, name, id, type, icon, fileSize):
        self.repository = repository
        self.name =  name.replace("_comma_",",")
        self.id = id
        self.type = type
        self.icon = icon
        self.fileSize = fileSize

    def getFilePath(self):
        return None

    def getDataPath(self):
        return self.getFilePath()

    def getCatalogUrl(self):
        return None

    def getRepository(self):
        return self.repository

    def getName(self):
        return self.name

    def getId(self):
        return self.id

    def getType(self):
        return self.type

    def getIcon(self):
        return self.icon

    def getUrl(self):
        return None

    def getFileSize(self):
        return self.fileSize

    def isBundle(self):
        return False

    def isGrid(self):
        return self.getType() == "cdm_grid" or self.getName().endswith(".nc")

    def isGroup(self):
        return False

    def addDisplayWidget(self, row):
        return


class TDSCatalogEntry(RepositoryEntry):
    def __init__(self, repository, url, name):
        RepositoryEntry.__init__(self,repository, name, url, "", None, 0)
        self.url  = url

    def getFilePath(self):
        return self.url

    def isGroup(self):
        return True

    def getCatalogUrl(self):
        return self.url




class FileEntry(RepositoryEntry):
    def __init__(self, repository, path):
        # print(path)
        RepositoryEntry.__init__(self,repository, path, path, "", None, os.path.getsize(path))
        self.path  = path

    def getFilePath(self):
        return os.getcwd() + "/" + self.path

    def getDataPath(self):
        return self.getFilePath()

    def isBundle(self):
        return self.path.find("xidv") >=0 or self.path.find("zidv")>=0

    def isGroup(self):
        return os.path.isdir(self.path)


class RamaddaEntry(RepositoryEntry):
    def __init__(self, ramadda, name, id, type, icon,  url, fileSize):
        RepositoryEntry.__init__(self,ramadda, name, id, type, icon, fileSize)
        self.url = url

    def getFilePath(self):
        return self.url
        # return  self.getRepository().makeUrl("/entry/get?entryid=" + self.getId())

    def getDataPath(self):
        return self.makeOpendapUrl()

    def getCatalogUrl(self):
        return self.repository.makeUrl("/entry/show?output=thredds.catalog&entryid=" + self.id)

    def getIcon(self):
        return self.icon

    def getUrl(self):
        return self.url

    def isBundle(self):
        return self.getType() == "type_idv_bundle" or self.getUrl().find("xidv") >= 0 \
                                 or self.getUrl().find("zidv") >= 0

    def isGrid(self):
        return self.getType() == "cdm_grid" or self.getName().endswith(".nc")

    def isGroup(self):
        return self.getType() == "type_drilsdown_casestudy" or self.getType() == "group" \
                                 or self.getType() == "localfiles"

    def makeOpendapUrl(self):
        return self.getRepository().base +"/opendap/" + self.id +"/entry.das"

    def makeGetFileUrl(self):
        return self.getRepository().base +"/entry/get?entryid=" + self.id

    def addDisplayWidget(self,row):
        b = DrilsdownUI.make_button("Set URL", DrilsdownUI.set_url_clicked)
        b.entry = self
        row.append(b)
        link = self.getRepository().makeUrl("/entry/show/?output=idv.islform&entryid=" + self.getId())
        row.append(HTML('<a target=ramadda href="' + link +'">Subset Bundle</a>'))


# Make the REPOSITORIES
repositories = [Ramadda("http://weather.rsmas.miami.edu/repository/entry/show?entryid=45e3b50b-dbe2-408b-a6c2-2c009749cd53",
                        "The Mapes IDV Collection"),
                Ramadda("http://geodesystems.com/repository/entry/show?entryid=12704a38-9a06-4989-aac4-dafbbe13a675",
                        "Geode Systems Drilsdown Collection"),
                Ramadda("https://www.esrl.noaa.gov/psd/repository/entry/show?entryid=f8d470f4-a072-4c1e-809e-d6116a393818",
                        "NOAA-ESRL-PSD Climate Data Repository"),
                # Ramadda("http://ramadda.atmos.albany.edu:8080/repository?entryid=643aa629-c53d-48cb-8454-572fad73cb0f",
                #         "University of Albany RAMADDA"),
                TDS("http://thredds.ucar.edu/thredds/catalog.xml",
                    "Unidata THREDDS Data Server"),
                Ramadda("http://motherlode.ucar.edu/repository/entry/show?entryid=0",
                        "Unidata RAMADDA Server"),
                TDS("http://weather.rsmas.miami.edu/thredds/catalog.xml",
                    "University of Miami THREDDS Data Server"),
                LocalFiles(".")

]
Repository.theRepository = repositories[0]

make_ui("")

        


