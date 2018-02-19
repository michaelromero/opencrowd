import jinja2
from . import section
from opencrowd.config.opencrowd import TEMPLATES_DIR


class TextBox(section.Section):
    """
    Create and manage a new TextBox section. A TextBox section is used for prompting or educating workers, and generally
    precedes other sections.

    This Section was created with code from Chris Pratt
    https://cpratt.co/
    https://cpratt.co/twitter-bootstrap-callout-css-styles/

    :param callout_type: affects the color of the textbox. default: grey primary: blue success: green info: light blue warning: yellow danger: red
    :type callout_type: str

    """

    def __init__(self, main_title=None, text=None, callout_type='default', opencrowd_id=None, hidden=False ):
        super(TextBox, self).__init__(opencrowd_id, hidden)
        self.main_title = main_title
        if text is None:
            text = []
        self.text = text
        self.callout_type = callout_type
        self.type = self.__class__.__name__

    def to_json(self):
        json_obj = {'main_title': self.main_title,
                    'text': self.text,
                    'type': self.type,
                    'callout_type': self.callout_type}
        json_obj.update(super(TextBox, self).to_json())
        # super(TextBox, self).to_json().update(
        #     {'main_title': self.main_title,
        #      'text': self.text,
        #      'type': self.__class__.__name__,
        #      'callout_type': self.callout_type}
        # )
        return json_obj
        # return super(TextBox, self).to_json()

    def get_load_function(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "TextBox")
        template = env.get_template('load.js')
        return template.render()

    def render(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "TextBox")
        template = env.get_template('TextBox.html')
        return template.render(TextBox=self)

    def dynamicGenerateGraphLogic(self):
        return "if (node.type == \"TextBox\") {\n\
        var html_template = generate_textbox(node, root_id);\n\
        $(\"#\"+anchor_id).after(html_template);\n\
    }"

    def staticGenerateGraphLogic(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "TextBox")
        template = env.get_template('graph.js')
        return template.render()

if __name__ == '__main__':
    text_box = TextBox(main_title='Title', text=['Paragraph 1', 'Paragraph 2'])
    print(text_box.render())


