"""Tornado handlers for the live notebook view."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import os
from tornado import web
HTTPError = web.HTTPError

from ..base.handlers import (
    IPythonHandler, FilesRedirectHandler, path_regex,
)
from ..utils import url_escape


class NotebookHandler(IPythonHandler):

    sections = (
        (
            ("http://ipython.org/documentation.html", "IPython Help", True),
            ("http://nbviewer.ipython.org/github/ipython/ipython/tree/2.x/examples/Index.ipynb", "Notebook Help", True),
        ), (
            ("http://docs.python.org", "Python", True),
            ("http://help.github.com/articles/github-flavored-markdown", "Markdown", True),
            ("http://docs.scipy.org/doc/numpy/reference/", "NumPy", True),
            ("http://docs.scipy.org/doc/scipy/reference/", "SciPy", True),
            ("http://matplotlib.org/contents.html", "Matplotlib", True),
            ("http://docs.sympy.org/latest/index.html", "SymPy", True),
            ("http://pandas.pydata.org/pandas-docs/stable/", "pandas", True)
        )
    )

    @web.authenticated
    def get(self, path):
        """get renders the notebook template if a name is given, or 
        redirects to the '/files/' handler if the name is not given."""
        path = path.strip('/')
        cm = self.contents_manager
        
        # will raise 404 on not found
        try:
            model = cm.get(path, content=False)
        except web.HTTPError as e:
            if e.status_code == 404 and 'files' in path.split('/'):
                # 404, but '/files/' in URL, let FilesRedirect take care of it
                return FilesRedirectHandler.redirect_to_files(self, path)
            else:
                raise
        if model['type'] != 'notebook':
            # not a notebook, redirect to files
            return FilesRedirectHandler.redirect_to_files(self, path)
        name = url_escape(path.rsplit('/', 1)[-1])
        path = url_escape(path)
        self.write(self.render_template('notebook.html',
            notebook_path=path,
            notebook_name=name,
            kill_kernel=False,
            mathjax_url=self.mathjax_url,
            sections=self.sections,
            )
        )


#-----------------------------------------------------------------------------
# URL to handler mappings
#-----------------------------------------------------------------------------


default_handlers = [
    (r"/notebooks%s" % path_regex, NotebookHandler),
]

