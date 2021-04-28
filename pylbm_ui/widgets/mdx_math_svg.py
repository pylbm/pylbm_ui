r"""
mdx_math_svg

Python-Markdown extension to render equations as embedded SVG.
No MathJax, no images. Real vector drawings.

The Markdown syntax recognized is:
```
$Equation$, \(Equation\)

$$
  Display Equations
$$

\[
  Display Equations
\]

\begin{align}
  Display Equations
\end{align}
```


Copyright 2021 by Cris Luengo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.


Based on:

- Extension logic, recognizing Markdown syntax:
  Arithmatex from PyMdown Extensions <https://github.com/facelessuser/pymdown-extensions>
  Copyright 2014 - 2017 Isaac Muse <isaacmuse@gmail.com>
  MIT license.

- Converting LaTeX into SVG:
  latex2svg.py
  Copyright 2017, Tino Wagner
  MIT license.

- Tweaking the output of latex2svg for embedding into HTML5, and use of cache:
  latex2svgextra.py from m.css <https://github.com/mosra/m.css>
  Copyright 2017, 2018, 2019, 2020 Vladimír Vondruš <mosra@centrum.cz>
  MIT license.
"""

# Import statements for the Markdown extension component
from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import attr_list
from markdown import util as md_util
# import xml.etree.ElementTree as ET
import lxml.etree as ET

# Other import statements
import os
import sys
import subprocess
import shlex
import re
import copy
import html
import pickle
from tempfile import TemporaryDirectory
from ctypes.util import find_library
from hashlib import sha1


# -------------------------------------------------------
# Code below adapted from latex2svg and latex2svgextra
# -------------------------------------------------------

# --- The Cache ---

# Increase this value if generated SVG changes somehow. Stored caches will be discarded.
_cache_version = 1

def _empty_cache():
    return {
        'version': _cache_version,
        'age': 0,
        'data': {}
    }

# Cache for rendered equations (source formula sha1 -> svg).
# _cache[1] is a counter (the "age") used to track which latex equations were used this time around.
# Unused equations can be pruned from the cache.
# The cache version should be bumped if the format of the cache is changed, cache files
# with a different version number can be discarded.
_cache = _empty_cache()

def load_cache(file):
    """Loads cached SVG data. Use at the start of a session to avoid
    repeating renderings done in the previous session.
    """
    global _cache
    try:
        with open(file, 'rb') as f:
            _cache = pickle.load(f)
            if not _cache or not isinstance(_cache, dict) or \
                    'version' not in _cache or _cache['version'] != _cache_version:
                # Reset the cache if not valid or not expected version
                # TODO: If font size changes, we also need to flush the cache (but the params are no longer global...)
                _cache = _empty_cache()
            else:
                # Otherwise bump cache age
                _cache['age'] += 1
    except FileNotFoundError:
        _cache = _empty_cache()

def save_cache(file):
    """Saves cached SVG data. Use at the end of a session so they
    can be recovered in your next session.
    """
    global _cache
    # Don't save any file if there is nothing
    if not _cache['data']:
        return

    # Prune entries that were not used
    cache_to_save = _cache.copy()
    cache_to_save['data'] = {}
    for hash, entry in _cache['data'].items():
        if entry[0] != _cache['age']:
            continue
        cache_to_save['data'][hash] = entry

    with open(file, 'wb') as f:
        pickle.dump(cache_to_save, f)


# --- Various regular expressions to parse and modify the SVG ---

# dvisvgm 1.9.2 (on Ubuntu 16.04) doesn't specify the encoding part. However
# that version reports broken "depth", meaning inline equations are not
# vertically aligned properly, so it can't be made to work 100% correct anyway.
_patch_src = re.compile(r"""<\?xml version='1\.0'( encoding='UTF-8')?\?>
<!-- This file was generated by dvisvgm \d+\.\d+\.\d+ -->
<svg height='(?P<height>[^']+)pt' version='1.1' viewBox='(?P<viewBox>[^']+)' width='(?P<width>[^']+)pt' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'>
""")

# dvisvgm 2.6 has a different order of attributes. According to the changelog,
# the SVGs can be now hashed, which hopefully means that the output won't
# change every second day again. Hopefully.
_patch26_src = re.compile(r"""<\?xml version='1\.0' encoding='UTF-8'\?>
<!-- This file was generated by dvisvgm \d+\.\d+ -->
<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='(?P<width>[^']+)pt' height='(?P<height>[^']+)pt' viewBox='(?P<viewBox>[^']+)'>
""")

# version ignored by all UAs, safe to drop https://stackoverflow.com/a/18468348
_patch_dst = r"""<svg{attribs} style="width: {width:.3f}em; height: {height:.3f}em;{style}" viewBox="{viewBox}">
<title>
{formula}
</title>
"""

_unique_src = re.compile(r"""(?P<name> id|xlink:href)='(?P<ref>#?)(?P<id>g\d+-\d+|page\d+)'""")
_unique_dst = r"""\g<name>='\g<ref>eq{counter}-\g<id>'"""

_remove_svg_header = re.compile(r"""<\?xml version='1\.0'( encoding='UTF-8')?\?>
<!-- This file was generated by dvisvgm \d+\.\d+\.\d+ -->
""")

_remove_svg_namespace = re.compile(r"xmlns='http://www.w3.org/2000/svg'")


# The code and data related to latex2svg collected in a class
class LaTeX2SVG:
    "The class that does all the good stuff"

    def __init__(self):
        self.params = {
            'fontsize': 1,  # em (in the sense used by CSS)
            'template': r"""
        \documentclass[12pt,preview]{standalone}
        {{ preamble }}
        \begin{document}
        \begin{preview}
        {{ code }}
        \end{preview}
        \end{document}
        """,
            'preamble': r"""
        \usepackage[utf8x]{inputenc}
        \usepackage{amsmath}
        \usepackage{amsfonts}
        \usepackage{amssymb}
        \usepackage{newtxtext}
        \usepackage{newtxmath}
        """,
            'latex_cmd': 'latex -interaction nonstopmode -halt-on-error',
            'dvisvgm_cmd': 'dvisvgm --no-fonts --exact',
            'libgs': None,
        }

        if not self.params['libgs'] and not hasattr(os.environ, 'LIBGS'):
            p = find_library('gs')
            if p:
                self.params['libgs'] = p
            elif sys.platform == 'darwin':
                # Fallback to homebrew Ghostscript on macOS
                homebrew_libgs = '/usr/local/opt/ghostscript/lib/libgs.dylib'
                if os.path.exists(homebrew_libgs):
                    self.params['libgs'] = homebrew_libgs
            if not self.params['libgs']:
                print('Warning: libgs not found, mdx_math_svg will not be able to properly align inline equations.')

        # dvisvgm 2.2.2 was changed to "avoid scientific notation of floating point numbers"
        # (https://github.com/mgieseki/dvisvgm/blob/3facb925bfe3ab47bf40d376d567a114b2bee3a5/NEWS#L90),
        # meaning the default precision (6) is now used for the decimal points, so you'll often get
        # numbers like 194.283203, which is way too much precision. Here we detect the version
        # of dvisvgm, and for >= 2.2.2 we set the precision to 2, which seems to be just fine.
        try:
            ret = subprocess.run(['dvisvgm','--version'], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, encoding='utf-8')
            if ret.returncode:
                print(ret.stderr)
            ret.check_returncode()
            version = re.match(r'dvisvgm (\d*)\.(\d*)\.(\d*)', ret.stdout)
            if version:
                version = (int(version.group(1)), int(version.group(2)), int(version.group(3)))
                #print('Found dvisvgm version:', version)
                if version >= (2, 2, 2):
                    #print('dvisvgm is 2.2.2 or newer, adjusting precision')
                    self.params['dvisvgm_cmd'] = self.params['dvisvgm_cmd'] + ' --precision=2'
        except FileNotFoundError:
            print('Warning: dvisvgm not found, mdx_math_svg will not work.')
            pass

        # Counter to ensure unique IDs for multiple SVG elements on the same page.
        # Reset back to zero on start of a new page for reproducible behavior.
        # Or leave as is if you don't care.
        self.counter = 0


    def _latex2svg(self, latex, working_directory):
        document = (self.params['template']
                    .replace('{{ preamble }}', self.params['preamble'])
                    .replace('{{ code }}', latex))

        with open(os.path.join(working_directory, 'code.tex'), 'w') as f:
            f.write(document)

        # Run LaTeX and create DVI file
        try:
            ret = subprocess.run(shlex.split(self.params['latex_cmd'] + ' code.tex'),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 cwd=working_directory, encoding='cp437')
            if ret.returncode:
                # LaTeX prints errors on stdout instead of stderr (stderr is empty),
                # so print stdout instead
                print(ret.stdout)
                print('\n\n\nAttempting to compile the following:\n\n\n')
                print(document)
            ret.check_returncode()
        except FileNotFoundError:
            raise RuntimeError('latex not found')

        # Add LIBGS to environment if supplied
        env = os.environ.copy()
        if self.params['libgs']:
            env['LIBGS'] = self.params['libgs']

        # Convert DVI to SVG
        try:
            ret = subprocess.run(shlex.split(self.params['dvisvgm_cmd'] + ' code.dvi'),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 cwd=working_directory, env=env, encoding='utf-8')
            if ret.returncode:
                print(ret.stderr)
            ret.check_returncode()
        except FileNotFoundError:
            raise RuntimeError('dvisvgm not found')

        with open(os.path.join(working_directory, 'code.svg'), 'r') as f:
            svg = f.read()

        # Parse dvisvgm output for alignment
        def get_measure(output, name):
            regex = r'\b{}=([0-9.e-]+)pt'.format(name)
            match = re.search(regex, output)
            if match:
                return float(match.group(1))
            else:
                return None

        depth = get_measure(ret.stderr, 'depth')  # This is in pt

        return svg, depth


    def latex2svg(self, latex):
        """Convert LaTeX to SVG using dvisvgm.

        Uses settings in the dict mdx_math_svg.params.

        Uses a cache. mdx_math_svg.load_cache(file) will load cached data
        from file, and mdx_math_svg.save_cache(file) will save the current
        cache to disk. Use these commands at the start and end of your
        session.

        Parameters
        ----------
        latex : str
            LaTeX code to render.

        Returns
        -------
        svg : str
           SVG data.
        """
        # Find latex code in cache
        global _cache
        hash = sha1(latex.encode('utf-8')).digest()
        if hash in _cache['data']:
            svg = _cache['data'][hash][1]
            #print('Found the following LaTeX in the cache:', latex)
        else:
            # It's not in the cache: compute SVG
            with TemporaryDirectory() as tmpdir:
                #print('Rendering the following LaTeX:', latex)
                svg, depth = self._latex2svg(latex, tmpdir)

            # Patch SVG
            pt2em = self.params['fontsize'] / 10  # Unfortunately, 12pt(==1em) font is not 1em.
            if depth is not None and latex.startswith(r'\('):  # Inline
                style = ' vertical-align: -{:.3f}em;'.format(depth * pt2em)
            else:
                style = ''

            root = ET.fromstring(svg.encode())

            root.attrib['style'] = style
            root.attrib['width'] = f"{float(root.attrib['width'].replace('pt', '')) * pt2em}em"
            root.attrib['height'] = f"{float(root.attrib['height'].replace('pt', '')) * pt2em}em"

            title = ET.Element('title')
            title.text = html.escape(latex)
            root.append(title)

            svg = ET.tostring(root).decode()

        # Put svg in cache, note that if it was already there, we're just updating the counter
        _cache['data'][hash] = (_cache['age'], svg)

        # Make element IDs unique
        self.counter += 1
        svg = _unique_src.sub(_unique_dst.format(counter=self.counter), svg)

        return svg


    def load_cache(self, file):
        """Loads cached SVG data. Use at the start of a session to avoid
        repeating renderings done in the previous session. The cache is
        shared among all instances of this plugin.
        """
        load_cache(file)


    def save_cache(self, file):
        """Saves cached SVG data. Use at the end of a session so they
        can be recovered in your next session. The cache is shared
        among all instances of this plugin.
        """
        save_cache(file)


# -------------------------------------------------------
# Code below adapted from Arithmatex
# -------------------------------------------------------

def _escape_chars(md, echrs):
    """
    Add chars to the escape list.
    Don't just append as it modifies the global list permanently.
    Make a copy and extend **that** copy so that only this Markdown
    instance gets modified.
    """
    escaped = copy.copy(md.ESCAPED_CHARS)
    for ec in echrs:
        if ec not in escaped:
            escaped.append(ec)
    md.ESCAPED_CHARS = escaped


class InlineMathSvgPattern(InlineProcessor):
    """MathSvg inline pattern handler."""

    ESCAPED_BSLASH = '%s%s%s' % (md_util.STX, ord('\\'), md_util.ETX)

    def __init__(self, pattern, config, latex2svg, md):
        """Initialize."""

        self.inline_class = config.get('inline_class', '')
        self.latex2svg = latex2svg

        InlineProcessor.__init__(self, pattern, md)

    def handleMatch(self, m, data):
        """Handle inline content."""

        # Handle escapes
        escapes = m.group(1)
        if not escapes:
            escapes = m.group(4)
        if escapes:
            return escapes.replace('\\\\', self.ESCAPED_BSLASH), m.start(0), m.end(0)

        # Handle LaTeX
        latex = m.group(3)
        if not latex:
            latex = m.group(6)
        latex = r'\(' + latex + r'\)'
        svg = self.latex2svg.latex2svg(latex)

        import xml.etree.ElementTree as ET

        el = ET.Element('span', {'class': self.inline_class})
        el.text = self.md.htmlStash.store(svg)

        return el, m.start(0), m.end(0)


class BlockMathSvgProcessor(BlockProcessor):
    """MathSvg block pattern handler."""

    def __init__(self, pattern, config, latex2svg, md):
        """Initialize."""

        self.display_class = config.get('display_class', '')
        self.latex2svg = latex2svg
        self.md = md
        self.checked_for_deps = False
        self.use_attr_list = False  # will be set in run(), we'll know all extensions have been initialized by then

        self.match = None
        self.pattern = re.compile(pattern)

        BlockProcessor.__init__(self, md.parser)

    def test(self, parent, block):
        """Return 'True' for future Python Markdown block compatibility."""

        self.match = self.pattern.match(block) if self.pattern is not None else None
        return self.match is not None

    def run(self, parent, blocks):
        """Find and handle block content."""

        # Check for dependent extensions
        if not self.checked_for_deps:
            for ext in self.md.registeredExtensions:
                if isinstance(ext, attr_list.AttrListExtension):
                    self.use_attr_list = True
                    break
            self.checked_for_deps = True

        blocks.pop(0)

        escaped = False
        latex, attrib = self.match.group('math'), self.match.group('attrib')
        if not latex:
            latex, attrib = self.match.group('math3'), self.match.group('attrib3')
        if not latex:
            latex, attrib = self.match.group('math2'), self.match.group('attrib2')
            escaped = True  # math2 includes the '\begin{env}' and '\end{env}'
        if not escaped:
            latex = r'\[' + latex + r'\]'
        svg = self.latex2svg.latex2svg(latex)
        attrib_dict = {'class': self.display_class}
        if attrib and self.use_attr_list:
            #print("\nFound attrib:", attrib)
            for k, v in attr_list.get_attrs(attrib):
                if k == '.':
                    attrib_dict['class'] += ' ' + v
                elif k == 'class':  # we need to preserve our "display class"!
                    attrib_dict['class'] = self.display_class + ' ' + v
                else:
                    attrib_dict[k] = v
            #print(attrib_dict)
            attrib = ''

        el = ET.SubElement(parent, 'div', attrib_dict)
        el.text = self.md.htmlStash.store(svg)
        if attrib:
            el.tail = attrib

        return True


RE_SMART_DOLLAR_INLINE = r'(?:(?<!\\)((?:\\{2})+)(?=\$)|(?<!\\)(\$)(?!\s)((?:\\.|[^\\$])+?)(?<!\s)(?:\$))'
RE_DOLLAR_INLINE = r'(?:(?<!\\)((?:\\{2})+)(?=\$)|(?<!\\)(\$)((?:\\.|[^\\$])+?)(?:\$))'
RE_BRACKET_INLINE = r'(?:(?<!\\)((?:\\{2})+?)(?=\\\()|(?<!\\)(\\\()((?:\\[^)]|[^\\])+?)(?:\\\)))'

RE_DOLLAR_BLOCK = r'(?P<dollar>[$]{2})(?P<math>((?:\\.|[^\\])+?))(?P=dollar)(?:\{(?P<attrib>.*)\})?'
RE_TEX_BLOCK = r'(?P<math2>\\begin\{(?P<env>[a-z]+\*?)\}(?:\\.|[^\\])+?\\end\{(?P=env)\})(?:\{(?P<attrib2>.*)\})?'
RE_BRACKET_BLOCK = r'\\\[(?P<math3>(?:\\[^\]]|[^\\])+?)\\\](?:\{(?P<attrib3>.*)\})?'


class MathSvgExtension(Extension):
    """Adds MathSvg extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            'inline_class': [
                'math',
                "Inline math is SVG wrapped in a <span> tag, this option adds a class name to it - Default: 'math'"
            ],
            'display_class': [
                'math',
                "Display math is SVG wrapped in a <div> tag, this option adds a class name to it - Default: 'math'"
            ],
            "smart_dollar": [True, "Use mdx_math_svg's smart dollars - Default True"],
            "block_syntax": [
                ['dollar', 'square', 'begin'],
                'Enable block syntax: "dollar" ($$...$$), "square" (\\[...\\]), and '
                '"begin" (\\begin{env}...\\end{env}) - Default: ["dollar", "square", "begin"]'
            ],
            "inline_syntax": [
                ['dollar', 'round'],
                'Enable block syntax: "dollar" ($$...$$), "round" (\\(...\\))'
                ' - Default: ["dollar", "round"]'
            ],
            "fontsize": [1, "Font size in em for rendering LaTeX equations - Default 1"],
            "additional_preamble": [
                [],
                'Additional LaTeX statements to add to the preamble - Default: []'
            ]
        }

        self.latex2svg = LaTeX2SVG()

        super(MathSvgExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        """Extend the inline and block processor objects."""

        md.registerExtension(self)
        _escape_chars(md, ['$'])

        config = self.getConfigs()

        # Configure latex2svg
        self.latex2svg.params['fontsize'] = config.get('fontsize', 1)
        additional_preamble = config.get('additional_preamble', [])
        if additional_preamble:
            if not isinstance(additional_preamble, str):
                additional_preamble = '\n'.join(additional_preamble)
            self.latex2svg.params['preamble'] = self.latex2svg.params['preamble'] + '\n' + additional_preamble

        # Inline patterns
        allowed_inline = set(config.get('inline_syntax', ['dollar', 'round']))
        smart_dollar = config.get('smart_dollar', True)
        inline_patterns = []
        if 'dollar' in allowed_inline:
            inline_patterns.append(RE_SMART_DOLLAR_INLINE if smart_dollar else RE_DOLLAR_INLINE)
        if 'round' in allowed_inline:
            inline_patterns.append(RE_BRACKET_INLINE)
        if inline_patterns:
            inline = InlineMathSvgPattern('(?:%s)' % '|'.join(inline_patterns), config, self.latex2svg, md)
            md.inlinePatterns.register(inline, 'mathsvg-inline', 189.9)

        # Block patterns
        allowed_block = set(config.get('block_syntax', ['dollar', 'square', 'begin']))
        block_pattern = []
        if 'dollar' in allowed_block:
            block_pattern.append(RE_DOLLAR_BLOCK)
        if 'square' in allowed_block:
            block_pattern.append(RE_BRACKET_BLOCK)
        if 'begin' in allowed_block:
            block_pattern.append(RE_TEX_BLOCK)
        if block_pattern:
            block = BlockMathSvgProcessor(r'(?s)^(?:%s)[ ]*$' % '|'.join(block_pattern), config, self.latex2svg, md)
            md.parser.blockprocessors.register(block, "mathsvg-block", 79.9)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return MathSvgExtension(*args, **kwargs)
