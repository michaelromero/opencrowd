import jinja2
from . import section
import uuid
import logging

from opencrowd.model.base.node import OpencrowdNode
# from opencrowd.model.database import Database
from opencrowd.config.opencrowd import TEMPLATES_DIR, QUESTION_HEADER
# from opencrowd.config.redis import DB_HOST, DB_PORT

question_logger = logging.getLogger('question')


class QuestionAsInstruction(OpencrowdNode):
    def __init__(self):
        super(QuestionAsInstruction, self).__init__()
        self.sections = []
        self.opencrowd_id = str(uuid.uuid4())
        self.option_ids = []

    def add_section(self, section, parents=None):
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

        # check for unique option ids
        # if section.to_json()['type'] == 'InputGroup':
        #     for option_id in section.option_ids:
        #         if option_id not in self.option_ids:
        #             self.option_ids.append(option_id)
        self.sections.append(section)
        question_logger.debug("Question {} appended Section {}".format(self.opencrowd_id, section.opencrowd_id))
        section.save()
        self.save()

    # def render(self):
    #     env = Environment(trim_blocks=True, lstrip_blocks=True)
    #     env.loader = FileSystemLoader(TEMPLATES_DIR + 'base')
    #     template = env.get_template('Question.html')
    #     return template.render(Question=self)

    def save(self):
        question_logger.debug("Saving Question {}".format(self.opencrowd_id))
        database = Database(DB_HOST, DB_PORT)
        database.set(QUESTION_HEADER + self.opencrowd_id, self)

    # @staticmethod
    # def get(question_id):
    #     database = Database(DB_HOST, DB_PORT)
    #     return database.get(QUESTION_HEADER + question_id)
    #
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


class Instruction(section.Section):
    def __init__(self, hidden=False, opencrowd_id=None):
        super(Instruction, self).__init__(opencrowd_id=opencrowd_id, hidden=hidden)
        self.sections = []

    def add_section(self, section):
        self.sections.append(section)

    def to_json(self):
        json_obj = {'type': 'Instruction'}
        json_obj.update(super(Instruction, self).to_json())
        return json_obj

    def render(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "Instruction")
        template = env.get_template('Instruction.html')
        return template.render(Instruction=self)

    def dynamicGenerateGraphLogic(self):
        pass

    def staticGenerateGraphLogic(self):
        pass

    def call_save_function(self):
        pass

    def generate_save_function(self):
        pass

if __name__ == '__main__':
    from .image import Image
    from .text_box import TextBox
    from opencrowd.model.base.question import Question
    from opencrowd.model.base.task import Task
    from opencrowd.model.base.HIT import HIT_HEADER
    from opencrowd.model.database import Database
    from opencrowd.config.redis import DB_PORT, DB_HOST
    task = Task()
    # create an instruction
    instruction = QuestionAsInstruction()
    image = Image(urls=['http://lorempixel.com/400/200/nature/'])
    instruction.add_section(image)
    print(image.opencrowd_id)
    # create a question
    question = Question()
    textbox_a = TextBox(main_title='Title_a', text=['Paragraph 1a', 'Paragraph 2a'])
    question.add_section(textbox_a, parents='root')

    # add to task
    task.add_question(question)
    task.add_instruction(instruction)

    # create HITs
    task.create_HITs(1, 1)

    # render HITs
    database = Database(DB_HOST, DB_PORT)
    for idx, HIT_id in enumerate(task.HIT_ids):
        HIT = database.get(HIT_HEADER + HIT_id)
        HIT = HIT.render('pass')

    with open('instruction_render.html', 'w+') as f:
        f.write(HIT)
