# ipython-IDV

Extension for IPython Notebooks to provide line and cell magics to call out to Unidata's [Integrated Data Viewer](https://github.com/Unidata/IDV) 

Part of the [DRILSDOWN project](https://github.com/Unidata/drilsdown)

Copy to drilsdown.py extension to your local extensions directory -
~/ipython/extensions

In the notebook do:
%load_ext drilsdown
%idvHelp

This requires that you have an [IDV version 5.3u1](http://www.unidata.ucar.edu/software/idv/nightly/) or above and set IDV_HOME environment variable to the IDV install directory. The python will run:
${IDV_HOME}/runIDV


The drilsdownplugin.jar is a RAMADDA plugin that provides Drisldown Case Study functionality. 
It is produced from the [RAMADDA drilsdown repository](https://github.com/Unidata/drilsdown) but
is included here so all of the products that are required for running drilsdown can be found in 
one place.

The ramaddaplugin.jar is an IDV plugin that provides publication services to RAMADDA. Likewise, it
is included here so all of the products that are required for running drilsdown can be found in 
one place.
