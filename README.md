# ipython-IDV

Extension for IPython Notebooks to provide line and cell magics to call out to Unidata's [Integrated Data Viewer](https://github.com/Unidata/IDV)

Part of the [DRILSDOWN project](https://github.com/Unidata/drilsdown)

Copy to drilsdown.py extension to your local extensions directory -
~/ipython/extensions

In the notebook do:
%load_ext drilsdown
%idvHelp

This requires that you have the IDV_HOME environment variable set to the IDV install dir. The pyhton will run:
${IDV_HOME}/runIDV

