from turbogears.widgets import Widget, mochikit, Resource, JSLink
from turbogears import startup

class RatingLink(JSLink):
    def __init__(self, *args, **kw):
        super(RatingLink, self).__init__(None, *args, **kw)

    def update_params(self, d):
        super(RatingLink, self).update_params(d)
        d["link"] = "/%sstatic/%s" % (startup.webpath,
                                      self.name)
        

class RatingWidget(Widget):
    """
    this widget has no call back.
    """
    name = "RatingWidget"
    javascript=[mochikit, RatingLink(name = "rating.js") ]
    template = """
        <script type="text/javascript"><![CDATA[
connect(window, "onload", new Function("env", "rating_init('${href}', ${num}, '${update}', '${img_on}', '${img_off}','${img_over}')"));
//]]>
        </script>
    """
    params = ["update", "href", "num",
              "img_on",
              "img_off",
              "img_over",
              ]
    params_doc = {
        "update":"div class name to be replaced",
        "href":"remote method href",
        "num" : "number of rating levels",
        "img_on" : "url of the image in 'on' state",
        "img_off" : "url of the image in 'off' state",
        "img_over" : "url of the image in 'over' state",
        }

from turbogears.widgets import Widget, mochikit

class SingleRatingWidget(RatingWidget):
    """
    this widget has no call back.
    """
    name = "SingleRatingWidget"
    template = """
        <script type="text/javascript"><![CDATA[
connect(window, "onload", new Function("env", "single_rating_init('${href}', ${num}, '${update}', '${imgon_pre}', '${imgoff_pre}', '${imgbusy_pre}', '${img_post}')"));
//]]>
        </script>
    """

    params = ["update", "href", "num",
              "imgon_pre",
              "imgoff_pre",
              "imgbusy_pre"
              "img_post",
              ]
    params_doc = {
        "update":"div class name to be replaced",
        "href":"remote method href",
        "num" : "number of rating levels",
        "imgon_pre" : "url of the image in the form '%s%d%s' % ($imgon_pre, $i, $img_post)",
        "imgoff_pre" : "url of the image in the form '%s%d%s' % ($imgoff_pre, $i, $img_post)",
        "imgbusy_pre" : "url of the image in the form '%s%d%s' % ($imgbusy_pre, $i, $img_post)",
        "img_post" : "url of the image in the form '%s%d%s' % ($img_pre, $i, $img_post)",
        }
