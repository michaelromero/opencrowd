from opencrowd.model.server import Opencrowd
from opencrowd.model.project import Project
from opencrowd.model.base.task import Task
from opencrowd.model.base import Question
from opencrowd.model.section import CollapsePanel, TextBox, Image, BoundingBox, RadioGroup, CheckboxGroup, Option
from opencrowd.config.opencrowd import CROWDSOURCE_SPECIFICATION


def delete_sandbox(opencrowd):
    opencrowd.delete_sandbox()


def generate_3_projects(opencrowd):
    projects = []
    for k in range(3):
        project = Project(title='Test Project', description='Test Description', crowdsource=CROWDSOURCE_SPECIFICATION)
        projects.append(project)
    for project in projects:
        opencrowd.add_project(project)


def dag(sections):
    for idx, section in enumerate(sections[:-1]):
        sections[idx].add_link([sections[idx+1].opencrowd_id])


def many_images(project, num_questions=10):
    task = Task()
    for j in range(num_questions):
        collapse_panel = CollapsePanel(title="Example Title", body="Header Example", footer="Footer Example")
        textbox_a = TextBox(main_title='Title_a', text=['Paragraph 1a', 'Paragraph 2a'])
        image = Image(urls=['http://lorempixel.com/400/200/nature/'])
        image2 = Image(urls=['http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/'])
        image3 = Image(urls=['http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/'])
        image4 = Image(urls=['http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/'])
        image6 = Image(urls=['http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/'])
        image12 = Image(urls=['http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/'])
        bounding_box = BoundingBox(url="http://lorempixel.com/800/400/nature")
        option_a = Option(text='a1', on_hover='hover for a1', value='a1', correct=None)
        option_a2 = Option(text='a2', on_hover='hover for a2', value='a2', correct=None)
        option_b = Option(text='b1', on_hover='hover for b1', value='b1', correct=None)
        option_b2 = Option(text='b2', on_hover='hover for b2', value='b2', correct=None)
        checkbox_a = RadioGroup(options=[option_a, option_a2])
        checkbox_b = RadioGroup(options=[option_b, option_b2])
        question = Question()
        question.add_section(collapse_panel)
        question.add_section(textbox_a)
        question.add_section(image, parents='root')
        question.add_section(image2, parents=image)
        question.add_section(image3, parents=image2)
        question.add_section(image4, parents=image3)
        question.add_section(image6, parents=image4)
        question.add_section(image12, parents=image6)
        question.add_section(bounding_box, parents=image12)
        question.add_section(checkbox_a, parents=bounding_box)
        question.add_section(checkbox_b, parents=checkbox_a)
        task.add_question(question)

    project.add_task(task)
    task.create_HITs(questions_per_assignment=num_questions, assignments_per_HIT=3)


if __name__ == '__main__':
    # start the opencrowd server
    opencrowd = Opencrowd.regenerate()
    # create a new project and attach it to the opencrowd server
    project = opencrowd.add_project(project=Project(title='Test Project', description='Test Description', crowdsource=CROWDSOURCE_SPECIFICATION))
    # create the many images example
    many_images(project)
    # submit the many images example to Amazon Mechanical Turk
    project.submit_tasks()
