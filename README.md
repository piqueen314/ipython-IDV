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



