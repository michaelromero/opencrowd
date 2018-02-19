"""
.. module:: question
   :platform: Unix, Mac
   :synopsis: the question, made of sections, is converted into an html template

A question is made up of sections. When sections are added to a question, the question will
begin to generate a directed graph structure. The question needs to be stored in a Task object, which
generates HIT objects from the question pool. The question will pass the graph structure to the HIT,
which passes it to the HTML that is passed to the crowdsource.

Example usage:

.. code-block:: python

   import opencrowd

   question = Question()

   # sections previously created, ex: images = Image(urls=[img[0], img[1]])
   # make sure you specify a parent
   question.add_section(images, parent='root')

   # attach to a task


.. moduleauthor:: Michael Romero <michaelrom@zillowgroup.com>


"""

import uuid
import logging
from opencrowd.model.database import Database
from opencrowd.config.opencrowd import TEMPLATES_DIR, QUESTION_HEADER
from opencrowd.config.redis import DB_HOST, DB_PORT
from opencrowd.model.base.node import OpencrowdNode

question_logger = logging.getLogger('question')


class Question(OpencrowdNode):
    """
    Create and manage a new Question.
    """
    def __init__(self):
        super(Question, self).__init__()
        self.sections = []
        self.opencrowd_id = str(uuid.uuid4())

    def add_section(self, section, parents=None):
        """
        Add a section to the question. If Parent is 'prev', the Question
        will automatically add the previous section as the parent of the
        newly added section, creating a linear DAG. Else, if parents is a
        list, the new section will be rendered after each parent.

        :param section: Section to add, see note below
        :type section: Section
        :param parents: parents of this section
        :type parents: [Section]

        .. attention::
            the section parameter can only take the following:
                * 'root': specifies this as the head of the graph structure
                * 'prev': use the previous section as the parent
                * [Sections] or Section: use the section(s) as parents

        """
        if parents == 'prev':
            if len(self.sections):
                self.sections[-1].children.append(section.opencrowd_id)
                self.sections[-1].save()
                section.parents.append(self.sections[-1].opencrowd_id)
        elif parents == 'root':
            section.parents = 'root'
        elif parents is not None:
            if isinstance(parents, list):
                for parent_section in parents:
                    section.parents.append(parent_section.opencrowd_id)
                    parent_section.children.append(section.opencrowd_id)
                    parent_section.save()
                    print(parent_section.children)
            elif not isinstance(parents, list):
                section.parents.append(parents.opencrowd_id)
                parents.children.append(section.opencrowd_id)
                parents.save()

        self.sections.append(section)
        question_logger.debug("Question {} appended Section {}".format(self.opencrowd_id, section.opencrowd_id))
        section.save()
        self.save()

    def save(self):
        question_logger.debug("Saving Question {}".format(self.opencrowd_id))
        database = Database(DB_HOST, DB_PORT)
        database.set(QUESTION_HEADER + self.opencrowd_id, self)

    # # used for pickle
    # def __getstate__(self):
    #     return {'sections': self.sections,
    #             'section_index_counts': self.section_index_counts,
    #             'opencrowd_id': self.opencrowd_id}
    #
    # # used for pickle
    # def __setstate__(self, state):
    #     self.sections = state['sections']
    #     self.section_index_counts = state['section_index_counts']
    #     self.opencrowd_id = state['opencrowd_id']

if __name__ == '__main__':
    import opencrowd.model.section
    text_box = opencrowd.model.section.TextBox(main_title='Title', text=['Paragraph 1', 'Paragraph 2'])
    image = opencrowd.model.section.Image(urls=['http://lorempixel.com/400/200/nature/'])
    question = Question()
    question.add_section(image)
    question.add_section(text_box)
    print(question.render())
