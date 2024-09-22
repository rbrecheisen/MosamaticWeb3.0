# MosamaticWeb3.0
New and simplified version of Mosamatic Web

# Datasets, filesets and files
A file is a single DICOM file. A fileset is a collection of DICOM files, either corresponding to a single scan or a set of individual files each belonging to a single subject. Files are loaded from a single directory. Since these are all DICOM files Mosamatic Web 3.0 will parse the DICOM header of each file to determine which files belong together. Instance UID will be used for this purpose. The following HTML pages are dedicated to datasets, filesets and files:

- datasets.html - Shows a list of loaded datasets.
- dataset.html - Shows a list of file sets of a given dataset.
- fileset.html - Shows a list of files of a given fileset.

