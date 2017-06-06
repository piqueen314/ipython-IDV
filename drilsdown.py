# drillsdown.py

#
# Copy this into
# ~/.ipython/extensions/
# In the ipython shell do:
#%load_ext drilsdown
#or
#%reload_ext drilsdown
#
# This needs to have IDV_HOME pointing to the IDV install directory
# This will execute IDV_HOME/runIdv
#

import sys;
import os;
import os.path;
import re;
import subprocess;
from base64 import b64encode;
from IPython.display import HTML;
from IPython.display import Image;
from IPython.display import IFrame;
from IPython.display import display;
from IPython.display import clear_output;
from tempfile import NamedTemporaryFile;
from IPython.display import FileLink;
import time;
from IPython import get_ipython;
from ipywidgets import *;
import ipywidgets as widgets;
from  zipfile import *;
import requests;
import xml.etree.ElementTree
from glob import glob
from os import listdir
from os.path import isfile, join






try:
    from urllib.request import urlopen
    from urllib.parse import urlparse, urlencode, urljoin
except ImportError:
    from urlparse import urljoin
    from urlparse import urlparse
    from urllib import urlopen, urlencode

idvDebug = 0;


displayedItems = [];

def doDisplay(comp):
    """Call this to display a component that can later be cleared with the Clear button"""
    global displayedItems;
    display(comp);
    displayedItems.append(comp);



def readUrl(url):
    """Utility to read a URL. Returns the text of the result"""
    try:
        return urlopen(url).read().decode("utf-8");
    except:
        print("Error reading url:" + url);







def testit(line, cell=None):
    print( os.listdir("."));




##
## Here are the magic commands
##

def idvHelp(line, cell=None):
    html =  "<pre>idvHelp  Show this help message<br>" + \
    "runIdv<br>" + \
    "makeUI<br>" +\
    "loadBundle <bundle url or file path><br>" + \
    "           If no bundle given and if setRamadda has been called the bundle will be fetched from RAMADDA<br>" +\
    "loadBundleMakeImage <bundle url or file path><br>" +\
    "loadCatalog Load the case study catalog into the IDV<br>" +\
    "makeImage <-publish> <-caption ImageName> Capture an IDV image and optionally publish it to RAMADDA<br>" +\
    "makeMovie <-publish> <-caption MovieName> Capture an IDV movie and optionally publish it to RAMADDA<br>" +\
    "saveBundle <xidv or zidv filename> <-publish> - write out the bundle and optionally publish to RAMADDA<br>" +\
    "publishBundle  <xidv or zidv filename> - write out the bundle and publish it to RAMADDA<br>" +\
    "publishNotebook <notebook file name> - publish the current notebook to RAMADDA via the IDV<br>" +\
    "setRamadda <ramadda url to a Drilsdown case study><br>" +\
    "createCaseStudy <case study name><br>" +\
    "setBBOX &lt;north west south east&gt; No arguments to clear the bbox<br></pre>";
    doDisplay(HTML(html));

def runIdv(line = None, cell=None):
    """Magic hook to start the IDV"""
    Idv.runIdv();


def loadCatalog(line, cell=None):
    Idv.loadCatalog(line);

def loadBundleMakeImage(line, cell=None):
    loadBundle(line,cell);
    return makeImage(line,cell);

def createCaseStudy(line, cell=None):
    url = Repository.theRepository.makeUrl("/entry/form?parentof=" + Repository.theRepository.entryId +"&type=type_drilsdown_casestudy&name=" + line);
    url = url.replace(" ","%20");
    print ("Go to this link to create the Case Study:");
    print (url);
    print("Then call %setRamadda with the new Case Study URL");


def loadData(line, cell=None, name = None):
    Idv.loadData(line,name);
    

def loadBundle(line, cell=None):
    if line == None or line == "":
        if Repository.theRepository is not None:
            line = Repository.theRepository.makeUrl("/drilsdown/getbundle?entryid=" + Repository.theRepository.entryId);

    if line == None or line == "":
        print ("No bundle argument provided");
        return;

    Idv.loadBundle(line);


def makeImage(line, cell=None):
    toks = line.split(" ");
    skip = 0;
    publish = False;
    caption = None;
    for i in range(len(toks)):
        if skip>0:
            skip = skip-1;
            continue;
        tok  = toks[i];
        if tok == "-publish":
            publish = True;
        elif tok == "-caption":
            skip = 1;
            caption = toks[i+1];
    Idv.makeImage(publish, caption);



def publishNotebook(line, cell=None):
    filename = "notebook.ipynb";
    if line != "" and line is not None:
        filename = line;
    Idv.publishNotebook(filename);



def makeMovie(line, cell=None):
    publish  = False;
    if line == "-publish":
        publish = True;
    Idv.makeMovie(publish);


def setRamadda(line, cell=None):
    """Set the ramadda to be used. The arg should be the normal /entry/view URL for a RAMADDA entry"""
    lineToks  = line.split(" ");
    shouldList =  len(lineToks)==1;
    line = lineToks[0];
    Repository.setRepository(Ramadda(line), shouldList);



def listRepository(entryId = None, repository=None):
    """List the entries held by the entry id"""
    if repository is None:
        repository = Repository.theRepository;
    repository.listEntry(entryId);

def saveBundle(line, cell=None):
    extra = "";
    filename = "idv.xidv";
    publish = False;
    toks = line.split(" ");
    for i in range(len(toks)):
        tok  = toks[i];
        if tok!="":
            if tok == "-publish":
                publish= True;
            else:
                filename = tok;
    Idv.saveBundle(filename, publish);


def publishBundle(line, cell=None):
    extra = " publish=\"true\" ";
    filename = "idv.xidv";
    if line != "" and line is not None:
        filename = line;
    Idv.publishBundle(filename);


def setBBOX(line, cell=None):
    Idv.setBBOX(line);



def load_ipython_extension(shell):
    """Define the magics"""
    magicType = "line";
    shell.register_magic_function(testit, magicType);
    shell.register_magic_function(idvHelp, magicType);
    shell.register_magic_function(runIdv, magicType);
    shell.register_magic_function(makeUI, magicType);
    shell.register_magic_function(loadBundle, magicType);
    shell.register_magic_function(loadBundleMakeImage, magicType);
    shell.register_magic_function(loadCatalog, magicType);
    shell.register_magic_function(makeImage, magicType);
    shell.register_magic_function(makeMovie, magicType);
    shell.register_magic_function(setRamadda, magicType);
    shell.register_magic_function(createCaseStudy, magicType);
    shell.register_magic_function(setBBOX, magicType);
    shell.register_magic_function(saveBundle, magicType);
    shell.register_magic_function(publishBundle, magicType);
    shell.register_magic_function(publishNotebook, magicType);




def makeUI(line):
    DrilsdownUI.makeUI();


class DrilsdownUI:
    """Handles all of the UI callbacks """
    idToRepository = {};


    def makeUI():
        global repositories;
        nameMap = {};
        names = [];
        first = None;
        for i in range(len(repositories)):
            repository = repositories[i];
            if i == 0:
                first = repository.getId();
            DrilsdownUI.idToRepository[repository.getId()] = repository;
            nameMap[repository.getName()] =  repository.getId();
            names.append(repository.getName());


        textLayout=Layout(width='150px');
        repositorySelector = widgets.Dropdown(
            options=nameMap,
            value=first,
            );

        search = widgets.Text(
            layout=textLayout,
            value='',
            placeholder='IDV bundle',
            description='',
            disabled=False)

        search.on_submit(DrilsdownUI.handleSearch);
        search.type = "type_idv_bundle";

        cssearch = widgets.Text(
            value='',
            layout=textLayout,
            placeholder='Case Study or folder',
            description='',
            disabled=False)
        cssearch.on_submit(DrilsdownUI.handleSearch);
        cssearch.type = "type_drilsdown_casestudy";


        gridsearch = widgets.Text(
            value='',
            layout=textLayout,
            placeholder='Gridded data files',
            description='',
            disabled=False)
        gridsearch.on_submit(DrilsdownUI.handleSearch);
        gridsearch.type = "cdm_grid";

        allsearch = widgets.Text(
            value='',
            layout=textLayout,
            placeholder='All',
            description='',
            disabled=False)
        allsearch.on_submit(DrilsdownUI.handleSearch);
        allsearch.type = "";

        listBtn = DrilsdownUI.makeButton("List",DrilsdownUI.listRepositoryClicked);
        listBtn.entry = None;
    
        cbx = widgets.Checkbox(
            value=False,
            description='Publish',
            disabled=False);

        repositorySelector.observe(DrilsdownUI.repositorySelectorChanged,names='value');
        display(VBox(
                [HTML("<h3>iPython-IDV Control Panel</h3>"),
                    HBox([HTML("<b>Resources:</b>"),
                            repositorySelector,
                            listBtn]),
                    HBox([HTML("<b>Search for:</b>"), search,
                          cssearch, gridsearch, allsearch]),
                    HBox([DrilsdownUI.makeButton("Run IDV",DrilsdownUI.runIDVClicked),
                            DrilsdownUI.makeButton("Make Image",DrilsdownUI.makeImageClicked, cbx),
                            DrilsdownUI.makeButton("Make Movie",DrilsdownUI.makeMovieClicked,cbx),
                            DrilsdownUI.makeButton("Save Bundle",DrilsdownUI.saveBundleClicked,cbx),
                            cbx]),



                    HBox([
#Label("Outputs append below until Cleared:"),
                          DrilsdownUI.makeButton("Clear Outputs",DrilsdownUI.clearClicked),
                          DrilsdownUI.makeButton("List Available Commands",idvHelp)]),
                    ]));

    def makeButton(label, callback, extra=None):
        """Utility to make a button widget"""
        b = widgets.Button(
            description=label,
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip=label,
            )
        b.extra  = extra;
        b.on_click(callback);
        return b;


    def handleSearch(widget):
        type = widget.type;
        value  =  widget.value.replace(" ","%20");
        entries = Repository.theRepository.doSearch(value, type);
        Repository.theRepository.displayEntries("<b>Search Results:</b> " + widget.value +" <br>", entries);

    def runIDVClicked(b):
        runIdv("");

    def saveBundleClicked(b):
        extra = "";
        if b.extra.value == True:
            extra = "-publish"
        saveBundle(extra);

    def makeImageClicked(b):
        extra = "";
        if b.extra.value:
            extra = "-publish"
        makeImage(extra);

    def makeMovieClicked(b):
        if b.extra.value:
            Idv.makeMovie(True);
        else:
            Idv.makeMovie(False);

    def loadBundleClicked(b):
        loadBundle(b.entry.getFilePath());

    def viewUrlClicked(b):
        doDisplay(HTML("<a target=ramadda href=" + b.url +">" + b.name+"</a>"));
        display(IFrame(src=b.url,width=800, height=400));


    def loadDataClicked(b):
        loadData(b.entry.getDataPath(), None, b.name);


    def setDataClicked(b):
        url  = b.entry.getDataPath();
        Idv.dataUrl = url;
        print('To access the data use the variable: Idv.dataUrl or:\n' + url);

    def setUrlClicked(b):
        url  = b.entry.makeGetFileUrl();
        Idv.fileUrl = url;
        print('To access the URL use the variable: Idv.fileUrl or:\n' + url);

    def listRepositoryClicked(b):
        if b.entry is None:
            listRepository(None);
        else:
            listRepository(b.entry.getId(), b.entry.getRepository());


    def loadCatalogClicked(b):
        loadCatalog(b.url);

    def repositorySelectorChanged(s):
        repository = DrilsdownUI.idToRepository[s['new']];
        Repository.setRepository(repository);


    def clearClicked(b):
        clear_output();
        global displayedItems;
        for i in range(len(displayedItems)):
            displayedItems[i].close();




class Idv:
    bbox = None;
    dataUrl = None;
    fileUrl = None;

#These correspond to the commands in ucar.unidata.idv.IdvMonitor
    cmd_ping = "/ping";
    cmd_loadisl = "/loadisl";

#The port is defined by the idv.monitorport = 8765 in the .unidata/idv/DefaultIdv/idv.properties
    idvBaseUrl = "http://127.0.0.1:8765";


    def idvPing():
        """This function checks if the IDV is running"""

#NOTE: Don't call idvCall here because idvCall calls runIdv which calls ping
        try:
            return  urlopen(Idv.idvBaseUrl +Idv.cmd_ping).read();
        except:
            return None;


    def runIdv():
        """Check if the IDV is running"""
        idvRunning = Idv.idvPing();
        if  idvRunning:
            return;
#Check if the env is defined
        if "IDV_HOME" not in os.environ:
            print ("No IDV_HOME environment variable set");
            return;
        path = os.environ['IDV_HOME'] +"/runIDV";
        print ("Starting IDV: " + path);
        subprocess.Popen([path]) 
    #Give the IDV a chance to get going
        for x in range(0, 60):
            if Idv.idvPing() != None:
                print("IDV started");
                return;
            if x % 5 == 0:
                print ("Waiting on the IDV");
            time.sleep(1);
        print ("IDV failed to start (or is slow in starting)");





    def idvCall(command, args=None):
        """
        Will start up the IDV if needed then call the command
        If args is non-null then this is a map of the url arguments to pass to the IDV
        """
        runIdv();
#TODO: add better error handling 
        try:
            url = Idv.idvBaseUrl +command;
            if args:
                url += "?" + urlencode(args);
            if idvDebug:
                print("Calling " + url);
            html  = urlopen(url).read();
            return html.decode("utf-8");
        except:
            return None;


    def loadData(url, name=None):
        extra1 = "";
        extra2 = "";
        if name  is not None:
            extra1 += ' name="' + name +'" ';
        isl = '<isl>\n<datasource url="' + url +'" ' + extra1 +'/>' + extra2 +'\n</isl>';
        if Idv.idvCall(Idv.cmd_loadisl, {"isl": isl}) == None:
            print("loadData failed");
            return;
        print("data loaded");
    
    def publishNotebook(filename):
        ipython = get_ipython();
        ipython.magic("notebook -e " + filename);
        file = os.getcwd() + "/" + filename;
        isl = '<isl><publish file="'  + file +'"/></isl>';
        print("Check your IDV to publish the file");
        result  = Idv.idvCall(Idv.cmd_loadisl, {"isl": isl});
        if result  is None:
            print("Publication failed");
            return;
        if result.strip()!="":
            print("Publication successful");
            print("URL: " + result);
            return
        print("Publication failed");


    def setBBOX(line):
        toks = line.split();
        if len(toks) == 0:
            Idv.bbox = None;
            print("BBOX is cleared");
            return;
        Idv.bbox = [];
        for i in range(len(toks)):
            Idv.bbox.append(float(toks[i]));
        print("BBOX is set");



    def loadCatalog(url = None):
        if url is  None or url  == "":
            url = Repository.theRepository.makeUrl("/entry/show?parentof=" + Repository.theRepository.entryId +"&amp;output=thredds.catalog");
        else:
            url = url.replace("&","&amp;");
        isl = '<isl>\n<loadcatalog url="' + url+'"/></isl>';
        if Idv.idvCall(Idv.cmd_loadisl, {"isl": isl}) == None:
            print("loadCatalog failed");
            return;

        print("Catalog loaded");


    def saveBundle(filename, publish=False):
        extra = "";
        filename = "idv.xidv";
        if publish:
            extra +=' publish="true" '
        isl = '<isl><save file="' + filename +'"' + extra +'/></isl>';
        result = Idv.idvCall(Idv.cmd_loadisl, {"isl": isl});
        if result == None:
            print("save failed");
            return;
        print(filename);
        if os.path.isfile(filename):
            print ("bundle saved:" + filename);
            return FileLink(filename)
        print ("bundle not saved");


    def loadBundle(bundleUrl, bbox=None):
        print("bundle: "  + bundleUrl);
        extra1 = "";
        extra2 = "";
        if bbox is  None:
            bbox = Idv.bbox;
        if bbox is not None:
            extra1 += 'bbox="' + repr(bbox[0]) +"," +repr(bbox[1]) +"," + repr(bbox[2]) +"," + repr(bbox[3]) +'"';
        ##The padding is to reset the viewpoint to a bit larger area than the bbox
            padding = (float(bbox[0]) - float(bbox[2]))*0.1;
            north = float(bbox[0])+padding;
            west = float(bbox[1])-padding;
        ##For some reason we need to pad south a bit more
            south = float(bbox[2])-1.5*padding;
            east = float(bbox[3])+padding;
            extra2 += '<pause/><center north="' + repr(north) +'" west="' + repr(west) +'" south="'  + repr(south) +'" east="' + repr(east) +'" />';
        isl = '<isl>\n<bundle file="' + bundleUrl +'" ' + extra1 +'/>' + extra2 +'\n</isl>';
        print(isl);
        if Idv.idvCall(Idv.cmd_loadisl, {"isl": isl}) == None:
            print("loadBundle failed");
            return;
##        print("bundle loaded");


    def publishBundle(filename):
        extra = " publish=\"true\" ";
        isl = '<isl><save file="' + filename +'"' + extra +'/></isl>';
        result = Idv.idvCall(Idv.cmd_loadisl, {"isl": isl});
        if result is None:
            print("save failed");
            return;
        if result.strip() != "":
            print("Publication successful");
            print("URL: " + result);
        if os.path.isfile(filename):
            print ("bundle saved:" + filename);
            return FileLink(filename)
        print ("Publication failed");



    def makeMovie(publish=False, caption=None, display=True):
        Idv.makeImageOrMovie(False, publish, caption, display);

    def makeImage(publish=False, caption=None, display=True):
        Idv.makeImageOrMovie(True, publish, caption, display);

    def makeImageOrMovie(image, publish=False, caption=None, display=True):
        what = "movie";
        if image:
            what = "image";
        selfPublish=False
        idvPublish = False;
        parent=None
        extra = "";
        extra2 = "";
        name = None;
        ramadda =  Repository.theRepository;
        if type(publish) is bool:
            if publish:
                idvPublish  = True;
                extra = " publish=\"true\" ";
        elif publish is not None:
            selfPublish = True;
            if 'ramadda' in publish:
                ramadda = Ramadda(publish['ramadda']);
            if 'parent' in publish:
                parent = publish['parent'];
            else:
                parent = ramadda.getId();
            if 'name' in publish:
                name = publish['name'];
        if caption is not None:
            extra2 +=    '<matte bottom="50" background="white"/>';
            label = caption;
            label = label.replace("-"," ");
            extra2 +=    '<overlay text="' + label +'"  place="LM,0,-10" anchor="LM"  color="black" fontsize="16"/>';
            extra2 +=    '<matte space="1"  background="black"/>';
        if name is None:
            name = caption;
        with NamedTemporaryFile(suffix='.gif') as f:
            isl = '<isl><' + what +' combine="true" file="' + f.name +'"' + extra +'>' + extra2  +'</' + what +'></isl>';
            result = Idv.idvCall(Idv.cmd_loadisl, {"isl": isl});
            if idvPublish:
                if result == None or result.strip()=="":
                    print("make " + what + " failed");
                    return;
                print("Publication successful");
                print("URL: " + result);
            if selfPublish:
                ramadda.publish(name,file=f.name, parent=parent);
            data = open(f.name, "rb").read()
            data = b64encode(data).decode('ascii');
            img = '<img src="data:image/gif;base64,{0}">';
            if display:
                doDisplay(HTML(img.format(data)));




class Repository:
    theRepository = None;
    def __init__(self, id):
        self.id = id;

    def setRepository(repository, shouldList=False):
        """Set the repository to be used. The arg should be the normal /entry/view URL for a REPOSITORY entry"""
        Repository.theRepository = repository;
        if shouldList:
            listRepository(Repository.theRepository.entryId, repository);
        return  Repository.theRepository;




    def getId(self):
        return self.entryId;




    def doSearch(self, value, type=None):
        print("Search not available");

    
    def displayEntries(self, label="Entries", entries=[]):
        cnt = 0;
        indent = HTML("&nbsp;&nbsp;&nbsp;");
        rows=[HTML(label)];
        for i in range(len(entries)):
            if cnt > 100:
                break;
            cnt = cnt+1;
            entry = entries[i];
            name  = entry.getName();
            id = entry.getId();
            icon = entry.getIcon();
            fullName = name;
            maxLength  = 25;
            if len(name)>maxLength:
                name = name[:maxLength-len(name)];
            name = name.ljust(maxLength," ");
            name = name.replace(" ","&nbsp;");
            row = [];
            if entry.getUrl() is not None:
                href = self.makeEntryHref(id,  name, icon, fullName);
                href  = "<span style=font-family:monospace;>" + href +"</span>";
                href = HTML(href);
                row = [indent, href];
            else:
                label  = "<span style=font-family:monospace;>" + name +"</span>";
                row = [indent, HTML(label)];

            if entry.isBundle():
                b  = DrilsdownUI.makeButton("Load bundle",DrilsdownUI.loadBundleClicked);
                b.entry = entry;
                row.append(b);
                entry.addDisplayWidget(row);
            elif entry.isGrid():
                b  = DrilsdownUI.makeButton("Load data",DrilsdownUI.loadDataClicked);
                b.name =fullName;
                b.entry  = entry;
                row.append(b);
                b  = DrilsdownUI.makeButton("Set data",DrilsdownUI.setDataClicked);
                b.entry  = entry;
                row.append(b);
            elif entry.isGroup():
                b  = DrilsdownUI.makeButton("List",DrilsdownUI.listRepositoryClicked);
                b.entry = entry;
                row.append(b);
                catalogUrl = entry.getCatalogUrl();
                if catalogUrl is not None:
                    loadCatalog  = DrilsdownUI.makeButton("Load Catalog",DrilsdownUI.loadCatalogClicked);
                    loadCatalog.url = catalogUrl;
                    row.append(loadCatalog);
            else:
                if entry.getUrl() is not None:
                    b  = DrilsdownUI.makeButton("View",DrilsdownUI.viewUrlClicked);
                    b.url = self.makeUrl("/entry/show?entryid=" + id);
                    b.name = name;
                    row.append(b);
                    fileSize = entry.getFileSize();
                    if fileSize>0:
                        link = self.makeUrl("/entry/get?entryid=" + id);
                        row.append(HTML('&nbsp;&nbsp;<a target=ramadda href="' + link+'">Download (' + repr(fileSize) +' bytes) </a>'));
                else:
                    row.append(HTML('<a target=_filedownload href="' + entry.path +'">' + entry.path +'</>'));
            rows.append(HBox(row));

        doDisplay(VBox(rows));
        if cnt == 0:
            doDisplay(HTML("<b>No entries found</b>"));


class LocalFiles(Repository):
    def __init__(self, dir):
        if dir is None:
            self.dir = ".";
        else:
            self.dir = dir;
        self.cwd = self.dir;
        self.name =   "Local Files";
        self.searchCnt = 0;

    def listEntry(self, entryId):
        """List the entries held by the entry id"""
        entries = self.doList(entryId);
        self.displayEntries("<b></b><br>", entries);


    def getId(self):
        return self.dir;

    def getName(self):
        return self.name;

    def getBase(self):
        return self.dir;

    def doList(self, dir = None, display=False, label="Entries"):
        """make a list of RamaddaEntry objects that are children of the given entryId"""
        if dir is None:
            dir = self.dir;
        files =  os.listdir(dir);
        entries = [];
        prefix  = dir+"/";
        if prefix == "./":
            prefix = "";
        for i in range(len(files)):
            if files[i].startswith(".") is not True:
                entries.append(FileEntry(self, prefix + files[i]));

        if display:
            self.displayEntries(label, entries);
        else:
            return  entries;

    def doSearch(self, value, type=None):
        """Do a search for the text value and (optionally) the entry type. Return a list of RamaddaEntry objects"""
        self.searchCnt  = 0;
##        print("Search not supported for local files");
        files = [];
        self.doSearchInner(value,self.dir, files, type);
        return files;

    def doSearchInner(self, value, dir, list, type):
        ##Only check so many files - should make this breadth firs
        if self.searchCnt > 5000:
            return;
        files =  os.listdir(dir);
        for i in range(len(files)):
            File = files[i];
            file = File.lower();
            if file.startswith("."):
                continue;
            if re.match(value, File) or value in File or re.match(value, file) or value in file:
                ok =True;
                if type is not None:
                    if type == "type_idv_bundle":
                        if not File.endswith(".xidv") and not File.endswith(".zidv"):
                            ok  = False;
                        
                    if type == "type_drilsdown_casestudy":
                        if not os.path.isdir(dir +"/" + file):
                            ok = False;
                    if type =="cdm_grid":
                        if not File.endswith(".nc"):
                            ok  =False;
                if ok:
                    list.append(FileEntry(self,dir+"/" + file));
            if os.path.isdir(dir +"/" + file):
                self.doSearchInner(value, dir+"/" + file,list, type);


class TDS(Repository):
    def __init__(self, url,  name=None):
        self.url = url;
        catalog =  readUrl(url);
        if name is not None:
            self.name = name;
        else:
            root = xml.etree.ElementTree.fromstring(catalog);
            self.name = root.attrib['name'];

    def listEntry(self, entryId):
        """List the entries held by the entry id"""
        entries = self.doList(entryId);
        self.displayEntries("<b></b><br>", entries);


    def getId(self):
        return self.url;

    def getName(self):
        return self.name;

    def getBase(self):
        return self.url;

    def doList(self, url = None, display=False, label="Entries"):
        """make a list of RamaddaEntry objects that are children of the given entryId"""
        if url is None:
            url = self.url;
        catalog =  readUrl(url);
        root = xml.etree.ElementTree.fromstring(catalog);
        entries= [];
        for child in root:
#            print("child:" + child.tag);
            self.getEntries(root, url, child, entries);

        if display:
            self.displayEntries(label, entries);
        else:
            return  entries;

    def cleanTag(self, tag):
        tag = re.sub("{.*}","", tag);
        return tag;
        

    def getEntries(self, root, url, element, entries):
        tag = self.cleanTag(element.tag);

        if tag == "dataset":
            for child in element:
                self.getEntries(root, url, child, entries);
            serviceName = self.findServiceName(root);
            if serviceName is not None:
                print("dataset:" + element.attrib["name"]);
                return;
            return;
        if tag == "catalogRef":
            href = element.attrib["{http://www.w3.org/1999/xlink}href"];
            title = element.attrib["{http://www.w3.org/1999/xlink}title"];
            url = urljoin(url, href);
            entries.append(TDSCatalogEntry(self, url, title));
            return;
            
        return;

    def findOpendapServices(self, parentService, element, map):
##        serviceType="OPENDAP"
        return;

    def findServiceName(self, element):

        if element.tag == "serviceName":
            return element.text;
        for child in element:
            name = self.findServiceName(child);
            if name is not None:
                return name;
        return None;




    def doSearch(self, value, type=None):
        print("Search not supported for TDS repositories");
        return [];


class Ramadda(Repository):
    theRamadda = None;
    def __init__(self, url, name=None):
        self.url = url;
        toks = urlparse(url);
        self.host = toks.scheme +"://" + toks.netloc;
        self.base = toks.scheme +"://" + toks.netloc;
        path = re.sub("/entry.*","", toks.path);
        self.base += path;
        self.entryId = re.search("entryid=([^&]+)", toks.query).group(1);
        if name is not None:
            self.name = name;
        else:
            toks =  readUrl(self.makeUrl("/entry/show?output=entry.csv&escapecommas=true&fields=name,icon&entryid=" + self.entryId)).split("\n")[1].split(",");
            self.name =   toks[0].replace("_comma_",",");


    def getId(self):
        return self.entryId;

    def getName(self):
        return self.name;

    def getBase(self):
        return self.base;

    def listEntry(self, entryId):
        if entryId is None:
            entryId = self.entryId;
        """List the entries held by the entry id"""
#        print(self.makeUrl("/entry/show?output=entry.csv&escapecommas=true&fields=name,icon&entryid=" + entryId));
        toks =  readUrl(self.makeUrl("/entry/show?output=entry.csv&escapecommas=true&fields=name,icon&entryid=" + entryId)).split("\n")[1].split(",");
        baseName =  toks[0];
        baseName  = baseName.replace("_comma_",",");
        icon =  toks[1];
        entries = self.doList(entryId);
        self.displayEntries("<b>" + "<img src=" + self.host + icon+"> " + "<a target=self href=" +self.base +"/entry/show?entryid=" + entryId +">" + baseName+"</a></b><br>", entries);




    def doList(self, entryId = None, display=False, label="Entries"):
        """make a list of RamaddaEntry objects that are children of the given entryId"""
        if entryId is None:
            entryId = self.entryId;
        csv = readUrl(self.makeUrl("/entry/show?entryid=" + entryId +"&output=default.csv&escapecommas=true&fields=name,id,type,icon,url,size&orderby=name"));
        entries = self.makeEntries(csv);
        if display:
            self.displayEntries(label, entries);
        else:
            return  entries;

    def doSearch(self, value, type=None):
        """Do a search for the text value and (optionally) the entry type. Return a list of RamaddaEntry objects"""
        entries =[];
        if type == None or type=="":
            url = self.makeUrl("/search/do?output=default.csv&escapecommas=true&fields=name,id,type,icon,url,size&orderby=name&text=" + value);
        else:
            url = self.makeUrl("/search/type/" + type +"?output=default.csv&escapecommas=true&orderby=name&fields=name,id,type,icon,url,size&text=" + value);    
        csv = readUrl(url);
        return self.makeEntries(csv);


    def makeEntries(self, csv):
        """Convert the RAMADDA csv into a list of RamaddaEntry objects """
        entries =[];
        lines =  csv.split("\n");
        cnt = 0;
        for i in range(len(lines)):
            if i == 0:
                continue;
            line2 = lines[i];
            line2 =  line2.split(",");
            if len(line2)>=5:
                cnt = cnt+1;
                name = line2[0];
                name  = name.replace("_comma_",",");
                id = line2[1];
                type = line2[2];
                icon = line2[3];
                url = line2[4];
                fileSize = 0;
                try:
                    fileSize = float(line2[5]);
                except:
                    print("bad line:" + line2[5]);
                entry = RamaddaEntry(self, name, id, type,icon, url, fileSize);
                entries.append(entry);
        return entries;

    
    def makeUrl(self,path):
        """Add the ramadda base path to the given url path"""
        return self.base + path;


    def makeEntryUrl(self, entryId):
        """make a href for the given entry"""
        return  self.base  +'/entry/show?entryid=' + entryId;

    def makeEntryHref(self, entryId, name, icon = None, alt = ""):
        """make a href for the given entry"""
        html = '<a target=ramadda title="' + alt +'" href="' + self.base  +'/entry/show?entryid=' + entryId  + '">' + name +'</a>';
        if icon is not None:
            html = "<img src=" + self.host + icon+"> " + html;
        return html;
    

    def publish(self, name, file=None, parent=None):
        if "RAMADDA_USER" not in os.environ:
            print ("No RAMADDA_USER environment variable set");
            return;

        if "RAMADDA_PASSWORD" not in os.environ:
            print ("No RAMADDA_PASSWORD environment variable set");
            return;

        user = os.environ['RAMADDA_USER'];
        password = os.environ['RAMADDA_PASSWORD'];

        if parent == None:
            parent = self.entryId

        extra = "";
        if file is not None:
            extra += ' file="' + os.path.basename(file) +'" ';
        entryXml = '<entry name="' + name +  '" ' + extra +'/>';
        with NamedTemporaryFile(suffix='.zip') as tmpZip:
            with ZipFile(tmpZip.name, 'w') as myzip:
                with NamedTemporaryFile(suffix='.xml') as tmpFile:
                    entriesFile = open(tmpFile.name, 'w')
                    entriesFile.write(entryXml);
                    entriesFile.close();
                    myzip.write(tmpFile.name,arcname='entries.xml');
                if file is not None:
                    myzip.write(file);
            files = {'file': open(tmpZip.name, 'rb')}
            ##TODO: change http to https
            url = self.makeUrl("/entry/xmlcreate");
            r = requests.post(url, files=files, data = {'group':parent,'auth.user':user,'auth.password': password,'response':'xml'})
            root = xml.etree.ElementTree.fromstring(r.text);
            if root.attrib['code'] == 'ok':
                for child in root:
                    display(HTML("Published file: " +self.makeEntryHref(child.attrib['id'],name)));
            else:
                print('Error publishing file');
                print(r.text);


class RepositoryEntry:
    def __init__(self, repository, name, id, type, icon, fileSize):
        self.repository = repository;
        self.name =  name.replace("_comma_",",");
        self.id = id;
        self.type = type;
        self.icon = icon;
        self.fileSize = fileSize;

    def getFilePath(self):
        return None;

    def getDataPath(self):
        return self.getFilePath();

    def getCatalogUrl(self):
        return None;

    def getRepository(self):
        return self.repository;

    def getName(self):
        return self.name;

    def getId(self):
        return self.id;

    def getType(self):
        return self.type;

    def getIcon(self):
        return self.icon;

    def getUrl(self):
        return None;

    def getFileSize(self):
        return self.fileSize;

    def isBundle(self):
        return False;

    def isGrid(self):
        return self.getType() == "cdm_grid" or self.getName().endswith(".nc");

    def isGroup(self):
        return False;

    def addDisplayWidget(self, row):
        return;


class TDSCatalogEntry(RepositoryEntry):
    def __init__(self, repository, url, name):
        RepositoryEntry.__init__(self,repository, name, url, "", None, 0);
        self.url   = url;

    def getFilePath(self):
        return self.url;

    def isGroup(self):
        return True;

    def getCatalogUrl(self):
        return self.url;




class FileEntry(RepositoryEntry):
    def __init__(self, repository, path):
##        print(path);
        RepositoryEntry.__init__(self,repository, path, path, "", None, os.path.getsize(path));
        self.path   = path;


    def getFilePath(self):
        return os.getcwd() + "/" + self.path;

    def getDataPath(self):
        return self.getFilePath();

    def isBundle(self):
        return self.path.find("xidv") >=0 or self.path.find("zidv")>=0;

    def isGroup(self):
        return os.path.isdir(self.path);


class RamaddaEntry(RepositoryEntry):
    def __init__(self, ramadda, name, id, type, icon,  url, fileSize):
        RepositoryEntry.__init__(self,ramadda, name, id, type, icon, fileSize);
        self.url = url;

    def getFilePath(self):
        return  self.getRepository().makeUrl("/entry/get?entryid=" + self.getId())

    def getDataPath(self):
        return self.makeOpendapUrl()

    def getCatalogUrl(self):
        return self.repository.makeUrl("/entry/show?output=thredds.catalog&entryid=" + self.id);

    def getIcon(self):
        return self.icon;

    def getUrl(self):
        return self.url;

    def isBundle(self):
        return self.getType() == "type_idv_bundle" or self.getUrl().find("xidv") >=0 or self.getUrl().find("zidv")>=0;

    def isGrid(self):
        return self.getType() == "cdm_grid" or self.getName().endswith(".nc");

    def isGroup(self):
        return self.getType()=="type_drilsdown_casestudy" or self.getType()=="group" or self.getType()=="localfiles";

    def makeOpendapUrl(self):
        return  self.getRepository().base +"/opendap/" + self.id +"/entry.das";

    def makeGetFileUrl(self):
        return  self.getRepository().base +"/entry/get?entryid=" + self.id;

    def addDisplayWidget(self,row):
        b  = DrilsdownUI.makeButton("Set URL",DrilsdownUI.setUrlClicked);
        b.entry = self;
        row.append(b);
        link = self.getRepository().makeUrl("/entry/show/?output=idv.islform&entryid=" + self.getId());
        row.append(HTML('<a target=ramadda href="' + link +'">Subset Bundle</a>'));


##Make the REPOSITORIES
repositories  =[Ramadda("http://weather.rsmas.miami.edu/repository/entry/show?entryid=45e3b50b-dbe2-408b-a6c2-2c009749cd53","The Mapes IDV Collection"),
           Ramadda("http://geodesystems.com/repository/entry/show?entryid=12704a38-9a06-4989-aac4-dafbbe13a675", "Geode Systems Drilsdown Collection"),
            Ramadda("https://www.esrl.noaa.gov/psd/repository/entry/show?entryid=f8d470f4-a072-4c1e-809e-d6116a393818","NOAA-ESRL-PSD Climate Data Repository"),
##                Ramadda("http://ramadda.atmos.albany.edu:8080/repository?entryid=643aa629-c53d-48cb-8454-572fad73cb0f","University of Albany RAMADDA"),
           TDS("http://thredds.ucar.edu/thredds/catalog.xml","Unidata THREDDS Data Server"),
            Ramadda("http://motherlode.ucar.edu/repository/entry/show?entryid=0","Unidata RAMADDA Server"),
                TDS("http://weather.rsmas.miami.edu/thredds/catalog.xml","University of Miami THREDDS Data Server"),
            LocalFiles(".")

];
Repository.theRepository = repositories[0];


#import DrilsdownDefaults;

#if not  DrilsdownDefaults.generatedNotebook:

makeUI("");

        

