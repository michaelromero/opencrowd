"""
.. module:: task
   :platform: Unix, Mac
   :synopsis: A task compiles a list of questions into HITs.

A project is comprised of Tasks. Each Task compiles a group of questions into HITs,
and tracks the results.

.. moduleauthor:: Michael Romero <michaelrom@zillowgroup.com>
"""

import logging
import random
import uuid
import traceback

from opencrowd.config.opencrowd import TASK_HEADER, HIT_HEADER, QUESTION_HEADER, SECTION_HEADER
from opencrowd.config.redis import DB_HOST, DB_PORT
from opencrowd.model.base.HIT import HIT
from opencrowd.model.database import Database

task_logger = logging.getLogger('task')


class Task(object):
    """
    The task object maintains a pool of questions it uses to generate HITs. It
    can then push these HITs to Amazon Mechanical Turk workers for completion,
    then update itself and pull the Assignments down for review.

    :param project_id: the project id of the project this task is under.\
    handled automatically if project.add_task is used.
    :type project_id: str

    """
    def __init__(self, project_id=None):
        self.question_ids = list()
        self.HIT_ids = list()
        self.opencrowd_id = str(uuid.uuid4())
        self.questions_per_assignment = None
        self.assignments_per_HIT = None
        self.project_id = project_id
        self.instruction_ids = []
        self.option_ids = []

    def add_question(self, question):
        """
        Add a Question to a Task

        :param question: The question object to add
        :type question: Question

        """
        self.question_ids.append(question.opencrowd_id)
        self.save()

    def create_HITs(self, questions_per_assignment, assignments_per_HIT, method='random'):
        """
        Generate [HIT]s  from this task's question pool. Currently only the 'random' method
        is supported.

        :param questions_per_assignment: how many questions to place in each HIT.
        :type questions_per_assignment: int
        :param assignments_per_HIT: # workers to find for this HIT
        :type assignments_per_HIT: int
        :param method: 'random'
        :param type: str

        """
        if not isinstance(questions_per_assignment, int):
            raise TypeError("'questions_per_assignment' not set")

        if not isinstance(assignments_per_HIT, int):
            raise TypeError("'assignments_per_HIT' not set")

        # assert self.project_id is not None

        assignments = []
        if method == 'random':
            random.shuffle(self.question_ids)
            database = Database(DB_HOST, DB_PORT)
            questions = [database.get(QUESTION_HEADER + question_id) for question_id in self.question_ids]
            assignments = [questions[i:i + questions_per_assignment] for i in range(0, len(questions), questions_per_assignment)]

        for idx, assignment in enumerate(assignments):
            task_logger.info('{}/{}'.format(idx+1, len(assignments)))
            try:
                new_hit = HIT(assignments_per_hit=assignments_per_HIT,
                              AutoApprovalDelayInSeconds=604800,
                              lifetime_in_seconds=604800,
                              assignment_duration_in_seconds=1800,
                              Reward='0.01',
                              Title='alpha',
                              Keywords='trulia, alpha, arch',
                              Description='alpha description',
                              task_id=self.opencrowd_id)
                for question in assignment:
                    new_hit.add_question(question)
                    task_logger.debug('HIT {} attached question {}'.format(new_hit.opencrowd_id, question.opencrowd_id))

                # add instructions
                for instruction_id in self.instruction_ids:
                    new_hit.add_instruction_id(instruction_id)
                self.HIT_ids.append(new_hit.opencrowd_id)
                self.save()

            except Exception as e:
                task_logger.error("Unable to generate HIT. An exception of type {} occurred. Arguments:\n{!r}.\nTraceback: {}".format(type(e).__name__, e.args, traceback.format_exc()))

    def update(self, generated_crowdsource, database=None):
        """
        Update this tasks's HITs

        :param generated_crowdsource:  the crowdsource specifications. see opencrowd/config/opencrowd
        :param database: database connection, defaults to redis in opencrowd/config/redis
        """
        database = database if database is not None else Database(DB_HOST, DB_PORT)
        for HIT_id in self.HIT_ids:
            HIT = database.get(HIT_HEADER + HIT_id)
            HIT.update(generated_crowdsource, database)
            self.save()

    def submit(self, AMT):
        """
        submit the HIT through the AMT connection

        :param AMT:

        """
        database = Database(DB_HOST, DB_PORT)
        for idx, HIT_id in enumerate(self.HIT_ids):
            HIT = database.get(HIT_HEADER + HIT_id)
            HIT = HIT.submit(AMT)
            self.HIT_ids[idx] = HIT.HITId
            self.save()

    def save(self):
        task_logger.debug("Saving Task {}".format(self.opencrowd_id))
        database = Database(DB_HOST, DB_PORT)
        database.set(TASK_HEADER + self.opencrowd_id, self)

    @staticmethod
    def get(task_id):
        task_logger.debug("Fetching Task {}".format(task_id))
        database = Database(DB_HOST, DB_PORT)
        return database.get(TASK_HEADER + task_id)


if __name__ == '__main__':
    from .question import Question
    from opencrowd.model.section import TextBox, Image
    from opencrowd.config.opencrowd import CROWDSOURCE_SPECIFICATION
    from opencrowd.model.crowd import AmazonMechanicalTurk

    text_box = TextBox(main_title='Title', text=['Paragraph 1', 'Paragraph 2'])
    image = Image(urls=['http://lorempixel.com/400/200/nature/'])
    task = Task()

    # generate 20 questions

    for i in range(20):
        question = Question()
        question.add_section(image)
        question.add_section(text_box)
        task.add_question(question)

    # split into 5 HITs of 4 questions each
    task.create_HITs(4, 3)

    task_id = task.opencrowd_id
    task.save()
    new_task = Task.get(task_id)

    AMT = AmazonMechanicalTurk(CROWDSOURCE_SPECIFICATION['endpoint'],
                               CROWDSOURCE_SPECIFICATION['form_submission_action'],
                               CROWDSOURCE_SPECIFICATION['region_name'],
                               CROWDSOURCE_SPECIFICATION['aws_access_key_id'],
                               CROWDSOURCE_SPECIFICATION['aws_secret_access_key'])
    new_task.submit(AMT)
