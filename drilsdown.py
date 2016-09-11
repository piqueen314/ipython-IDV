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
import urllib.request;
import urllib.parse;
from base64 import b64encode;
from IPython.display import HTML;
from IPython.display import Image;
from tempfile import NamedTemporaryFile;
from IPython.display import FileLink;
import time;

idvDebug = 0;

#How we talk to the running IDV
#The port is defined by the idv.monitorport = 8080 in the .unidata/idv/DefaultIdv/idv.properties
idvBaseUrl = "http://localhost:8765";

#These correspond to the commands in ucar.unidata.idv.IdvMonitor
cmd_ping = "/ping";
cmd_loadisl = "/loadisl";


ramaddaBase = None;
ramaddaEntry = None;

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
    for x in range(0, 30):
        if idvPing() != None:
            print("IDV started");
            break;
        if x % 5 == 0:
            print ("Waiting on the IDV");
        time.sleep(1);

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
            url += "?" + urllib.parse.urlencode(args);
        if idvDebug:
            print("Calling " + url);
        html  = urllib.request.urlopen(url).read();
        return html;
    except:
        return None;

#This function checks if the IDV is running
def idvPing():
#NOTE: Don't call idvCall here because idvCall calls runIdv which calls ping
    try:
        return  urllib.request.urlopen(idvBaseUrl +cmd_ping).read();
    except:
        return None;


##
## Here are the magic commands
##

def idvHelp(line, cell=None):
    print("runIdv");
    print("loadBundle <bundle url or file path>");
    print("           If no bundle given and if setRamadda has been called the bundle will be fetched from RAMADDA");
    print("loadBundleMakeImage <bundle url or file path>");
    print("makeImage");
    print("makeMovie");
    print("setRamadda <ramadda url to a Drilsdown case study>");
    print("setBBOX <north west south east> No arguments to clear the bbox");
    print("idvSave <xidv or zidv filename> - write out the bundle");



def loadBundleMakeImage(line, cell=None):
    loadBundle(line,cell);
    return makeImage(line,cell);

def loadBundle(line, cell=None):
    global bbox;
    global ramaddaBase;
    global ramaddaEntryId;
    if line == None or line == "":
        if ramaddaHost is not None:
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
    with NamedTemporaryFile(suffix='.png') as f:
        isl = '<isl><image combine="true" file="' + f.name +'"><matte space="5"/></image></isl>';
        if idvCall(cmd_loadisl, {"isl": isl}) == None:
            print("makeImage failed");
            return;
        return Image(filename=f.name);


def makeMovie(line, cell=None):
    data ="";
    with NamedTemporaryFile(suffix='.gif') as f:
        isl = '<isl><movie file="' + f.name +'"/></isl>';
        if idvCall(cmd_loadisl, {"isl": isl}) == None:
            print("makeMovie failed");
            return;
        data = open(f.name, "rb").read()
        data = b64encode(data).decode('ascii');
        img = '<img src="data:image/gif;base64,{0}">';
        return HTML(img.format(data));

##The arg should be the normal /entry/view URL for a RAMADDA entry
def setRamadda(line, cell=None):
    global ramaddaBase;
    global ramaddaEntryId;
    toks = urllib.parse.urlparse(line);
    ramaddaBase = toks.scheme +"://" + toks.netloc;
    path = re.sub("/entry.*","", toks.path);
    ramaddaBase += path;
    args = urllib.parse.parse_qs(toks.query);
    ramaddaEntryId = args["entryid"][0];
    print("Current ramadda:" + ramaddaBase  + " entry:" + ramaddaEntryId);


def idvSave(line, cell=None):
    filename = "idv.xidv";
    if line != "" and line is not None:
        filename = line;
    isl = '<isl><save file="' + filename +'"/></isl>';
    if idvCall(cmd_loadisl, {"isl": isl}) == None:
        print("save failed");
        return;
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
    shell.register_magic_function(loadBundle, magicType);
    shell.register_magic_function(loadBundleMakeImage, magicType);
    shell.register_magic_function(makeImage, magicType);
    shell.register_magic_function(makeMovie, magicType);
    shell.register_magic_function(setRamadda, magicType);
    shell.register_magic_function(setBBOX, magicType);
    shell.register_magic_function(idvSave, magicType);





