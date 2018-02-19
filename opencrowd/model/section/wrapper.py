import jinja2
from . import section

from opencrowd.config.opencrowd import TEMPLATES_DIR


class Wrapper(section.Section):
    def __init__(self, identity, hidden=False, index=0, sections=[]):
        super(Wrapper, self).__init__(index)
        self.identity = identity
        self.sections = sections
        self.hidden = hidden

    def add_section(self, section):
        self.sections.append(section)

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def get_type(self):
        return "wrapper"

    def get_id(self):
        return str(self.identity)

    def to_json(self):
        return {'type': self.get_type(),
                'identity': self.identity,
                'id': self.get_id(),
                'hidden': self.hidden
                }

    def render(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + self.get_type())
        template = env.get_template('Wrapper.html')
        return template.render(Wrapper=self)

    def add_option(self, option):
        self.options.append(option)

    def get_display_function(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + self.get_type())
        template = env.get_template('load.js')
        return template.render()
