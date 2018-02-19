"""
.. module:: Opencrowd
   :platform: Unix
   :synopsis: Acts as the interface between opencrowd and the user.

The opencrowd server primarily acts as an API between the developer and the opencrowd library. It also
performs memory management and operations across all elements (adding/tracking/deleting projects, tasks,
HITs, questions, sections). Generating


.. moduleauthor:: Michael Romero <michaelrom@zillowgroup.com>


"""
import logging
from opencrowd.model.project import Project
from opencrowd.model.crowd import AmazonMechanicalTurk
from opencrowd.model.database import Database
from opencrowd.config.redis import DB_HOST, DB_PORT
from opencrowd.config.opencrowd import CROWDSOURCE_SPECIFICATION, SERVER_HEADER, PROJECT_HEADER, TASK_HEADER, HIT_HEADER, ASSIGNMENT_HEADER, QUESTION_HEADER
from opencrowd.model.base.node import OpencrowdNode
from opencrowd.model.response.response import Default, AnswersOnly
opencrowd_logger = logging.getLogger('opencrowd')


class Opencrowd(OpencrowdNode):
    """
    :param project_ids: the project ids to attach to this instance of the server. For advanced usage only, otherwise leave default and run regenerate()
    :type project_ids: list of str
    """

    def __init__(self, project_ids=list()):
        super(Opencrowd, self).__init__()
        self.project_ids = project_ids

    def children_ids(self):
        return self.project_ids

    def add_project(self, project):
        """
        Add a project object to opencrowd

        :param project: the project  to attach to this instance of the server. For advanced usage only
        :type project: a Project object
        :returns: the project used in param
        """
        self.project_ids.append(project.opencrowd_id)
        project.save()
        self.save()
        return project

    def create_project(self, title=None, description=None, crowdsource=CROWDSOURCE_SPECIFICATION):
        """
        The best way to generate a project. Creates a new project object and tracks it

        :param title: A title for the project
        :type title: str
        :param description: A description of the project
        :type description: str
        :param crowdsource: The specification for the crowdsource
        :type crowdsource: dict
        :returns: the newly created Project object
        """

        new_project = Project(title, description, crowdsource)
        project = self.add_project(new_project)
        return project

    def update(self):
        """
        Update this server's projects
        """
        database = Database(DB_HOST, DB_PORT)
        for project_id in self.project_ids:
            project = database.get(PROJECT_HEADER + project_id)
            project.update(database=database)

    def submit_tasks(self):
        """
        Will recursively enter projects saved, their tasks, and their tasks' HITs that have not been submitted yet, and
        have each HIT submit itself.
        """
        database = Database(DB_HOST, DB_PORT)
        for project_id in self.project_ids:
            project = database.get(PROJECT_HEADER + project_id)
            project.submit_tasks()

    def list_project_ids(self, project_ids=None):
        """
        List all project ids
        """

        if project_ids is None or type(project_ids) is list or type(project_ids) is str:
            project_ids = self.project_ids if project_ids is None else project_ids
            return project_ids
        else:
            raise TypeError("project_ids must be a single string or list of strings")

    def list_task_ids(self, project_ids=None):
        """
        List all task ids
        """

        database = Database(DB_HOST, DB_PORT)
        task_ids = []
        for project_id in self.list_project_ids(project_ids):
            project = database.get(PROJECT_HEADER + project_id)
            for task_id in project.task_ids:
                task_ids.append(task_id)
        return task_ids
        # return list(flatten([[task.opencrowd_id for task in project.tasks] for project_id, project in self.projects.iteritems()]))

    def list_HIT_ids(self, project_ids=None):
        """
        List all HIT ids
        """

        database = Database(DB_HOST, DB_PORT)
        HIT_ids = []
        for task_id in self.list_task_ids(project_ids):
            task = database.get(TASK_HEADER + task_id)
            for HIT_id in task.HIT_ids:
                HIT_ids.append(HIT_id)
        return HIT_ids

    def list_assignment_ids(self, project_ids=None):
        """
        List all assignment ids
        """

        database = Database(DB_HOST, DB_PORT)
        assignment_ids = []
        for HIT_id in self.list_HIT_ids(project_ids):
            HIT = database.get(HIT_HEADER + HIT_id)
            for assignment_id in HIT.assignment_ids:
                assignment_ids.append(assignment_id)
        return assignment_ids

    def list_question_ids(self, project_ids=None):
        """
        List all question ids
        """

        database = Database(DB_HOST, DB_PORT)
        question_ids = []
        for HIT_id in self.list_HIT_ids(project_ids):
            HIT = database.get(HIT_HEADER + HIT_id)
            for question_id in HIT.question_ids:
                question_ids.append(question_id)
        return question_ids

    def list_section_ids(self, project_ids=None):
        """
        List all section ids
        """

        database = Database(DB_HOST, DB_PORT)
        section_ids = []
        for question_id in self.list_question_ids(project_ids):
            question = database.get(QUESTION_HEADER + question_id)
            for section in question.sections:
                section_ids.append(section.opencrowd_id)
        return section_ids

    def save(self):
        """
        Utilize the Database class to save this object
        """
        database = Database(DB_HOST, DB_PORT)
        database.set(SERVER_HEADER, self)
        opencrowd_logger.debug("Saving opencrowd Server")

    def recursive_delete(self):
        """
        Delete all instances, via ids, tracked on this instance
        """
        project_ids = self.list_project_ids()
        task_ids = self.list_task_ids()
        HIT_ids = self.list_HIT_ids()
        assignment_ids = self.list_assignment_ids()
        question_ids = self.list_question_ids()
        database = Database(DB_HOST, DB_PORT)
        for question_id in question_ids:
            database.delete(QUESTION_HEADER + question_id)
        for assignment_id in assignment_ids:
            database.delete(ASSIGNMENT_HEADER + assignment_id)
        for HIT_id in HIT_ids:
            database.delete(HIT_HEADER + HIT_id)
        for task_id in task_ids:
            database.delete(TASK_HEADER + task_id)
        for project_id in project_ids:
            database.delete(PROJECT_HEADER + project_id)
        self.project_ids = []
        self.save()

    def delete_sandbox(self):
        """
        Delete all HITs on AMT Sandbox
        """

        if len(self.project_ids) > 0:
            opencrowd_logger.info("Deleting all sandbox HITs...")
            AMT = AmazonMechanicalTurk(
                'https://mturk-requester-sandbox.us-east-1.amazonaws.com',
                'https://workersandbox.mturk.com/mturk/externalSubmit',
                'us-east-1',
                CROWDSOURCE_SPECIFICATION['aws_access_key_id'],
                CROWDSOURCE_SPECIFICATION['aws_secret_access_key']
            )
            AMT.delete_sandbox()
            self.recursive_delete()

        else:
            opencrowd_logger.warning("opencrowd server possibly out of sync: no projects found")
            AMT = AmazonMechanicalTurk(
                'https://mturk-requester-sandbox.us-east-1.amazonaws.com',
                'https://workersandbox.mturk.com/mturk/externalSubmit',
                'us-east-1',
                CROWDSOURCE_SPECIFICATION['aws_access_key_id'],
                CROWDSOURCE_SPECIFICATION['aws_secret_access_key']
            )
            AMT.delete_sandbox()
            self.recursive_delete()

    @staticmethod
    def regenerate():
        """
        Restores a default opencrowd instance and the project ids it tracks. After an Opencrowd server instance is
        created, it's generally best to regenerate it unless you specified particular project ids to track.
        """

        database = Database(DB_HOST, DB_PORT)
        if database.database.exists(SERVER_HEADER):
            opencrowd_logger.debug('Loading opencrowd server...')
            regenerated_server = database.get('opencrowd_server')
            return regenerated_server
        else:
            opencrowd_logger.debug('Generating new opencrowd server...')
            opencrowd_server = Opencrowd()
            return opencrowd_server

    def get_assignment_objects(self, assignment_ids=None, project_ids=None):
        """
        Return already saved assignment objects (does not run update())

        :param assignment_ids: optionally specify which assignments to return based on a list of ids
        :type assignment_ids: list of str
        :param project_ids: optionally specify which projects to scan for assignments
        :type project_ids: list of str
        :returns: list of assignment objects
        """

        assignment_ids = assignment_ids if assignment_ids is not None else self.list_assignment_ids(project_ids=project_ids)
        database = Database(DB_HOST, DB_PORT)
        assignments = []
        assignment_ids = [assignment_ids] if type(assignment_ids) is not list else assignment_ids
        for assignment_id in assignment_ids:
            assignments.append(database.get(ASSIGNMENT_HEADER + assignment_id))
        return assignments

    @staticmethod
    def generate_response(assignment, response_type='default'):
        """
        Create a Response class based on the specified assignment

        :param assignment: completed assignment object
        :type assignment: Assignment
        :param response_type: "default" or "answers_only"
        :type response_type: str
        :returns: Response
        """

        if response_type == 'answers_only':
            response = AnswersOnly(assignment=assignment)
        else:
            response = Default(assignment=assignment)
        return response

if __name__ == '__main__':
    from opencrowd.model.base.task import Task
    from opencrowd.model.base import Question
    from opencrowd.model.section import TextBox, Image, BoundingBox

    opencrowd = Opencrowd.regenerate()

    text_box = TextBox(main_title='Title', text=['Paragraph 1', 'Paragraph 2'])
    image = Image(urls=['http://lorempixel.com/400/200/nature/'])
    bounding_box = BoundingBox(url="http://lorempixel.com/800/400/nature")
    opencrowd.delete_sandbox()
    projects = []
    for k in range(3):
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

        projects.append(project)

    for project in projects:
        opencrowd.add_project(project)
        project.submit_tasks()

    opencrowd.save()
