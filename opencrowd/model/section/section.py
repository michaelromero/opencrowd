"""
.. module:: section
   :platform: Unix
   :synopsis: Sections are the smallest building block in opencrowd.

Sections are the smallest building block in opencrowd.
Sections comprise a question.
Questions are stored in a Task.
A task collects the questions into a HIT.
A HIT is displayed and worked on by a worker.
A completed HIT is returned.

* :ref:`Bounding Box<bounding_box>`
* :ref:`Collapse Panel<collapse_panel>`
* :ref:`Image<image>`
* :ref:`Input Group<input_group>`
* :ref:`Text Box<text_box>`


.. moduleauthor:: Michael Romero <michaelrom@zillowgroup.com>


"""

import uuid
from opencrowd.model.database import Database
from opencrowd.config.opencrowd import SECTION_HEADER
from opencrowd.config.redis import DB_HOST, DB_PORT


class Section(object):
    """
    The opencrowd server primarily acts as an API between the developer and the opencrowd library. It also
    performs memory management and operations across all elements (adding/tracking/deleting projects, tasks,
    HITs, questions, sections).

    :param project_ids: the project ids to attach to this instance of the server. For advanced usage only, otherwise leave default and run regenerate()
    :type project_ids: list of str
    """

    def __init__(self, opencrowd_id, hidden):
        self.opencrowd_id = str(uuid.uuid4()) if not opencrowd_id else opencrowd_id
        self.hidden = hidden
        self.parents = []
        self.children = []

    def set_hidden(self, boolean):
        self.hidden = boolean

    def get_opencrowd_id(self):
        return self.opencrowd_id

    def to_json(self):
        """
        This operation is used by the templating engine, jinja, to return values for DAG generation in the javascript.
        These values, which are appended with any specific section values (images have urls, text boxes have strings, etc.)
        are stored in a global javascript variable describing the DAG.
        """

        json_obj = {}
        if self.hidden:
            json_obj['hidden'] = self.hidden
        if len(self.children):
            json_obj['children'] = self.children
        if self.parents:
            json_obj['parents'] = self.parents

        return json_obj

    def save(self):
        database = Database(DB_HOST, DB_PORT)
        database.set(SECTION_HEADER + self.opencrowd_id, self)

    def call_save_function(self):
        """
        Some sections require special javascript code to save themselves in the HTML. New sections would implement this
        abstract method. For example, the bounding box maintains special variables to maintain states.
        """
        return ""

    def generate_save_function(self):
        """
        The generic save function in the opencrowd html template loads section-specific save functions into a
        particular area. This function generates the calling code to such areas. For example, the bounding box section
        will load save_bounding_box() into the generic save() function.
        """
        return ""

