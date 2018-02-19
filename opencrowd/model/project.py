"""
.. module:: project
   :platform: Unix, Mac
   :synopsis: the project focuses on specific types of tasks

A project is made up of tasks.

Example usage:

.. code-block:: python

   import opencrowd

   oc = Opencrowd.regenerate()
   project = opencrowd.add_project(project=Project(title='Test Project', description='Test Description', crowdsource=CROWDSOURCE_SPECIFICATION))

"""
import logging
import subprocess
import uuid
from .crowd import AmazonMechanicalTurk
from .database import Database
from opencrowd.config.opencrowd import PROJECT_HEADER, TASK_HEADER
from opencrowd.config.redis import DB_HOST, DB_PORT
from opencrowd.model.base.node import OpencrowdNode

project_logger = logging.getLogger('project')


class Project(OpencrowdNode):
    """
    Create and manage a new Project.

    :param title: Title of the project
    :type title: str
    :param description: Description of the project
    :type description: str
    :param crowdsource: see opencrowd/config/opencrowd 
    :type crowdsource: dict
    """
    def __init__(self, title=None, description=None, crowdsource=None):
        try:
            super(Project, self).__init__()
            self.title = title
            self.description = description
            self.crowdsource = crowdsource
            # self.tasks = list()
            self.task_ids = list()
            self.opencrowd_id = str(uuid.uuid4())

        except Exception as e:
            project_logger.error("An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args))
        # try:
        self.git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
        # except Exception as e:
        #     project_logger.info("An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args))
        #     self.git_hash = "An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args)

    def children_ids(self):
        return self.task_ids

    def update(self, database=None):
        """
        Update this server's projects

        :param database: database to use, otherwise defaults to \
        opencrowd/config/database
        :type database: Database
        """
        database = database if database is not None else Database(DB_HOST, DB_PORT)
        for task_id in self.task_ids:
            task = database.get(TASK_HEADER + task_id)
            task.update(self.generate_crowdsource(), database)

    def submit_tasks(self):
        """
        Submit each unsubmitted task contained in this project
        """
        AMT = self.generate_crowdsource()
        # for task in self.tasks:
        #     task.submit(AMT)
        database = Database(DB_HOST, DB_PORT)
        for task_id in self.task_ids:
            task = database.get(TASK_HEADER + task_id)
            task.submit(AMT)

    def add_task(self, task):
        """
        Add a task to this project

        :param task: the task to add
        :type task: Task
        """
        try:
            # self.tasks.append(task)
            self.task_ids.append(task.opencrowd_id)
            task.project_id = self.opencrowd_id
            task.save()
            self.save()
            project_logger.debug("Project {} attached Task {}".format(self.opencrowd_id, task.opencrowd_id))

        except Exception as e:
            project_logger.error("Project unable to attach task. An exception of type {0} occured. Arguments: \n{1!r}".format(type(e).__name__, e.args))

    def generate_crowdsource(self):
        """
        generate the crowdsource based on this project's initialized
        crowdsource specification. Generally propagated via submit task.

        :return: Crowd
        """
        try:
            if self.crowdsource['type'] == 'amt':
                AMT = AmazonMechanicalTurk(
                    self.crowdsource['endpoint'],
                    self.crowdsource['form_submission_action'],
                    self.crowdsource['region_name'],
                    self.crowdsource['aws_access_key_id'],
                    self.crowdsource['aws_secret_access_key']
                )
                return AMT
            else:
                raise ValueError('Crowdsource type not recognized')
        except Exception as e:
            project_logger.error("Unable to generate crowdsource. An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args))

    def save(self):
        database = Database(DB_HOST, DB_PORT)
        database.set(PROJECT_HEADER + self.opencrowd_id, self)
        project_logger.debug("Saving Project {}".format(self.opencrowd_id))

if __name__ == '__main__':
    from opencrowd.config.opencrowd import CROWDSOURCE_SPECIFICATION
    from opencrowd.model.base.task import Task
    from opencrowd.model.base import Question
    from opencrowd.model.section import TextBox, Image, BoundingBox
    text_box = TextBox(main_title='Title', text=['Paragraph 1', 'Paragraph 2'])
    image = Image(urls=['http://lorempixel.com/400/200/nature/'])
    bounding_box = BoundingBox(url="http://lorempixel.com/800/400/nature")

    project = Project(title='Test Project', description='Test Description', crowdsource=CROWDSOURCE_SPECIFICATION)

    # generate 20 questions
    for j in range(3):
        task = Task()
        for i in range(20):
            question = Question()
            question.add_section(bounding_box)
            question.add_section(image)
            question.add_section(text_box)
            task.add_question(question)

        # split into 5 HITs of 4 questions each
        task.create_HITs(4, 3)
        project.add_task(task)

    project.save()
    project_id = project.opencrowd_id
    database = Database(DB_HOST, DB_PORT)
    new_project = database.get(PROJECT_HEADER + project_id)
    new_project.submit_tasks()

    # project.submit_tasks()
