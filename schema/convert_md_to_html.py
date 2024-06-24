# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
"""
convert the md files into html files
need internet connection for svg latex

usage:

convert all md files in all the subdirectories
>>> python convert_md_to_html.py

convert all md files only in the directories that contain the subpath
>>> python convert_md_to_html.py subpath

convert only one md file
>>> python convert_md_to_html.py path/to_the/file.md

"""

import os
import sys


def md2html(f_input, f_output):
    optwebtex = "--webtex='https://latex.codecogs.com/svg.latex?'"
    opt = [
        "--template=template.html",
        "--embed-resources",
        "--standalone",
        "--metadata title=\"dummy\""
    ]
    command = f"pandoc {f_input} "
    command += optwebtex
    command += f" -o {f_output} "
    for optk in opt:
        command += optk + " "
    print('execute command:')
    print(command)
    os.system(command)


path = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) > 1:
    subpath = sys.argv[1]
else:
    subpath = "/"

test_dir = True
if subpath[-3:] == ".md":
    f_input = subpath
    f_output = subpath[:-3] + ".html"
    md2html(f_input, f_output)
    test_dir = False

if test_dir:
    for root, d_names, f_names in os.walk(path):
        if subpath in root:
            for f_name in f_names:
                filename, ext = os.path.splitext(os.path.basename(f_name))
                if ext == '.md':
                    f_input = os.path.join(root, f_name)
                    f_output = os.path.join(root, filename + '.html')
                    md2html(f_input, f_output)
