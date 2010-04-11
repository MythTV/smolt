# -*- coding: utf-8 -*-
# Copyright (C) 2008 Luke Macken <lewk at csh rit edu>
# Licensed under MIT
# http://pypi.python.org/pypi/TurboFlot
#
# With modifications for Smolt.
#
import random ; random.seed()
import simplejson

from turbogears.widgets import CSSLink, JSLink, Widget
from turbogears.widgets import register_static_directory

import inspect
import os
js_dir = os.path.join(os.path.dirname(inspect.currentframe().f_code.co_filename), 'static', 'js')
register_static_directory("turboflot", js_dir)

class TurboFlot(Widget):
    """
        A TurboGears Flot Widget.
    """
    template = """
      <div xmlns:py="http://purl.org/kid/ns#">
        <div style="width:${width};height:${height};" id="${id}" />
        <script>
          $(document).ready(function() {
            $.plot($("#${id}"), ${data}, ${options});
          });
        </script>
      </div>
    """
    params = ["data", "options", "height", "width", "id", "label"]
    params_doc = {
            "data"    : "An array of data series",
            "options" : "Plot options",
            "height"  : "The height of the graph",
            "width"   : "The width of the graph",
            "label"   : "Label for the graph",
            "id"      : "An optional ID for the graph"
    }
    css = [CSSLink('turboflot', 'turboflot.css')]
    javascript = [JSLink('turboflot', 'excanvas.js'),
                  JSLink("turboflot", "jquery.js"),
                  JSLink("turboflot", "jquery.flot.js")]

    def __init__(self, data, options={}, height="300px", width="600px",
                 id=None, label=''):
        super(TurboFlot, self).__init__()
        if id:
            self.id = id
        else:
            self.id = "turboflot" + str(int(random.random() * 1000))
        self.data = simplejson.dumps(data)
        self.options = simplejson.dumps(options)
        self.height = height
        self.width = width
        self.label = label
