#STM Images Metadata Database

The STM backup folder contains all the measurements produced at the TASC laboratory  of CNR-IOM Trieste since 1998 for a total of 244.7GB and 431,000 files.

All images have a file with the extension .par, which contains the instrument and other metadata in a text form.

Metadata extraction from par text files was handled using a heavily customized version of the `load_dict()` function from the [spym module](https://pypi.org/project/spym/ "spym"), a Python package for processing Scanning Probe Microscopy data. 

For every image was created a python dictionary that contains key value pairs for all metadata and also path, filename, and image hash digest (md5) were added to be able to check for duplicates and retrieve images from storage.
These dictionaries were then added as rows in the table of the database dedicated to STM images metadata.

The STM images metadata database was built using MySQL on the OpenStack infrastructure of CNR-IOM Trieste and connected to 
phpMyAdmin, a web-interface tool written in PHP made for handling and administrating MySQL database. 