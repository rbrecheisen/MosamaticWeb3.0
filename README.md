# MosamaticWeb3.0
New and simplified version of Mosamatic Web

# Filesets and files
A file is a single DICOM file. A fileset is a collection of DICOM files, either corresponding to a single scan or a set of individual files each belonging to a single subject. Files are loaded from a single directory. Since these are all DICOM files Mosamatic Web 3.0 will parse the DICOM header of each file to determine which files belong together. Instance UID will be used for this purpose. The following HTML pages are dedicated to filesets and files:

- filesets.html - Shows a list of filesets
- fileset.html - Shows fileset details and a list of files
- file.html - Shows file details

# Creating new tasks
To create a new task do the following:

- Create new task in app\tasks, e.g., "dosomethingtask.py". The implementation should be a function ""dosomethingtask" decorated with "@task()" so Huey can find it.
- Create new task view in app\views\tasks, e.g., "dosomething.py". Look in "dummy.py" for the template and make sure the task is called with the correct HTML parameters.
- Create new task HTLM page in app\templates\tasks, e.g., "dosomething.html". Look in "dummy.html" for the template and make sure the right form fields are present for submitting the task parameters.

Rerun Huey to have it pick up the new task.

# Running Mosamatic Web 3.0 on linux/arm64 architectures
