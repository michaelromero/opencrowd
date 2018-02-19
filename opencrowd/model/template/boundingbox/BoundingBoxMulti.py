import json
import logging

from classes.question import Question
from classes.sections import BoundingBox
from classes.task import Task

bounding_box_multi_logger = logging.getLogger('bb_multi_template')


class BoundingBoxTemplate(object):
    def __init__(self, urls=None, assignments_per_HIT=None, questions_per_HIT=None):
        self.urls = urls
        self.questions = []
        self.HITs = []
        self.task = None
        self.assignments_per_HIT = assignments_per_HIT
        self.questions_per_HIT = questions_per_HIT

    def generate_questions(self):
        for url in self.urls:
            question = Question()
            bounding_box = BoundingBox()
            bounding_box.set_url(url)
            question.add_section(bounding_box)
            self.questions.append(question)
            # bounding_box1 = BoundingBox()
            # bounding_box1.set_url("https://lorempixel.com/800/400/nature")

    def generate_task(self):
        task = Task()
        for question in self.questions:
            task.add_question(question)
        self.task = task

    def create_HITs(self, questions_per_HIT=None, assignments_per_HIT=None):
        if questions_per_HIT is None:
            questions_per_HIT = self.questions_per_HIT
        if assignments_per_HIT is None:
            assignments_per_HIT = self.assignments_per_HIT

        self.generate_questions()
        self.generate_task()
        try:
            self.task.create_HITs(questions_per_HIT, assignments_per_HIT)

        except Exception as e:
            bounding_box_multi_logger.error("An exception of type {0} occurred. Arguments: {1!r}".format(type(e).__name__, e.args))

    def add_file(self, file_name):
        with open(file_name) as f:
            self.urls = json.load(f)

    def set_assignments_per_HIT(self, assignments_per_HIT):
        self.assignments_per_HIT = assignments_per_HIT

    def set_questions_per_HIT(self, questions_per_HIT):
        self.questions_per_HIT = questions_per_HIT

if __name__ == '__main__':
    from classes.project import Project
    from opencrowd.config.opencrowd import CROWDSOURCE_SPECIFICATION

    template = BoundingBoxTemplate()
    template.add_file('BoundingBoxMulti.json')

    template.set_assignments_per_HIT(3)
    template.set_questions_per_HIT(3)

    template.create_HITs()

    project = Project('Testing Project',
                      'Description of the Test Project',
                      CROWDSOURCE_SPECIFICATION)

    project.add_task(template.task)

    for task_id in project.tasks:
        project.submit_task(task_id)
        exit(1)
