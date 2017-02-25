# ipython-IDV

Extension for IPython Notebooks to provide line and cell magics to call out to Unidata's [Integrated Data Viewer](https://github.com/Unidata/IDV) 

Part of the [DRILSDOWN project](https://github.com/Unidata/drilsdown)

To set this up:

After installing the iPython notebook to your machine you will also need to install the [ipywidgets package](https://ipywidgets.readthedocs.io/en/latest/user_install.html)

Once installed copy the [drilsdown.py](https://github.com/Unidata/ipython-IDV/blob/master/drilsdown.py) extension to your local extensions directory -
~/ipython/extensions

When you run the iPython notebook do:

<pre>
%load_ext drilsdown
</pre>

If you are writing code you can also import the Idv and Ramadda classes:

<pre>
from drilsdown import Idv
from drilsdown import Ramadda
</pre>

You should see an initial user interface including a link to the help section.

To run the IDV commands you need to have the latest [IDV version 5.3u1](http://www.unidata.ucar.edu/software/idv/nightly/) or above and set IDV_HOME environment variable to the IDV install directory. The python will run:
${IDV_HOME}/runIDV

You also need to configure your IDV to accept connections from the ipython notebook. To do this set the following property in your local ~/.unidata/idv/DefaultIdv/idv.properties file:

<pre>
idv.monitorport = 8765
</pre>


The [ramaddaplugin.jar](https://github.com/Unidata/ipython-IDV/blob/master/ramaddaplugin.jar) is an IDV plugin that provides publication services to RAMADDA. Copy this file to your local IDV plugins directory (~/.unidata/idv/DefaultIdv/plugins). It is included here so all of the products that are required for running drilsdown can be found in 
one place.

The [drilsdownplugin.jar](https://github.com/Unidata/ipython-IDV/blob/master/drilsdownplugin.jar)  is a RAMADDA plugin that provides Drisldown Case Study functionality. It is produced from the [RAMADDA drilsdown repository](https://github.com/Unidata/drilsdown) but is included here so all of the products that are required for running drilsdown can be found in one place. Copy this plugin to your RAMADDA plugins directory.



<h2>Examples</h2>
Here is an example of how to use the API to load an IDV bundle with different bounding boxes and capture images

<pre>
from drilsdown import Idv
from drilsdown import Ramadda
Ramadda.setRamadda("http://geodesystems.com/repository/entry/show?entryid=12704a38-9a06-4989-aac4-dafbbe13a675")
Idv.fileUrl="http://geodesystems.com/repository/entry/get?entryid=d83e0924-008d-4025-9517-394e9f13712f"
bboxes = [[50,-130,40,-100],[50,-100,40,-75],[40,-130,20,-100],[40,-100,20,-75]]
for i in range(len(bboxes)):
    bbox=bboxes[i];
    Idv.loadBundle(Idv.fileUrl,bbox)
    Idv.makeImage(caption="BBOX:" + repr(bbox[0]) +"/" + repr(bbox[1]) +"  " + repr(bbox[2]) +"/" + repr(bbox[3]))
</pre>


<pre>
from drilsdown import Idv
from drilsdown import Ramadda
Ramadda.setRamadda("http://geodesystems.com/repository/entry/show?entryid=12704a38-9a06-4989-aac4-dafbbe13a675")
Idv.fileUrl="http://geodesystems.com/repository/entry/get?entryid=d83e0924-008d-4025-9517-394e9f13712f"
bboxes = [[50,-130,40,-100],[50,-100,40,-75],[40,-130,20,-100],[40,-100,20,-75]]
for i in range(len(bboxes)):
    bbox=bboxes[i];
    Idv.loadBundle(Idv.fileUrl,bbox);
    label = "BBOX:" + repr(bbox[0]) +"/" + repr(bbox[1]) +"  " + repr(bbox[2]) +"/" + repr(bbox[3]);
    Idv.makeMovie(caption=label,display=True, publish={'parent':'9adf32b5-aad4-4a8d-997e-216b9757d240',"name":"Image #" + repr(i)})
</pre>




The makeImage can take one of 2 forms of a publish argument. The first is a boolean and will result in the IDV popping up its RAMADDA publish dialog box where the image can be published.
<pre>
    Idv.makeImage(caption=label, publish=True);
</pre>

In the second form the publish argument is a map. This directs the python to do the publishing directly to RAMADDA. The map can contain a parent member which is the entry id to publish to and a name member which is the entry name. 

<pre>
    Idv.makeImage(caption=label, publish={'parent':'9adf32b5-aad4-4a8d-997e-216b9757d240',"name":"Image #" + repr(i)})
</pre>

To enable direct publishing to RAMADDA you need to have your RAMADDA user name and password defined as environment variables:

<pre>
export RAMADDA_USER=
export RAMADDA_PASSWORD=
</pre>


