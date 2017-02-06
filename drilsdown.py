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

##Use Brian's ramadda as the default
ramaddaHost = "http://weather.rsmas.miami.edu";
ramaddaBase = ramaddaHost +"/repository";
ramaddaEntryId = "45e3b50b-dbe2-408b-a6c2-2c009749cd53";

ramaddas  ={"Brian Mapes RAMADDA": 
            "http://weather.rsmas.miami.edu/repository/entry/show?entryid=45e3b50b-dbe2-408b-a6c2-2c009749cd53", 
            "Geode Systems RAMADDA": 
            "http://geodesystems.com/repository/entry/show?entryid=12704a38-9a06-4989-aac4-dafbbe13a675",
            "Unidata's RAMADDA":
            "http://motherlode.ucar.edu/repository/entry/show?entryid=0"};

#How we talk to the running IDV
#The port is defined by the idv.monitorport = 8765 in the .unidata/idv/DefaultIdv/idv.properties
idvBaseUrl = "http://127.0.0.1:8765";

#These correspond to the commands in ucar.unidata.idv.IdvMonitor
cmd_ping = "/ping";
cmd_loadisl = "/loadisl";


#The global bounding box
bbox = None;


displayedItems = [];

##
##Call this to display a component that can later be cleared with the Clear button
##
def doDisplay(comp):
    global displayedItems;
    display(comp);
    displayedItems.append(comp);


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


def makeButton(label, callback, extra=None):
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
    global ramaddaBase;
    if ramaddaBase == None or ramaddaBase == "":
        print("You need to call setRamadda first");
        return;
    type = widget.type;
    value  =  widget.value.replace(" ","%20");
    if type == "":
        url = ramaddaBase +"/search/do?output=default.csv&escapecommas=true&fields=name,id,type,icon,url,size&orderby=name&text=" + value;
    else:
        url = ramaddaBase +"/search/type/" + type +"?output=default.csv&escapecommas=true&orderby=name&fields=name,id,type,icon,url,size&text=" + value;    
    csv = readUrl(url);
    listCsv("<b>Search Results:</b> " + widget.value +" <br>", csv);



def makeUI(line):
    global ramaddaEntryId;
    global ramaddas;
    textLayout=Layout(width='150px');
    ramaddaSelector = widgets.Dropdown(
        options=ramaddas,
        value="http://weather.rsmas.miami.edu/repository/entry/show?entryid=45e3b50b-dbe2-408b-a6c2-2c009749cd53",
        );

    search = widgets.Text(
        layout=textLayout,
    value='',
    placeholder='IDV bundle',
    description='',
    disabled=False)
    search.on_submit(handleSearch);
    search.type = "type_idv_bundle";

    cssearch = widgets.Text(
    value='',
        layout=textLayout,
    placeholder='Case study',
    description='',
    disabled=False)
    cssearch.on_submit(handleSearch);
    cssearch.type = "type_drilsdown_casestudy";


    gridsearch = widgets.Text(
    value='',
        layout=textLayout,
    placeholder='Gridded data',
    description='',
    disabled=False)
    gridsearch.on_submit(handleSearch);
    gridsearch.type = "cdm_grid";

    allsearch = widgets.Text(
    value='',
        layout=textLayout,
    placeholder='All',
    description='',
    disabled=False)
    allsearch.on_submit(handleSearch);
    allsearch.type = "";


    listBtn = makeButton("List",listRamaddaClicked);
    listBtn.entryid = "";
    
    cbx = widgets.Checkbox(
        value=False,
        description='Publish',
        disabled=False);

    lonRange = widgets.FloatRangeSlider(
        value=[-180, 180],
        min=-180,
        max=180.0,
        step=1.0,
        description='Lon:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='i',
        slider_color='white',
        color='black'
        )


    latRange = widgets.FloatRangeSlider(
        value=[-90, 90],
        min=-90,
        max=90.0,
        step=1.0,
        description='Lat:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='i',
        slider_color='white',
        color='black'
        )


    ramaddaSelector.observe(ramaddaSelectorChanged,names='value');
    display(VBox([
                     HBox([
                        makeButton("Run IDV",runIDVClicked),
                      makeButton("Make Image",makeImageClicked, cbx),
                      makeButton("Make Movie",makeMovieClicked,cbx),
                      makeButton("Save Bundle",saveBundleClicked,cbx),
                      cbx]),
                HBox([
                      ramaddaSelector,
                      listBtn,
                      makeButton("Clear",clearClicked),
                      makeButton("Help",idvHelp)]),
##                HBox([lonRange, latRange]),
                HBox([Label("Search for:"), search,
                      cssearch, gridsearch, allsearch]),
                
]));


##
##The button callbacks
##

def reloadClicked(b):
    ipython = get_ipython();
    ipython.magic("reload_ext drilsdown");

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
    extra = "";
    if b.extra.value:
        extra = "-publish"
    makeMovie(extra);

def loadBundleClicked(b):
    loadBundle(b.url);

def viewUrlClicked(b):
    doDisplay(HTML("<a target=ramadda href=" + b.url +">" + b.name+"</a>"));
    display(IFrame(src=b.url,width=800, height=400));


def loadDataClicked(b):
    global ramaddaBase;
    url = ramaddaBase +"/opendap/" + b.entryid +"/entry.das";
    loadData(url, None, b.name);

def listRamaddaClicked(b):
    global ramaddaEntryId;
    if b.entryid == "":
        listRamadda(ramaddaEntryId);
    else:
        listRamadda(b.entryid);


def loadCatalogClicked(b):
    loadCatalog(b.url);

def ramaddaSelectorChanged(s):
    setRamadda(s['new']);



def clearClicked(b):
    clear_output();
    global displayedItems;
    for i in range(len(displayedItems)):
        displayedItems[i].close();


displayedItems = [];


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
    "makeImage <-publish> Capture an IDV image and optionally publish it to RAMADDA<br>" +\
    "makeMovie <-publish> Capture an IDV movie and optionally publish it to RAMADDA<br>" +\
    "saveBundle <xidv or zidv filename> <-publish> - write out the bundle and optionally publish to RAMADDA<br>" +\
    "publishBundle  <xidv or zidv filename> - write out the bundle and publish it to RAMADDA<br>" +\
    "publishNotebook <notebook file name> - publish the current notebook to RAMADDA via the IDV<br>" +\
    "setRamadda <ramadda url to a Drilsdown case study (or setCaseStudy)><br>" +\
    "createCaseStudy <case study name><br>" +\
    "setBBOX <north west south east> No arguments to clear the bbox<br></pre>";
    doDisplay(HTML(html));




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


def loadData(line, cell=None, name = None):
    extra1 = "";
    extra2 = "";
    if name  is not None:
        extra1 += ' name="' + name +'" ';
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
        doDisplay(HTML(img.format(data)));



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
        doDisplay(HTML(img.format(data)));

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
def makeEntryHref(entryId, name, icon = None, alt = ""):
    global ramaddaBase;
    global ramaddaHost;
    html = '<a target=ramadda title="' + alt +'" href="' + ramaddaBase  +'/entry/show?entryid=' + entryId  + '">' + name +'</a>';
    if icon is not None:
        html = "<img src=" + ramaddaHost + icon+"> " + html;
    return html;

#
#List the entries held by the entry id
#
def listRamadda(entryId):
    global ramaddaBase;
    global ramaddaHost;
    toks =  readUrl(ramaddaBase+"/entry/show?output=entry.csv&escapecommas=true&fields=name,icon&entryid=" + entryId).split("\n")[1].split(",");
    baseName =  toks[0];
    baseName  = baseName.replace("_comma_",",");
    icon =  toks[1];
    csv = readUrl(ramaddaBase+"/entry/show?entryid=" + entryId +"&output=default.csv&escapecommas=true&fields=name,id,type,icon,url,size&orderby=name");
    listCsv("<b>" + "<img src=" + ramaddaHost + icon+"> " + "<a target=ramadda href=" +ramaddaBase +"/entry/show?entryid=" + entryId +">" + baseName+"</a></b><br>", csv);


#
#Display the csv listing of entries from RAMADDA
#
def listCsv(label, csv):
    lines =  csv.split("\n");
    cnt = 0;
    indent = HTML("&nbsp;&nbsp;&nbsp;");
    rows=[HTML(label)];
    for i in range(len(lines)):
        if cnt > 100:
            break;
        if i > 0:
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
                fullName = name;
                maxLength  = 25;
                if len(name)>maxLength:
                    name = name[:maxLength-len(name)];

                name = name.ljust(maxLength," ");
                name = name.replace(" ","&nbsp;");
                href = makeEntryHref(id,  name, icon, fullName);
                href  = "<span style=font-family:monospace;>" + href +"</span>";
                href = HTML(href);
                row = [indent, href];
                if type == "type_idv_bundle" or url.find("xidv") >=0 or url.find("zidv")>=0:
                    b  = makeButton("Load bundle",loadBundleClicked);
                    b.url  = ramaddaBase +"/entry/get?entryid=" + id;
                    row.append(b);
                    link = ramaddaBase +"/entry/show/?output=idv.islform&entryid=" + id;
                    row.append(HTML('<a target=ramadda href="' + link +'">Subset Bundle</a>'));
                elif type == "cdm_grid" or fullName.endswith(".nc") :
                    b  = makeButton("Load data",loadDataClicked);
                    b.name =fullName;
                    b.entryid  = id;
                    row.append(b);
                elif type=="type_drilsdown_casestudy" or type=="group" or type=="localfiles":
                    b  = makeButton("List",listRamaddaClicked);
                    b.entryid = id;
                    loadCatalog  = makeButton("Load Catalog",loadCatalogClicked);
                    loadCatalog.url = ramaddaBase +"/entry/show?output=thredds.catalog&entryid=" + id;
                    row.append(b);
                    row.append(loadCatalog);
                else:
                    b  = makeButton("View",viewUrlClicked);
                    b.url = ramaddaBase + "/entry/show?entryid=" + id;
                    b.name = name;
                    row.append(b);
                    
                try:
                    fileSize = line2[5];
                    if float(fileSize)>0:
                        link = ramaddaBase +"/entry/get?entryid=" + id;
                        row.append(HTML('&nbsp;&nbsp;<a target=ramadda href="' + link+'">Download (' + fileSize +' bytes) </a>'));
                except:
                    print("bad line:" + line2[5]);
                rows.append(HBox(row));

    doDisplay(VBox(rows));
    if cnt == 0:
        doDisplay(HTML("<b>No entries found</b>"));



def saveBundle(line, cell=None):
    extra = "";
    filename = "idv.xidv";
    toks = line.split(" ");
    for i in range(len(toks)):
        tok  = toks[i];
        if tok!="":
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
        print ("bundle saved:" + filename);
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
        print ("bundle saved:" + filename);
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
    print("BBOX is set");



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

