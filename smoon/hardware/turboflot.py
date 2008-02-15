import random
import simplejson
import pkg_resources

from turbogears.widgets import JSLink, Widget, register_static_directory

js_dir = pkg_resources.resource_filename("turboflot", "static")
register_static_directory("turboflot", js_dir)

class TurboFlot(Widget):
    """
        A TurboGears Flot Widget.
    """
    template = """
      <div xmlns:py="http://purl.org/kid/ns#" id="turboflot${id}"
           style="width:${width};height:${height};">
        <script>
          $.plot($("#turboflot${id}"), ${data}, ${options});
        </script>
      </div>
    """
    params = ["data", "options", "height", "width"]
    params_doc = {
            "data"    : "An array of data series",
            "options" : "Plot options",
            "height"  : "The height of the graph",
            "width"   : "The width of the graph"
    }
    javascript = [JSLink('turboflot', '../../static/js/excanvas.js'),
                  JSLink("turboflot", "../../static/js/jquery.js"),
                  JSLink("turboflot", "../../static/js/jquery.flot.js")]
    

    def __init__(self, data, options={}, height="300px", width="600px"):
        random.seed()
        self.id = int(random.random() * 1000)
        self.data = simplejson.dumps(data)
        self.options = simplejson.dumps(options)
        self.height = height
        self.width = width

