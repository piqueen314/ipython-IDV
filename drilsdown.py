# drillsdown.py

#
# Copy this into
# ~/.ipython/extensions/
# In the ipython shell to see the available commands do:
#%load_ext drisldown
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


#The global bounding box
bbox = None;
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
    "setRamadda <ramadda url to a Drilsdown case study><br>" +\
    "createCaseStudy <case study name><br>" +\
    "setBBOX <north west south east> No arguments to clear the bbox<br></pre>";
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
    global theRamadda;
    url = theRamadda.makeUrl("/entry/form?parentof=" + theRamadda.entryId +"&type=type_drilsdown_casestudy&name=" + line);
    url = url.replace(" ","%20");
    print ("Go to this link to create the Case Study:");
    print (url);
    print("Then call %setRamadda with the new Case Study URL");


def loadData(line, cell=None, name = None):
    Idv.loadData(line,name);
    

def loadBundle(line, cell=None):
    global bbox;
    global theRamadda;
    if line == None or line == "":
        if theRamadda is not None:
            line = theRamadda.makeUrl("/drilsdown/getbundle?entryid=" + theRamadda.entryId);

    if line == None or line == "":
        print ("No bundle argument provided");
        return;

    Idv.loadBundle(line, bbox);


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
            publish = true;
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
    Ramadda.setRamadda(line, shouldList);



def listRamadda(entryId):
    """List the entries held by the entry id"""
    global theRamadda;
    toks =  readUrl(theRamadda.makeUrl("/entry/show?output=entry.csv&escapecommas=true&fields=name,icon&entryid=" + entryId)).split("\n")[1].split(",");
    baseName =  toks[0];
    baseName  = baseName.replace("_comma_",",");
    icon =  toks[1];
    entries = theRamadda.doList(entryId);
    theRamadda.displayEntries("<b>" + "<img src=" + theRamadda.host + icon+"> " + "<a target=ramadda href=" +theRamadda.base +"/entry/show?entryid=" + entryId +">" + baseName+"</a></b><br>", entries);


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
    global bbox;
    toks = line.split();
    if len(toks) == 0:
        bbox = None;
        print("BBOX is cleared");
        return;
    bbox = toks;
    print("BBOX is set");



def load_ipython_extension(shell):
    """Define the magics"""
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
    shell.register_magic_function(createCaseStudy, magicType);
    shell.register_magic_function(setBBOX, magicType);
    shell.register_magic_function(saveBundle, magicType);
    shell.register_magic_function(publishBundle, magicType);
    shell.register_magic_function(publishNotebook, magicType);




def makeUI(line):
    DrilsdownUI.makeUI();


class DrilsdownUI:
    """Handles all of the UI callbacks """
    def makeUI():
        global ramaddas;
        nameMap = {};
        first = None;
        for i in range(len(ramaddas)):
            ramadda = ramaddas[i];
            if i == 0:
                first = ramadda.url;
            nameMap[ramadda.name] =  ramadda.url;

        textLayout=Layout(width='150px');
        ramaddaSelector = widgets.Dropdown(
            options=nameMap,
            ##        value=first,
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
            placeholder='Case study',
            description='',
            disabled=False)
        cssearch.on_submit(DrilsdownUI.handleSearch);
        cssearch.type = "type_drilsdown_casestudy";


        gridsearch = widgets.Text(
            value='',
            layout=textLayout,
            placeholder='Gridded data',
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

        listBtn = DrilsdownUI.makeButton("List",DrilsdownUI.listRamaddaClicked);
        listBtn.entryid = "";
    
        cbx = widgets.Checkbox(
            value=False,
            description='Publish',
            disabled=False);

        ramaddaSelector.observe(DrilsdownUI.ramaddaSelectorChanged,names='value');
        display(VBox([
                    HBox([
                            DrilsdownUI.makeButton("Run IDV",DrilsdownUI.runIDVClicked),
                            DrilsdownUI.makeButton("Make Image",DrilsdownUI.makeImageClicked, cbx),
                            DrilsdownUI.makeButton("Make Movie",DrilsdownUI.makeMovieClicked,cbx),
                            DrilsdownUI.makeButton("Save Bundle",DrilsdownUI.saveBundleClicked,cbx),
                            cbx]),
                    HBox([
                            ramaddaSelector,
                            listBtn,
                            DrilsdownUI.makeButton("Clear",DrilsdownUI.clearClicked),
                            DrilsdownUI.makeButton("Help",idvHelp)]),
                    HBox([Label("Search for:"), search,
                          cssearch, gridsearch, allsearch]),
                
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
        global theRamadda;
        type = widget.type;
        value  =  widget.value.replace(" ","%20");
        entries = theRamadda.doSearch(value, type);
        theRamadda.displayEntries("<b>Search Results:</b> " + widget.value +" <br>", entries);

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
        loadData(b.entry.makeOpendapUrl(), None, b.name);


    def setDataClicked(b):
        url  = b.entry.makeOpendapUrl();
        Idv.dataUrl = url;
        print('To access the data use the variable: Idv.dataUrl or:\n' + url);

    def setUrlClicked(b):
        url  = b.entry.makeGetFileUrl();
        Idv.fileUrl = url;
        print('To access the URL use the variable: Idv.fileUrl or:\n' + url);

    def listRamaddaClicked(b):
        global theRamadda;
        if b.entryid == "":
            listRamadda(theRamadda.entryId);
        else:
            listRamadda(b.entryid);


    def loadCatalogClicked(b):
        loadCatalog(b.url);

    def ramaddaSelectorChanged(s):
        Ramadda.setRamadda(s['new']);


    def clearClicked(b):
        clear_output();
        global displayedItems;
        for i in range(len(displayedItems)):
            displayedItems[i].close();




class Idv:
    dataUrl = "";
    fileUrl = "";

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
        if result  == None:
            print("publish failed");
            return;
        if result != "" and result is not None:
            print("Publication successful");
            print("URL: " + result);
            return
        print("Publication failed");


    def loadCatalog(url = None):
        global theRamadda;
        if url is not None or url  != "":
            url = theRamadda.makeUrl("/entry/show?parentof=" + theRamadda.entryId +"&amp;output=thredds.catalog");
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
        if os.path.isfile(filename):
            print ("bundle saved:" + filename);
            return FileLink(filename)
        print ("bundle not saved");


    def loadBundle(bundleUrl, bbox=None):
        extra1 = "";
        extra2 = "";
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
        if Idv.idvCall(Idv.cmd_loadisl, {"isl": isl}) == None:
            print("loadBundle failed");
            return;
##        print("bundle loaded");


    def publishBundle(filename):
        extra = " publish=\"true\" ";
        isl = '<isl><save file="' + filename +'"' + extra +'/></isl>';
        result = Idv.idvCall(Idv.cmd_loadisl, {"isl": isl});
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



    def makeMovie(publish):
        extra = "";
        data ="";
        if publish:
            extra += ' publish="true" ';
        with NamedTemporaryFile(suffix='.gif') as f:
            isl = '<isl><movie file="' + f.name + '"' + extra +'/></isl>';
            result  = Idv.idvCall(Idv.cmd_loadisl, {"isl": isl});
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



    def makeImage(publish=False, caption=None):
        extra = "";
        extra2 = "";
        if publish:
            extra = " publish=\"true\" ";
        if caption is not None:
            extra2 +=    '<matte bottom="50" background="white"/>';
            label = caption;
            label = label.replace("-"," ");
            extra2 +=    '<overlay text="' + label +'"  place="LM,0,-10" anchor="LM"  color="black" fontsize="16"/>';
            extra2 +=    '<matte space="1"  background="black"/>';
        with NamedTemporaryFile(suffix='.png') as f:
            isl = '<isl><image combine="true" file="' + f.name +'"' + extra +'>' + extra2  +'</image></isl>';
            result = Idv.idvCall(Idv.cmd_loadisl, {"isl": isl});
            if result == None:
                print("makeImage failed");
                return;
            if publish:
                print("Publication successful");
                print("URL: " + result);
            data = open(f.name, "rb").read()
            data = b64encode(data).decode('ascii');
            img = '<img src="data:image/gif;base64,{0}">';
            doDisplay(HTML(img.format(data)));


class Ramadda:
    def __init__(self, url):
        self.url = url;
        toks = urlparse(url);
        self.host = toks.scheme +"://" + toks.netloc;
        self.base = toks.scheme +"://" + toks.netloc;
        path = re.sub("/entry.*","", toks.path);
        self.base += path;
        self.entryId = re.search("entryid=([^&]+)", toks.query).group(1);
        toks =  readUrl(self.makeUrl("/entry/show?output=entry.csv&escapecommas=true&fields=name,icon&entryid=" + self.entryId)).split("\n")[1].split(",");
        self.name =   toks[0].replace("_comma_",",");
        self.icon =  toks[1];

    def setRamadda(url, shouldList=True):
        """Set the ramadda to be used. The arg should be the normal /entry/view URL for a RAMADDA entry"""
        global theRamadda;
        theRamadda = Ramadda(url);
        if shouldList:
            listRamadda(theRamadda.entryId);


    def getName(self):
        return self.name;

    def getBase(self):
        return self.base;

    def doList(self, entryId):
        """make a list of RamaddaEntry objects that are children of the given entryId"""
        csv = readUrl(self.makeUrl("/entry/show?entryid=" + entryId +"&output=default.csv&escapecommas=true&fields=name,id,type,icon,url,size&orderby=name"));
        return self.makeEntries(csv);

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


    def makeEntryHref(self, entryId, name, icon = None, alt = ""):
        """make a href for the given entry"""
        html = '<a target=ramadda title="' + alt +'" href="' + self.base  +'/entry/show?entryid=' + entryId  + '">' + name +'</a>';
        if icon is not None:
            html = "<img src=" + self.host + icon+"> " + html;
        return html;

    
    def displayEntries(self, label, entries):
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
            type = entry.getType();
            icon = entry.getIcon();
            url = entry.getUrl();
            fullName = name;
            maxLength  = 25;
            if len(name)>maxLength:
                name = name[:maxLength-len(name)];
            name = name.ljust(maxLength," ");
            name = name.replace(" ","&nbsp;");
            href = self.makeEntryHref(entry.getId(),  name, entry.getIcon(), fullName);
            href  = "<span style=font-family:monospace;>" + href +"</span>";
            href = HTML(href);
            row = [indent, href];
            id = entry.getId();
            type = entry.getType();
            if entry.isBundle():
                b  = DrilsdownUI.makeButton("Load bundle",DrilsdownUI.loadBundleClicked);
                b.entry = entry;
                b.url  = self.makeUrl("/entry/get?entryid=" + id)
                row.append(b);
                b  = DrilsdownUI.makeButton("Set URL",DrilsdownUI.setUrlClicked);
                b.entry = entry;
                row.append(b);
                link = self.makeUrl("/entry/show/?output=idv.islform&entryid=" + id);
                row.append(HTML('<a target=ramadda href="' + link +'">Subset Bundle</a>'));
            elif entry.isGrid():
                b  = DrilsdownUI.makeButton("Load data",DrilsdownUI.loadDataClicked);
                b.name =fullName;
                b.entry  = entry;
                row.append(b);
                b  = DrilsdownUI.makeButton("Set data",DrilsdownUI.setDataClicked);
                b.entry  = entry;
                row.append(b);
            elif entry.isGroup():
                b  = DrilsdownUI.makeButton("List",DrilsdownUI.listRamaddaClicked);
                b.entryid = id;
                loadCatalog  = DrilsdownUI.makeButton("Load Catalog",DrilsdownUI.loadCatalogClicked);
                loadCatalog.url = self.makeUrl("/entry/show?output=thredds.catalog&entryid=" + id);
                row.append(b);
                row.append(loadCatalog);
            else:
                b  = DrilsdownUI.makeButton("View",DrilsdownUI.viewUrlClicked);
                b.url = self.makeUrl("/entry/show?entryid=" + id);
                b.name = name;
                row.append(b);

                fileSize = entry.getFileSize();
                if fileSize>0:
                    link = self.makeUrl("/entry/get?entryid=" + id);
                    row.append(HTML('&nbsp;&nbsp;<a target=ramadda href="' + link+'">Download (' + repr(fileSize) +' bytes) </a>'));
            rows.append(HBox(row));

        doDisplay(VBox(rows));
        if cnt == 0:
            doDisplay(HTML("<b>No entries found</b>"));


class RamaddaEntry:
    def __init__(self, ramadda, name, id, type, icon, url, fileSize):
        self.ramadda = ramadda;
        self.name =  name.replace("_comma_",",");
        self.id = id;
        self.type = type;
        self.icon = icon;
        self.url = url;
        self.fileSize = fileSize;

    def getName(self):
        return self.name;

    def getId(self):
        return self.id;

    def getType(self):
        return self.type;

    def getIcon(self):
        return self.icon;

    def getUrl(self):
        return self.url;

    def getFileSize(self):
        return self.fileSize;

    def isBundle(self):
        return self.getType() == "type_idv_bundle" or self.getUrl().find("xidv") >=0 or self.getUrl().find("zidv")>=0;

    def isGrid(self):
        return self.getType() == "cdm_grid" or self.getName().endswith(".nc");

    def isGroup(self):
        return self.getType()=="type_drilsdown_casestudy" or self.getType()=="group" or self.getType()=="localfiles";

    def makeOpendapUrl(self):
        return  self.ramadda.base +"/opendap/" + self.id +"/entry.das";

    def makeGetFileUrl(self):
        return  self.ramadda.base +"/entry/get?entryid=" + self.id;


##Make the RAMADDAS
ramaddas  =[Ramadda("http://weather.rsmas.miami.edu/repository/entry/show?entryid=45e3b50b-dbe2-408b-a6c2-2c009749cd53"),
           Ramadda("http://geodesystems.com/repository/entry/show?entryid=12704a38-9a06-4989-aac4-dafbbe13a675")
##            Ramadda("http://motherlode.ucar.edu/repository/entry/show?entryid=0")
];
theRamadda = ramaddas[0];


makeUI("");

        

