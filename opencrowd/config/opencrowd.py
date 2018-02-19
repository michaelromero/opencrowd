import os
import sys
import logging
import json

config_logger = logging.getLogger('config')


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = BASE_DIR + "/template/"
sys.path.insert(0, BASE_DIR)
sys.path.insert(1, TEMPLATES_DIR)


#AWS KEY LOCATION
AWS_KEYS = '~/.aws/opencrowd'

# opencrowd
ENV = 'development'
SERVER = "127.0.0.1:8000"

if ENV == "production":
    endpoint = 'https://mturk-requester.us-east-1.amazonaws.com'
    form_submission_action = 'https://www.mturk.com/mturk/externalSubmit'
else:
    endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    form_submission_action = 'https://workersandbox.mturk.com/mturk/externalSubmit'

keys = {}

try:
    keys = json.load(open(os.path.expanduser(AWS_KEYS)))

except Exception as e:
    config_logger.error("Unable to load AWS keys. An exception of type {} occurred. Arguments:\n{!r}".format(
        type(e).__name__, e.args))
    keys['aws_access_key_id'] = 'nokey'
    keys['aws_secret_access_key'] = 'nokey'

CROWDSOURCE_SPECIFICATION = {
    'type': 'amt',
    'endpoint': endpoint,
    'form_submission_action': form_submission_action,
    'region_name': 'us-east-1',
    'aws_access_key_id': keys['aws_access_key_id'],
    'aws_secret_access_key': keys['aws_secret_access_key']
}
# save locations in redis
WORKER_HEADER = 'opencrowd_worker_'
SECTION_HEADER = 'opencrowd_section_'
QUESTION_HEADER = 'opencrowd_question_'
TASK_HEADER = 'opencrowd_task_'
HIT_HEADER = 'opencrowd_HIT_'
ASSIGNMENT_HEADER = 'opencrowd_assignment_'
PROJECT_HEADER = 'opencrowd_project_'
SERVER_HEADER = 'opencrowd_server'

# logging
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG_LEVEL = LOG_LEVELS[1]
logging.basicConfig(format="%(asctime)s [%(name)-12.12s] [%(levelname)-5.5s]  %(message)s",
                    level=LOG_LEVEL,
                    stream=sys.stdout)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
