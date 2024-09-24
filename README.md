# MosamaticWeb3.0
New and simplified version of Mosamatic Web

# Filesets and files
A file is a single DICOM file. A fileset is a collection of DICOM files, either corresponding to a single scan or a set of individual files each belonging to a single subject. Files are loaded from a single directory. Since these are all DICOM files Mosamatic Web 3.0 will parse the DICOM header of each file to determine which files belong together. Instance UID will be used for this purpose. The following HTML pages are dedicated to filesets and files:

- filesets.html - Shows a list of filesets
- fileset.html - Shows fileset details and a list of files
- file.html - Shows file details

# Fileset and file filters
Filesets can correspond to different DICOM entities, e.g., one or more CT scans, or one or more Dixon MRI scans. By activating a fileset filter you can search for specific types of DICOM scans. Mosamatic Web 3.0 supports the following fileset filters:

- CT
- T1 MRI
- T2 MRI
- Dixon MRI water
- Dixon MRI fat

