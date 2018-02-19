"""
.. module:: assignment
   :platform: Unix, Mac
   :synopsis: When a HITs are answered, they'll be retrieved as an assignment

When a HITs are answered, they'll be retrieved as assignments. Direct interaction with this
class is not necessary, as it will be interpreted via a Response object.

.. moduleauthor:: Michael Romero <michaelrom@zillowgroup.com>


"""


import xmltodict
import json
import logging
from opencrowd.config.opencrowd import ASSIGNMENT_HEADER
from opencrowd.config.redis import DB_HOST, DB_PORT
from opencrowd.model.database import Database
from opencrowd.model.base.node import OpencrowdNode

assignment_logger = logging.getLogger('assignment')


class Assignment(OpencrowdNode):
    """
    An assignment represents a worker's answers. An assignment is created when an opencrowd server, project, or task
    updates itself. The HITs are pulled from Amazon, and the results attached are parsed into assignments and stored.
    Assignments will be further used in the Response object. Direct interaction is not necessary.
    """

    def __init__(self, assignment):
        """
        assignment['Answer']:
        {
            "QuestionFormAnswers": {
                "@xmlns": "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd",
                "Answer": {
                    "QuestionIdentifier": "jsonObject",
                    "FreeText": "{assignment:{}}"
                }
            }
        }
        """

        super(Assignment, self).__init__()
        self.AssignmentId = assignment.get('AssignmentId')
        self.WorkerId = assignment.get('WorkerId')
        self.HITId = assignment.get('HITId')
        self.AssignmentStatus = assignment.get('AssignmentStatus')

        if not assignment.get('SubmitTime', None) is None and not assignment.get('AcceptTime', None) is None:
            self.MinutesTaken = round((assignment.get('SubmitTime') - assignment.get('AcceptTime')).total_seconds() / 60.0,2)
            self.SecondsTaken = round((assignment.get('SubmitTime') - assignment.get('AcceptTime')).total_seconds(),2)

        if assignment.get('Answer', None) is not None:
            answer = xmltodict.parse(assignment.get('Answer'))
            # QuestionIdentifier = jsonObject
            # FreeText = the value attached to jsonObject
            self.Answer = json.loads(answer['QuestionFormAnswers']['Answer']['FreeText'])
        if assignment.get('AutoApprovalTime', None) is not None:
            self.AutoApprovalTime = assignment.get('AutoApprovalTime').strftime("%Y-%m-%d %H:%M:%S")

        if assignment.get('AcceptTime', None) is not None:
            self.AcceptTime = assignment.get('AcceptTime').strftime("%Y-%m-%d %H:%M:%S")
        if assignment.get('SubmitTime', None) is not None:
            self.SubmitTime = assignment.get('SubmitTime').strftime("%Y-%m-%d %H:%M:%S")
        if assignment.get('ApprovalTime', None) is not None:
            self.ApprovalTime = assignment.get('ApprovalTime').strftime("%Y-%m-%d %H:%M:%S")
        if assignment.get('RejectionTime', None) is not None:
            self.RejectionTime = assignment.get('RejectionTime').strftime("%Y-%m-%d %H:%M:%S")
        if assignment.get('Deadline', None) is not None:
            self.Deadline = assignment.get('Deadline').strftime("%Y-%m-%d %H:%M:%S")

        if not assignment.get('SubmitTime', None) is None and assignment.get('AcceptTime', None) is None:
            self.MinutesTaken = (assignment.get('SubmitTime') - assignment.get('AcceptTime')).total_seconds() / 60.0
            self.SecondsTaken = (assignment.get('SubmitTime') - assignment.get('AcceptTime')).total_seconds()
        self.RequesterFeedback = assignment.get('RequesterFeedback')

        self.save()

    def save(self):
        assignment_logger.debug("Saving Assignment {}".format(self.AssignmentId))
        database = Database(DB_HOST, DB_PORT)
        database.set(ASSIGNMENT_HEADER + self.AssignmentId, self)
