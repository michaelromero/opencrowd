"""
.. module:: amazonmechanicalturk
   :platform: Unix, Mac
   :synopsis: The Amazon Mechanical Turk crowd interface for opencrowd

Provides an interface with amazon mechanical turk to push opencrowd generated
HITs. Amazon Mechanical Turk account specifications are defined in
opencrowd/config/opencrowd.

"""
import logging
import boto3
import datetime
from botocore.errorfactory import ClientError
from opencrowd.model.crowd.crowd import Crowd

amt_logger = logging.getLogger("amt")


def threaded_update(connection, HIT_id):
    connection.update_expiration_for_hit(HITId=HIT_id, ExpireAt=datetime.datetime(2015, 1, 1))


def threaded_delete_hit(connection, HIT_id):
    connection.delete_hit(HITId=HIT_id)


class AmazonMechanicalTurk(Crowd):
    """
    Provides the python library Boto3 with the AWS information needed to start
    a connection

    :param endpoint: Pointing to either the AMT sandbox or production servers
    :type endpoint: str
    :param form_submission_action: needs to match with the endpoint, this will\
    either submit to the sandbox or production
    :type form_submission_action: str
    :param region_name: generally 'us-east-1'
    :type region_name: str
    :param aws_access_key_id: The aws access key, available on your aws account
    :type aws_access_key_id: str
    :param aws_secret_access_key: available on your aws account
    :type aws_secret_access_key: str
    """
    def __init__(self,
                 endpoint,
                 form_submission_action,
                 region_name,
                 aws_access_key_id,
                 aws_secret_access_key):
        super(AmazonMechanicalTurk, self).__init__()
        self.endpoint = endpoint
        self.form_submission_action = form_submission_action
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.connection = self.generate_crowdsource_connection()

    def generate_crowdsource_connection(self):
        """
        :return: boto3 mturk client
        """
        try:
            return boto3.client(service_name='mturk',
                                endpoint_url=self.endpoint,
                                region_name=self.region_name,
                                aws_access_key_id=self.aws_access_key_id,
                                aws_secret_access_key=self.aws_secret_access_key)
        except Exception as e:
            amt_logger.error("Unable to generate crowdsource connection. An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args))

    def push(self, HIT):
        response = self.connection.create_hit(MaxAssignments=HIT.assignments_per_hit,
                                              AutoApprovalDelayInSeconds=HIT.AutoApprovalDelayInSeconds,
                                              LifetimeInSeconds=HIT.lifetime_in_seconds,
                                              AssignmentDurationInSeconds=HIT.assignment_duration_in_seconds,
                                              Reward=HIT.Reward,
                                              Title=HIT.Title,
                                              Keywords=HIT.Keywords,
                                              Description=HIT.Description,
                                              Question=HIT.render(self.form_submission_action))
        return response

    def list_hits(self):
        """
        List all HITs on AMT

        :return: list of Amazon HIT dicts
        """
        connection = self.generate_crowdsource_connection()
        response = connection.list_hits(MaxResults=100)
        hits = []
        [hits.append(hit['HITId']) for hit in response['HITs']]
        while 'NextToken' in response:
            response = connection.list_hits(NextToken=response['NextToken'], MaxResults=100)
            [hits.append(hit['HITId']) for hit in response['HITs']]

        amt_logger.info("Number of HITs retrieved: {}".format(len(hits)))
        return hits

    def get_hit(self, HITId):
        """
        Get a specific HIT

        :param HITId: id of the HIT to retrieve
        :type HITId: str
        :return: Amazon HIT dict
        """
        connection = self.generate_crowdsource_connection()
        hit = connection.get_hit(HITId=HITId)
        return hit

    def get_assignment(self, AssignmentId):
        """
        Get a specific assignment

        :param AssignmentId: id of the assignment to retrieve
        :type AssignmentId: str
        """
        connection = self.generate_crowdsource_connection()
        assignment = connection.get_assignment(AssignmentId=AssignmentId)
        return assignment

    def delete_sandbox(self):
        """
        delete all HITs on the sandbox. useful for testing
        """
        HITs = self.list_hits()

        for index, HIT_id in enumerate(HITs):
            amt_logger.info("Deleting HIT {0}/{1}".format(index+1, len(HITs)))
            self.connection.update_expiration_for_hit(HITId=HIT_id, ExpireAt=datetime.datetime(2015, 1, 1))
            assignment_ids = self.gather_submitted_assignments(HIT_id)
            self.approve_assignment_ids(assignment_ids)
            try:
                self.connection.delete_hit(HITId=HIT_id)
            except ClientError as e:
                if type(e).__name__ == 'RequestError':  # RequestError
                    amt_logger.error("{}".format(e.response['Error']['Message']))
            except Exception as e:
                amt_logger.error("Unable to delete hits. Error: %s" % str(e))

    def gather_submitted_assignments(self, hit_id):
        """
        Gather 'submitted' assignments under this HIT

        :param hit_id: gather assignments from this HIT
        :return: list of assignment ids (they were updated in-place)
        """
        assignment_ids = []
        response = self.connection.list_assignments_for_hit(HITId=hit_id)
        # [assignment_ids.append(k['AssignmentId']) for k in response['Assignments']]
        for k in response['Assignments']:
            assignment_ids.append(k['AssignmentId'])
        while 'NextToken' in response:
            response = self.connection.list_assignments_for_hit(HITId=hit_id, NextToken=response['NextToken'])
            # [assignment_ids.append(k['AssignmentId']) for k in response['Assignments']]
            for k in response['Assignments']:
                assignment_ids.append(k['AssignmentId'])
        return assignment_ids

    def list_assignments_for_hit(self, hit_id):
        """
        Gather assignments for this HIT

        :param hit_id: gather assignments from this HIT
        :return: list of AMT assignment dicts
        """
        # check for desync of database (redis) and the opencrowd server
        assignments = []
        response = self.connection.list_assignments_for_hit(HITId=hit_id)
        # [assignment_ids.append(k['AssignmentId']) for k in response['Assignments']]
        for k in response['Assignments']:
            assignments.append(k)
        while 'NextToken' in response:
            response = self.connection.list_assignments_for_hit(HITId=hit_id, NextToken=response['NextToken'])
            # [assignment_ids.append(k['AssignmentId']) for k in response['Assignments']]
            for k in response['Assignments']:
                assignments.append(k)
        return assignments

    def approve_assignment_ids(self, assignment_ids):
        """
        Approve an assignment on AMT. This will pay the worker the reward
        amount for the Task.

        :param assignment_ids: assignment ids to approve on AMT
        :type assignment_ids: list
        """
        for assignment_id in assignment_ids:
            assignment = self.connection.get_assignment(AssignmentId=assignment_id)
            if assignment['Assignment']['AssignmentStatus'] != "Approved":
                self.connection.approve_assignment(AssignmentId=assignment_id)

# import boto3
# import xmltodict
# import json
# import logging
# import datetime
#
# from opencrowd.classes.base.worker import Worker
# from opencrowd.classes.base.database import Database
# import opencrowd.classes.base.analysis
# from opencrowd.config.config import DB_HOST, DB_PORT
# from botocore.errorfactory import ClientError
#
# amt_logger = logging.getLogger('crowd')
#
# RESET_DATA = True # if RESET_DATA, assignments, workers, etc will be erased and re-collected
# PULL_ALL_HITS = True  # if false: only pull HITs that are 'Submitted'
#
# class Crowd(object):
#     def __init__(self):
#         pass
#
#     def push(self, html_doc, task):
#         raise NotImplementedError()
#
#
# class AMT(Crowd):
#     def __init__(self,
#                  approve_assignments_on_retrieval,
#                  form_submission_action,
#                  endpoint,
#                  region_name,
#                  aws_access_key_id,
#                  aws_secret_access_key):
#         """
#         :type aws_access_key_id: str
#         :param approve_assignments_on_retrieval:
#         :param form_submission_action:
#         :param endpoint:
#         :param region_name:
#         :param aws_access_key_id:
#         :param aws_secret_access_key:
#         """
#         super(AMT, self).__init__()
#         self.approve_assignments_on_retrieval = approve_assignments_on_retrieval
#         self.form_submission_action = form_submission_action
#         self.endpoint = endpoint
#         self.region_name = region_name
#         self.aws_access_key_id = aws_access_key_id
#         self.aws_secret_access_key = aws_secret_access_key
#         self.connection = boto3.client('mturk',
#                                        endpoint_url=self.endpoint,
#                                        region_name=self.region_name,
#                                        aws_access_key_id=self.aws_access_key_id,
#                                        aws_secret_access_key=self.aws_secret_access_key)
#
#     def push(self, html_doc, task, project):
#         self.create_hit(html_doc, task, project)
#
#     def create_hit(self, html_doc, task, project):
#         result = self.connection.create_hit(MaxAssignments=task.assignments_per_hit,
#                                             AutoApprovalDelayInSeconds=task.auto_approval_delay_in_seconds,
#                                             LifetimeInSeconds=task.lifetime_in_seconds,
#                                             AssignmentDurationInSeconds=task.assignment_duration_in_seconds,
#                                             Reward=task.reward,
#                                             Title=task.title,
#                                             Keywords=task.keywords,
#                                             Description=task.description,
#                                             Question=html_doc,
#                                             RequesterAnnotation=task.task_id)
#         task.hit_ids.append(result['HIT']['HITId'])
#         task.save()
#         project.hit_ids.append(result['HIT']['HITId'])
#         project.save()
#
#     def approve_assignment(self, assignment_id):
#         self.connection.approve_assignment(AssignmentId=assignment_id)
#
#     def reset_data(self, project, task):
#         amt_logger.warning("RESETTING ALL DATA!")
#         project.analysis = None
#         project.known_votes = {}
#         project.unknown_votes = {}
#         # hardcore worker deletion from redis to clear cloned answers...
#         amt_logger.warning("WIPING {} WORKERS!!!".format(len(project.workers)))
#         for worker_id in project.workers:
#             db = Database(DB_HOST, DB_PORT)
#             db.delete_worker(worker_id)
#             amt_logger.warning("Wiped worker: {}".format(worker_id))
#
#         project.workers = {}
#         task.known_votes = {}
#         task.unknown_votes = {}
#         task.qualifications_awarded = 0
#         task.assignments = {}
#         task.save()
#         project.save()
#         RESET_DATA = False
#
#     def process_assignments(self, assignments):
#         if RESET_DATA == True:
#             task, project = self.initialize(assignments[0]['task_id'])
#             self.reset_data(project, task)
#         for idx,assignment in enumerate(assignments):
#             amt_logger.info("Processing assignment {}/{} assignment id: {}".format(idx,len(assignments), assignment['assignment_id']))
#             task, project = self.initialize(assignment['task_id'])
#             if assignment['assignment_id'] not in task.assignments or RESET_DATA:
#                 task, project = self.initialize(assignment['task_id'])
#                 worker = self.find_or_generate_new_worker(assignment['worker_id'])
#                 if worker.worker_id not in project.workers:
#                     amt_logger.info("Adding worker {}".format(worker.worker_id))
#                     project.workers[worker.worker_id] = worker
#                     project.save()
#                 else:
#                     if worker.worker_id == "A2MRWQ2SKCTLT4":
#                         print worker
#                         print "{}".format(project.workers[worker.worker_id]["statistics"]["validation_statistics"])
#                 right_answers, wrong_answers, total, statistics_to_upgrade, task, project = task.grade(assignment, worker)
#                 if task.reward_qualification:
#                     task = self.grant_qualifications(right_answers, task, worker)
#
#                 if self.approve_assignments_on_retrieval:
#                     try:
#                         if assignment['status'] == 'Submitted':
#                             self.approve_assignment(assignment['assignment_id'])
#                             assignment['status'] = 'Approved'
#
#                     except Exception as e:
#                         template = "An exception of type {0} occurred. Arguments:\n{1!r}"
#                         message = template.format(type(e).__name__, e.args)
#                         amt_logger.error(message)
#                 project.save_worker(worker)
#                 worker.save()
#                 project.save()
#                 task.update(assignment)
#                 #update plurality
#
#
#     def initialize(self, task_id):
#         db = Database(DB_HOST, DB_PORT)
#         task = db.get('opencrowd_task_' + task_id)
#         project = db.get(task.project_database_entry_name)
#         return task, project
#
#     def find_or_generate_new_worker(self, worker_id):
#         db = Database(DB_HOST, DB_PORT)
#         if db.worker_exists(worker_id):
#             worker = db.get('opencrowd_worker_' + worker_id)
#         else:
#             worker = Worker(worker_id)
#         return worker
#
#     def from_hits_get_all_submitted_assignments(self, hit_ids):
#         assignments = []
#         amt_logger.info('Gathering submitted assignments...')
#         for index_hit_ids, hit_id in enumerate(hit_ids):
#             if PULL_ALL_HITS:
#                 amt_logger.info('{}/{} : Pulling ALL assignments...'.format(index_hit_ids, len(hit_ids)))
#                 response = self.connection.list_assignments_for_hit(HITId=hit_id)
#             else:
#                 amt_logger.info('{}/{} : Pulling \'submitted\' assignments...'.format(index_hit_ids, len(hit_ids)))
#                 response = self.connection.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted'])
#             for assignment in response['Assignments']:
#                 assignments.append(self.extract_info_from_amazon_response(assignment))
#
#             while 'NextToken' in response:
#                 if PULL_ALL_HITS:
#                     amt_logger.info('{}/{} : Next Token: Pulling ALL assignments...'.format(index_hit_ids, len(hit_ids)))
#                     response = self.connection.list_assignments_for_hit(HITId=hit_id, NextToken=response['NextToken'])
#                 else:
#                     amt_logger.info('{}/{} : Next Token: Pulling \'submitted\' assignments...'.format(index_hit_ids, len(hit_ids)))
#                     response = self.connection.list_assignments_for_hit(HITId=hit_id, NextToken=response['NextToken'], AssignmentStatuses=['Submitted'])
#                 for assignment in response['Assignments']:
#                     assignments.append(self.extract_info_from_amazon_response(assignment))
#
#         amt_logger.info('Number of assignments gathered: {}'.format(len(assignments)))
#         return assignments
#
#     def extract_info_from_amazon_response(self, assignment):
#                 """ assignment['Answer']:
#                 {
#                     "QuestionFormAnswers": {
#                         "@xmlns": "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd",
#                         "Answer": {
#                             "QuestionIdentifier": "jsonObject",
#                             "FreeText": "{assignment:{}}"
#                         }
#                     }
#                 }
#                 """
#                 accept_time = (assignment['AcceptTime'])
#                 submit_time = (assignment['SubmitTime'])
#
#                 answer = xmltodict.parse(assignment['Answer'])
#                 assignment_dict = json.loads(answer['QuestionFormAnswers']['Answer']['FreeText'])
#                 assignment_dict['time_information'] = {}
#                 assignment_dict['time_information']['accept_time'] = accept_time.strftime("%Y-%m-%d %H:%M:%S")
#                 assignment_dict['time_information']['submit_time'] = submit_time.strftime("%Y-%m-%d %H:%M:%S")
#                 assignment_dict['time_information']['time_diff_accept_and_submit_minutes'] = (submit_time - accept_time).total_seconds() / 60.0
#                 assignment_dict['time_information']['time_diff_accept_and_submit_seconds'] = (submit_time - accept_time).total_seconds()
#                 assignment_dict['status'] = assignment['AssignmentStatus']
#                 return assignment_dict
#
#     def pull(self, query_id):
#         db = Database(DB_HOST, DB_PORT)
#         project_or_task, type_of_query = db.query(query_id)
#         hit_ids = project_or_task.hit_ids
#         amt_logger.info('Number of hit ids: {}'.format(len(hit_ids)))
#         assignments = self.from_hits_get_all_submitted_assignments(hit_ids)
#         self.process_assignments(assignments)
#
#     def worker_grant_qualification(self, task, worker):
#             if task.qualification_id not in worker.qualifications:
#               self.connection.associate_qualification_with_worker(QualificationTypeId=task.qualification_id, WorkerId=worker.worker_id, IntegerValue=100, SendNotification=True)
#               worker.qualifications.append(task.qualification_id)
#
#
#     def grant_qualifications(self, right_answers, task, worker):
#         if task.minimum_for_qualification is not None and task.reward_qualification is True:
#             if right_answers >= task.minimum_for_qualification:
#                 self.worker_grant_qualification(task, worker)
#                 task.qualifications_awarded += 1
#         if task.minimum_for_qualification is not None and task.reward_qualification is False:
#             amt_logger.error('Have minimum for qualification but reward qualification is false. Exiting')
#             exit(1)
#         task.save()
#         return task
#
#     def get_all_hit_ids(self):
#         response = self.connection.list_hits(MaxResults=100)
#         amt_logger.info("Gathering Hits: {}".format(response['NumResults']))  # , flush=True)
#         hit_ids = []
#         [hit_ids.append(k['HITId']) for k in response['HITs']]
#         while 'NextToken' in response:
#             response = self.connection.list_hits(NextToken=response['NextToken'], MaxResults=100)
#             amt_logger.info("Gathering Hits: {}".format(response['NumResults']))  # , flush=True)
#             [hit_ids.append(k['HITId']) for k in response['HITs']]
#
#         amt_logger.info("Number of HITs retrieved: {}".format(len(hit_ids)))
#         return hit_ids
#
#     def expire_if_assignable(self, hit_id):
#         self.connection.update_expiration_for_hit(HITId=hit_id, ExpireAt=datetime.datetime(2015, 1, 1))
#         amt_logger.info('Expired HIT {}'.format(hit_id))
#
#     def gather_submitted_assignments(self, hit_id):
#         assignment_ids = []
#         response = self.connection.list_assignments_for_hit(HITId=hit_id, )
#         [assignment_ids.append(k['AssignmentId']) for k in response['Assignments']]
#         while 'NextToken' in response:
#             response = self.connection.list_assignments_for_hit(HITId=hit_id, NextToken=response['NextToken'])
#             [assignment_ids.append(k['AssignmentId']) for k in response['Assignments']]
#         return assignment_ids
#
#     def approve_assignments(self, assignment_ids):
#         for assignment_id in assignment_ids:
#             self.connection.approve_assignment(AssignmentId=assignment_id)
#
#     def delete_all_hits(self):
#         hit_ids = self.get_all_hit_ids()
#         for index, hit_id in enumerate(hit_ids):
#             amt_logger.info("Deleting HIT {0}/{1}".format(index, len(hit_ids)))
#             self.expire_if_assignable(hit_id)
#             assignment_ids = self.gather_submitted_assignments(hit_id)
#             for assignment_id in assignment_ids:
#                 assignment = self.connection.get_assignment(AssignmentId=assignment_id)
#                 #print assignment
#                 #print assignment['Assignment']['AssignmentStatus']
#                 #print assignment['HIT']['HITStatus']
#                 #exit(1)
#                 if assignment['Assignment']['AssignmentStatus'] != "Approved":
#                     self.approve_assignments(assignment_ids)
#             try:
#                 self.connection.delete_hit(HITId=hit_id)
#             except ClientError as e:
#                 if type(e).__name__ == 'RequestError':  # RequestError
#                     amt_logger.error("{}".format(e.response['Error']['Message']))
#             except Exception as e:
#                 amt_logger.error("Unable to delete hits. Error: %s" % str(e))
#                 response = "<h1>Unable to delete hits.</h1><br><p>Error: %s</p>" % str(e)
#                 return response
#
#         response = "<h1>Deleted {} HITs.</h1>".format(len(hit_ids))
#         return response
