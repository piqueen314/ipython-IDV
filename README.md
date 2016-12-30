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

