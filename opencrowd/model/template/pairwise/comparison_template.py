import logging

from opencrowd.model.server import Opencrowd
from opencrowd.model.project import Project
from opencrowd.model.base.task import Task
from opencrowd.model.base import Question
from opencrowd.model.section import TextBox, Image, BoundingBox, RadioGroup, CheckboxGroup, Option
from opencrowd.config.opencrowd import CROWDSOURCE_SPECIFICATION
comparison_logger = logging.getLogger('comparison')

opencrowd = Opencrowd.regenerate()
#
opencrowd.delete_sandbox()
#
project = opencrowd.add_project(
    project=Project(title='Comparison', description='Compare two images to see which is more aesthetically pleasing.', crowdsource=CROWDSOURCE_SPECIFICATION))

task = Task()

urls = []
with open('short_comparison.txt', 'r') as f:
    urls = f.readlines()

pairs = []
for i in range(0, len(urls), 2):
    pairs.append((urls[i], urls[i+1]))

for pair in pairs:
    question = Question()
    instruction = TextBox(main_title='Which image is more aesthetically pleasing?', text=['Blah blah objective', 'Blah blah subjective'])
    images = Image(urls=[pair[0], pair[1]])
    option_a = Option(text='The left image is better', on_hover='The left image is more aesthetically pleasing than the right', value='left', correct=None)
    option_b = Option(text='The right image is better', on_hover='The right image is more aesthetically pleasing than the left', value='right', correct=None)
    radio = RadioGroup(options=[option_a, option_b])

    question.add_section(instruction, parents='root')
    question.add_section(images, parents=instruction)
    question.add_section(radio, parents=images)
    task.add_question(question)

project.add_task(task)
task.create_HITs(questions_per_assignment=10, assignments_per_HIT=3)
project.submit_tasks()

