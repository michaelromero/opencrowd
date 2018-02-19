import jinja2
from . import section
import uuid

from opencrowd.config.opencrowd import TEMPLATES_DIR


class Image(section.Section):
    """
    Create and manage a new Image section. The Image section will dynamically
    fit images into appropriate columns. For instance, a single image will take
    up the entire section space. Two images will render side by side, 3 and 4
    will render across a single line, and more will be split across multiple
    lines.

    :param urls: a list of strings pointing to the url(s) of the image(s)
    :type title: list
    """

    def __init__(self, urls=None, hidden=False, opencrowd_id=None):
        super(Image, self).__init__(opencrowd_id, hidden)
        if urls is None:
            urls = []
        self.urls = urls
        self.length = len(urls)
        self.type = self.__class__.__name__

    def to_json(self):
        json_obj = {'type': self.type,
                    'urls': self.urls}
        json_obj.update(super(Image, self).to_json())
        return json_obj

    def get_load_function(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "Image")
        template = env.get_template('load.js')
        return template.render()

    def render(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "Image")
        template = env.get_template('Image.html')
        return template.render(Image=self)

    def dynamicGenerateGraphLogic(self):
        return "if (node.type == \"Image\") {\n\
        var html_template = generate_image(node, root_id);\n\
        $(\"#\"+anchor_id).after(html_template);\n\
    }"

    def staticGenerateGraphLogic(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "Image")
        template = env.get_template('graph.js')
        return template.render()

    def add_url(self, url):
        """
        add a url to the Image section

        :param url: a string of the url
        :type title: str
        """

        self.urls.append(url)
        self.length = len(self.urls)

if __name__ == '__main__':
    image = Image()
    image.add_url("http://lorempixel.com/800/400/nature")
    print(image.render())
