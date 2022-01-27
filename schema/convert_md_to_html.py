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

"""

import os
import sys

path = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) > 1:
    subpath = sys.argv[1]
else:
    subpath = "/"

for root, d_names, f_names in os.walk(path):
    if subpath in root:
        for f_name in f_names:
            filename, ext = os.path.splitext(os.path.basename(f_name))
            if ext == '.md':
                f_input = os.path.join(root, f_name)
                f_output = os.path.join(root, filename + '.html')
                command = f"pandoc {f_input} --webtex='https://latex.codecogs.com/svg.latex?' -o {f_output} --template=template.html --self-contained --metadata title=\"dummy\""
                print('execute command:')
                print(command)
                os.system(command)
