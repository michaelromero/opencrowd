import jinja2
from . import section
import uuid

from opencrowd.config.opencrowd import TEMPLATES_DIR


class CollapsePanel(section.Section):
    """
    Create and manage a new CollapsePanel section. The CollapsePanel is a
    bootstrap collapsible panel. It consists of 3 HTML sections, which can
    be standard strings: the title, body, and footer. The body and footer
    appear, via dropdown, when the title is clicked.

    :param title: html string
    :type title: str
    :param body: html string
    :type body: str
    :param footer: html string
    :type footer: str
    """

    def __init__(self, title="", body="", footer="", hidden=False, opencrowd_id=None):
        super(CollapsePanel, self).__init__(opencrowd_id, hidden)
        self.type = self.__class__.__name__
        self.title = title
        self.body = body
        self.footer = footer

    def to_json(self):
        json_obj = {'type': self.type,
                    'title': self.title,
                    'body': self.body,
                    'footer': self.footer}
        json_obj.update(super(CollapsePanel, self).to_json())
        return json_obj

    def get_load_function(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "CollapsePanel")
        template = env.get_template('load.js')
        return template.render()

    def render(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "CollapsePanel")
        template = env.get_template('CollapsePanel.html')
        return template.render(CollapsePanel=self)

    def dynamicGenerateGraphLogic(self):
        return "if (node.type == \"CollapsePanel\") {\n\
        var html_template = generate_CollapsePanel(node, root_id);\n\
        $(\"#\"+anchor_id).after(html_template);\n\
    }"

    def staticGenerateGraphLogic(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "CollapsePanel")
        template = env.get_template('graph.js')
        return template.render()
