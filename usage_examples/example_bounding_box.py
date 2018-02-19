from opencrowd.model.server import Opencrowd
from opencrowd.model.project import Project
from opencrowd.model.base.task import Task
from opencrowd.model.base import Question
from opencrowd.model.section import CollapsePanel, TextBox, Image, BoundingBox, RadioGroup, CheckboxGroup, Option
from opencrowd.config.opencrowd import CROWDSOURCE_SPECIFICATION


def create_bounding_box_task_with_additional_buttons(project, num_questions=10):
    task = Task()

    for j in range(num_questions):
        collapsable_instructions = CollapsePanel(title='Example Title',
                                                 body='Example Body',
                                                 footer='Example Footer')

        bounding_box_textbox_instruction = TextBox(main_title='Example Instructions: Draw a box over the image',
                                                   text=['Example Paragraph 1...', 'Example Paragraph 2...'])

        bounding_box = BoundingBox(url="http://lorempixel.com/800/400/nature")

        radio_group_instruction = TextBox(main_title='Example Main Title: Does the image have a shower?',
                                          text=['Example Text:Not only a shower, but a bath also counts'])

        # create a radio group, which are composed of Options
        shower_button = Option(text='Yes', on_hover='hover text here', value='shower', correct=None)
        no_shower_button = Option(text='No', on_hover='hover text here', value='no_shower', correct=None)
        shower_radio_group = RadioGroup(options=[shower_button, no_shower_button])

        # create a checkbox group, which are composed of Options
        spout_checkbox = Option(text='Shower with a spout', on_hover='...', value='spout', correct=None)
        tub_checkbox = Option(text='Bath tub shape', on_hover='...', value='tub', correct=None)
        bathroom_checkbox_group = CheckboxGroup(options=[spout_checkbox, tub_checkbox])

        # link the shower radio button to the checkbox group
        shower_button.add_children(bathroom_checkbox_group)

        # attach these unique objects to a question in desired render order
        question = Question()
        question.add_section(collapsable_instructions, parents='root')
        question.add_section(bounding_box_textbox_instruction, parents=collapsable_instructions)
        question.add_section(bounding_box, parents=bounding_box_textbox_instruction)
        question.add_section(radio_group_instruction, parents=bounding_box)
        question.add_section(shower_radio_group, parents=radio_group_instruction)
        question.add_section(bathroom_checkbox_group, parents=None)

        # add the question to the task question pool
        task.add_question(question)

    # add the task to a project
    project.add_task(task)

    # have the task create HITs from itself
    task.create_HITs(questions_per_assignment=num_questions, assignments_per_HIT=3)


if __name__ == '__main__':
    opencrowd = Opencrowd.regenerate()
    opencrowd.delete_sandbox()

    project = opencrowd.add_project(project=Project(title='Test Project',
                                                    description='Test Description',
                                                    crowdsource=CROWDSOURCE_SPECIFICATION))
    create_bounding_box_task_with_additional_buttons(project)

    # for each task attached to the project, if it has created HITs, submit them to Amazon Mechanical Turk
    project.submit_tasks()
