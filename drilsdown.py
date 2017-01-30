# drillsdown.py

#
# Copy this into
# ~/.ipython/extensions/
# In the ipython shell to see the available commands do:
# %idvHelp
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





try:
    from urllib.request import urlopen
    from urllib.parse import urlparse, urlencode
except ImportError:
    from urlparse import urlparse
    from urllib import urlopen, urlencode


idvDebug = 0;

##Use geodesystems drilsdown folder as the default
ramaddaHost = "http://geodesystems.com";
ramaddaBase = "http://geodesystems.com/repository";
ramaddaEntryId = "12704a38-9a06-4989-aac4-dafbbe13a675";


#How we talk to the running IDV
#The port is defined by the idv.monitorport = 8765 in the .unidata/idv/DefaultIdv/idv.properties
idvBaseUrl = "http://127.0.0.1:8765";

#These correspond to the commands in ucar.unidata.idv.IdvMonitor
cmd_ping = "/ping";
cmd_loadisl = "/loadisl";


#The global bounding box
bbox = None;

def runIdv(line = None, cell=None):
#Check if the IDV is running
    idvRunning = idvPing();
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
        if idvPing() != None:
            print("IDV started");
            return;
        if x % 5 == 0:
            print ("Waiting on the IDV");
        time.sleep(1);
    print ("IDV failed to start (or is slow in starting)");

#
#Will start up the IDV if needed then call the command
#If args is non-null then this is a map of the url arguments to pass to the IDV
#
def idvCall(command, args=None):
    runIdv();
#TODO: add better error handling 
    try:
        url = idvBaseUrl +command;
        if args:
            url += "?" + urlencode(args);
        if idvDebug:
            print("Calling " + url);
        html  = urlopen(url).read();
        return html.decode("utf-8");
    except:
        return None;

#This function checks if the IDV is running
def idvPing():
#NOTE: Don't call idvCall here because idvCall calls runIdv which calls ping
    try:
        return  urlopen(idvBaseUrl +cmd_ping).read();
    except:
        return None;

def readUrl(url):
    return urlopen(url).read().decode("utf-8");


def makeButton(label, callback):
    b = widgets.Button(
        description=label,
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip=label,
        )
    b.on_click(callback);
    return b;

def handleSearch(widget):
    global ramaddaBase;
    if ramaddaBase == None or ramaddaBase == "":
        print("You need to call setRamadda first");
        return;
    type = widget.type;
    value  =  widget.value.replace(" ","%20");
    if type == "":
        url = ramaddaBase +"/search/do?output=default.csv&fields=name,id,type,icon&text=" + value;
    else:
        url = ramaddaBase +"/search/type/" + type +"?output=default.csv&fields=name,id,type,icon&text=" + value;    
    csv = readUrl(url);
    display(HTML("<b>Search Results:</b> " + widget.value +" <br>"));
    listCsv(csv);



def makeUI(line):
    global ramaddaEntryId;
    search = widgets.Text(
    value='',
    placeholder='Search for an IDV bundle',
    description='',
    disabled=False)
    search.on_submit(handleSearch);
    search.type = "type_idv_bundle";

    cssearch = widgets.Text(
    value='',
    placeholder='Search for a Drilsdown Case Study',
    description='',
    disabled=False)
    cssearch.on_submit(handleSearch);
    cssearch.type = "type_drilsdown_casestudy";


    gridsearch = widgets.Text(
    value='',
    placeholder='Search for gridded data',
    description='',
    disabled=False)
    gridsearch.on_submit(handleSearch);
    gridsearch.type = "cdm_grid";

    allsearch = widgets.Text(
    value='',
    placeholder='Search for anything',
    description='',
    disabled=False)
    allsearch.on_submit(handleSearch);
    allsearch.type = "";


    listBtn = makeButton("List",listRamaddaClicked);
    listBtn.entryid = "";
    display(VBox([
                HBox([makeButton("Run IDV",runIDVClicked),
                      makeButton("Make Image",makeImageClicked),
                      makeButton("Make Movie",makeMovieClicked),
                      listBtn,
                      makeButton("Help",idvHelp)]),
                HBox([search,
                      cssearch]),
                HBox([gridsearch,
                      allsearch]),
                
]));

def runIDVClicked(b):
    runIdv("");

def makeImageClicked(b):
    display(makeImage(""));

def makeMovieClicked(b):
    display(makeMovie(""));

def loadBundleClicked(b):
    loadBundle(b.url);

def viewUrlClicked(b):
    display(HTML("<a target=ramadda href=" + b.url +">" + b.name+"</a>"));
    display(IFrame(src=b.url,width=800, height=400));


def loadDataClicked(b):
    loadData(b.url);

def listRamaddaClicked(b):
    global ramaddaEntryId;
#   display(HTML("<hr>"));
    if b.entryid == "":
        listRamadda(ramaddaEntryId);
    else:
        listRamadda(b.entryid);


def loadCatalogClicked(b):
    loadCatalog(b.url);



##
## Here are the magic commands
##

def idvHelp(line, cell=None):
    print("idvHelp  Show this help message");
    print("runIdv");
    print("makeUI");
    print("loadBundle <bundle url or file path>");
    print("           If no bundle given and if setRamadda has been called the bundle will be fetched from RAMADDA");
    print("loadBundleMakeImage <bundle url or file path>");
    print("loadCatalog Load the case study catalog into the IDV");
    print("makeImage <-publish> Capture an IDV image and optionally publish it to RAMADDA");
    print("makeMovie <-publish> Capture an IDV movie and optionally publish it to RAMADDA");
    print("saveBundle <xidv or zidv filename> <-publish> - write out the bundle and optionally publish to RAMADDA");
    print("publishBundle  <xidv or zidv filename> - write out the bundle and publish it to RAMADDA");
    print("publishNotebook <notebook file name> - publish the current notebook to RAMADDA via the IDV");
    print("setRamadda <ramadda url to a Drilsdown case study (or setCaseStudy)>");
    print("createCaseStudy <case study name>");
    print("setBBOX <north west south east> No arguments to clear the bbox");




def loadCatalog(line, cell=None):
    global ramaddaEntryId;
    global ramaddaBase;
    url = "";
    if line  != "":
        url = line;
        url = url.replace("&","&amp;");
    else:
        if ramaddaBase == None or ramaddaBase == "":
            print("You need to call setRamadda first");
            return;
        url = ramaddaBase +"/entry/show?parentof=" + ramaddaEntryId +"&amp;output=thredds.catalog";
    isl = '<isl>\n<loadcatalog url="' + url+'"/></isl>';
    if idvCall(cmd_loadisl, {"isl": isl}) == None:
        print("loadCatalog failed");
        return;
    print("Catalog loaded");
    print("Check your IDV");



def loadBundleMakeImage(line, cell=None):
    loadBundle(line,cell);
    return makeImage(line,cell);

def createCaseStudy(line, cell=None):
    global ramaddaBase;
    global ramaddaEntryId;
    if ramaddaBase == None or ramaddaBase == "":
        print("You need to call setRamadda first");
        return;
    url = ramaddaBase +"/entry/form?parentof=" + ramaddaEntryId +"&type=type_drilsdown_casestudy&name=" + line;
    url = url.replace(" ","%20");
    print ("Go to this link to create the Case Study:");
    print (url);
    print("Then call %setRamadda with the new Case Study URL");


def loadData(line, cell=None):
    extra1 = "";
    extra2 = "";
    isl = '<isl>\n<datasource url="' + line +'" ' + extra1 +'/>' + extra2 +'\n</isl>';
    if idvCall(cmd_loadisl, {"isl": isl}) == None:
        print("loadData failed");
        return;
    print("data loaded");
    

def loadBundle(line, cell=None):
    global bbox;
    global ramaddaBase;
    global ramaddaEntryId;
    if line == None or line == "":
        if ramaddaBase is not None:
            line = ramaddaBase +"/drilsdown/getbundle?entryid=" + ramaddaEntryId;

    if line == None or line == "":
        print ("No bundle argument provided");
        return;
    extra1 = "";
    extra2 = "";
    if bbox is not None:
        extra1 += 'bbox="' + bbox[0] +"," +bbox[1] +"," + bbox[2] +"," + bbox[3] +'"';
        ##The padding is to reset the viewpoint to a bit larger area than the bbox
        padding = (float(bbox[0]) - float(bbox[2]))*0.1;
        north = float(bbox[0])+padding;
        west = float(bbox[1])-padding;
        ##For some reason we need to pad south a bit more
        south = float(bbox[2])-1.5*padding;
        east = float(bbox[3])+padding;
        extra2 += '<pause/><center north="' + repr(north) +'" west="' + repr(west) +'" south="'  + repr(south) +'" east="' + repr(east) +'" />';
    isl = '<isl>\n<bundle file="' + line +'" ' + extra1 +'/>' + extra2 +'\n</isl>';
    if idvCall(cmd_loadisl, {"isl": isl}) == None:
        print("loadBundle failed");
        return;
    print("bundle loaded");


def makeImage(line, cell=None):
    extra = "";
    if line == "-publish":
        extra = " publish=\"true\" ";

    with NamedTemporaryFile(suffix='.png') as f:
        isl = '<isl><image combine="true" file="' + f.name +'"' + extra +'><matte space="5"/></image></isl>';
        result = idvCall(cmd_loadisl, {"isl": isl});
        if result == None:
            print("makeImage failed");
            return;
        if line == "-publish":
            print("Publication successful");
            print("URL: " + result);
        data = open(f.name, "rb").read()
        data = b64encode(data).decode('ascii');
        img = '<img src="data:image/gif;base64,{0}">';
        return HTML(img.format(data));


def publishNotebook(line, cell=None):
    filename = "notebook.ipynb";
    if line != "" and line is not None:
        filename = line;
    ipython = get_ipython();
    ipython.magic("notebook -e " + filename);
    file = os.getcwd() + "/" + filename;
    isl = '<isl><publish file="'  + file +'"/></isl>';
    print("Check your IDV to publish the file");
    result  = idvCall(cmd_loadisl, {"isl": isl});
    if result  == None:
        print("publish failed");
        return;
    if result != "" and result is not None:
        print("Publication successful");
        print("URL: " + result);
        return
    print("Publication failed");


def makeMovie(line, cell=None):
    extra = "";
    if line == "-publish":
        extra = " publish=\"true\" ";

    data ="";
    with NamedTemporaryFile(suffix='.gif') as f:
        isl = '<isl><movie file="' + f.name + '"' + extra +'/></isl>';
        result  = idvCall(cmd_loadisl, {"isl": isl});
        if result == None:
            print("makeMovie failed");
            return;
        if result != "" and result is not None:
            print("Publication successful");
            print("URL: " + result);

        data = open(f.name, "rb").read()
        data = b64encode(data).decode('ascii');
        img = '<img src="data:image/gif;base64,{0}">';
        return HTML(img.format(data));

def setCaseStudy(line, cell=None):
    return setRamadda(line, cell);

##The arg should be the normal /entry/view URL for a RAMADDA entry
def setRamadda(line, cell=None):
    toks = urlparse(line);
    global ramaddaBase;
    global ramaddaEntryId;
    global ramaddaHost;

    ramaddaHost = toks.scheme +"://" + toks.netloc;
    ramaddaBase = toks.scheme +"://" + toks.netloc;
    path = re.sub("/entry.*","", toks.path);
    ramaddaBase += path;
    ramaddaEntryId = re.search("entryid=([^&]+)", toks.query).group(1);
    listRamadda(ramaddaEntryId);



#
#make a href for the given entry
#
def makeEntryHref(entryId, name, icon = None):
    global ramaddaBase;
    global ramaddaHost;
    html = '<a target=ramadda href="' + ramaddaBase  +'/entry/show?entryid=' + entryId  + '">' + name +'</a>';
    if icon is not None:
        html = "<img src=" + ramaddaHost + icon+"> " + html;
    return html;

#
#List the entries held by the entry id
#
def listRamadda(entryId):
    global ramaddaBase;
    global ramaddaHost;
    toks =  readUrl(ramaddaBase+"/entry/show?output=entry.csv&fields=name,icon&entryid=" + entryId).split("\n")[1].split(",");
    baseName =  toks[0];
    icon =  toks[1];
    display(HTML("<b>" + "<img src=" + ramaddaHost + icon+"> " + "<a target=ramadda href=" +ramaddaBase +"/entry/show?entryid=" + entryId +">" + baseName+"</a></b><br>"));
    csv = readUrl(ramaddaBase+"/entry/show?entryid=" + entryId +"&output=default.csv&fields=name,id,type,icon");
    listCsv(csv);


#
#Display the csv listing of entries from RAMADDA
#
def listCsv(csv):
    lines =  csv.split("\n");
    html = "";
    cnt = 0;
    indent = HTML("&nbsp;&nbsp;&nbsp;");
    for i in range(len(lines)):
        if cnt > 100:
            break;
        if i > 0:
            line2 =  lines[i].split(",");
            if len(line2)==4 :
                cnt = cnt+1;
                name = line2[0];
                id = line2[1];
                type = line2[2];
                icon = line2[3];
                if len(name)>20:
                    name = name[:20-len(name)];

                name = name.ljust(20," ");
                name = name.replace(" ","&nbsp;");
                name  = "<span style=font-family:monospace;>" + name +"</span>";
                href = makeEntryHref(id,  name, icon);

                href = HTML(href);
                if type == "type_idv_bundle":
                    b  = makeButton("Load bundle",loadBundleClicked);
                    b.url  = ramaddaBase +"/entry/get?entryid=" + id;
                    box = HBox([indent, href, b ])
                    display(box);
                elif type == "cdm_grid" or name.endswith(".nc") :
                    b  = makeButton("Load data",loadDataClicked);
                    b.url  = ramaddaBase +"/entry/get?entryid=" + id;
                    box = HBox([indent, href, b])
                    display(box);
                elif type=="type_drilsdown_casestudy" or type=="group":
                    b  = makeButton("List",listRamaddaClicked);
                    b.entryid = id;
                    loadCatalog  = makeButton("Load Catalog",loadCatalogClicked);
                    loadCatalog.url = ramaddaBase +"/entry/show?output=thredds.catalog&entryid=" + id;
                    box = HBox([indent, href, b, loadCatalog]);
                    display(box);
                else:
                    b  = makeButton("View",viewUrlClicked);
                    b.url = ramaddaBase + "/entry/show?entryid=" + id;
                    b.name = name;
                    box = HBox([indent, href, b  ])
                    display(box);
#                    html+= "<img src=" + ramaddaHost + icon+"> " + '<a target=ramadda href=' + ramaddaBase +"/entry/show?entryid=" + id +">" + name +"</a><br>";                
    if cnt == 0:
        html = "<b>No entries found</b>";
    display(HTML(html));                


def saveBundle(line, cell=None):
    extra = "";
    filename = "idv.xidv";

    toks = line.split(" ");
    for i in range(len(toks)):
        tok  = toks[i];
        if tok == "-publish":
            extra +=' publish="true" '
        else:
            filename = tok;
    isl = '<isl><save file="' + filename +'"' + extra +'/></isl>';
    result = idvCall(cmd_loadisl, {"isl": isl});
    if result == None:
        print("save failed");
        return;
    if os.path.isfile(filename):
        print ("bundle saved");
        return FileLink(filename)
    print ("bundle not saved");


def publishBundle(line, cell=None):
    extra = " publish=\"true\" ";
    filename = "idv.xidv";
    if line != "" and line is not None:
        filename = line;
    isl = '<isl><save file="' + filename +'"' + extra +'/></isl>';
    result = idvCall(cmd_loadisl, {"isl": isl});
    if result == None:
        print("save failed");
        return;
    if result != "" and result is not None:
        print("Publication successful");
        print("URL: " + result);

    if os.path.isfile(filename):
        print ("bundle saved");
        return FileLink(filename)
    print ("bundle not saved");


def setBBOX(line, cell=None):
    global bbox;
    toks = line.split();
    if len(toks) == 0:
        bbox = None;
        print("BBOX is cleared");
        return;
    bbox = toks;


def setDDN(line, cell=None):
    ddnHome = line;
    print("ddn=" + line);

#
#Define the magics
#
def load_ipython_extension(shell):
    magicType = "line";
    shell.register_magic_function(idvHelp, magicType);
    shell.register_magic_function(runIdv, magicType);
    shell.register_magic_function(makeUI, magicType);
    shell.register_magic_function(loadBundle, magicType);
    shell.register_magic_function(loadBundleMakeImage, magicType);
    shell.register_magic_function(loadCatalog, magicType);
    shell.register_magic_function(makeImage, magicType);
    shell.register_magic_function(makeMovie, magicType);
    shell.register_magic_function(setRamadda, magicType);
    shell.register_magic_function(setCaseStudy, magicType);
    shell.register_magic_function(createCaseStudy, magicType);
    shell.register_magic_function(setBBOX, magicType);
    shell.register_magic_function(saveBundle, magicType);
    shell.register_magic_function(publishBundle, magicType);
    shell.register_magic_function(publishNotebook, magicType);


makeUI("");

