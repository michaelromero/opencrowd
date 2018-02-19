.. opencrowd documentation master file, created by
   sphinx-quickstart on Wed Aug 23 15:09:54 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

opencrowd
=========
Easy, powerful crowdsourcing
----------------------------

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   dev/tutorial
   dev/intro
   dev/base/base
   dev/academics
   dev/future
   dev/use_cases

opencrowd structure
===================
opencrowd begins with a :ref:`Project<project>`. A Project focuses around a specific goal, like image classification or sentiment analysis.

A Project contains :ref:`Tasks<task>`. A Task is meant to differentiate between experiments.

A Task contains :ref:`Questions<question>`. In this case, consider a Question to be an entire page that will be viewed in the browser by a worker.

Questions are composed of :ref:`Sections<sections>`. A Section can be represented by many different components, and they're chained together to form an HTML document in a Question. For example, a text box

opencrowd currently supports the following sections, each with specific configurations and nuances:
 - :ref:`Bounding Box<bounding_box>`
 - :ref:`Collapsible Instruction Panel<collapse_panel>`
 - :ref:`Images<image>`
 - :ref:`Input Groups<input_group>`
 - :ref:`Text Boxes<text_box>`

Crowdsourcing platform with API interface that allows collection of human work via `Amazon Mechanical Turk <https://www.mturk.com/mturk/welcome>`_. The platform focuses on generalized construction of tasks, and provides a full pipeline for creation, retrieval, and analysis for a variety of data-gathering tasks.
These tasks could range from data collection and verification for machine learning like labels for image classification, image quality, bounding boxes for object detection, etc, to possibly other non-machine learning use cases where human judgement is needed.
Usually creating a crowd sourcing task requires a good understanding of AMT (using an API framework, or the more limiting online front-end): worker management, creating-submitting-retrieving-evaluating tasks, designing templates, etc., which often requires time and prior experience.
This crowd sourcing platform resolves these issues by providing an interface that abstracts the complexities of crowd sourcing tasks and makes it simple for users to define new tasks while leveraging the same platform for worker evaluation and answer processing.




Example (For Developers)
========================
Pairwise Image Comparison
-------------------------
.. code-block:: python

   import opencrowd

   # create a Project
   project = opencrowd.add_project(project=Project(title='Pairwise Image Comparison',
                                   description='Compare two images against different criteria',
                                   crowdsource=CROWDSOURCE_SPECIFICATION))

   # separate similar experiments from each other via Tasks
   task = opencrowd.task()

   # gather input data
   # in this case, the images to compare are sequentially ordered in a txt file
   with open('comparison_images.txt', 'r') as f:
       urls = f.readlines()

   # parse the pairs
   pairs = []
   for i in range(0, len(urls), 2):
       pairs.append((urls[i], urls[i+1]))

   # for each pair, let's design a Question
   for pair in pairs:
       question = Question()
       # Generate unique Question layout via Sections:
       # Instructions
       # Images side by side
       # Radio buttons to select which is better
       instruction = TextBox(main_title='Which image is more aesthetically pleasing?', text=['Blah blah objective', 'Blah blah subjective'])
       images = Image(urls=[pair[0], pair[1]])
       option_a = Option(text='The left image is better', on_hover='The left image is more aesthetically pleasing than the right', value='left', correct=None)
       option_b = Option(text='The right image is better', on_hover='The right image is more aesthetically pleasing than the left', value='right', correct=None)
       # attach the above options to the radio group
       radio = RadioGroup(options=[option_a, option_b])
        
       # Add the sections in order 
       question.add_section(instruction, parents='root')
       question.add_section(images, parents=instruction)
       question.add_section(radio, parents=images)
       # attach the question to the task
       task.add_question(question)
   # attach the task to the project
   project.add_task(task)
   # generate the HITs (Human Intelligence Tasks) inside of the task
   task.create_HITs(questions_per_assignment=10, assignments_per_HIT=3)
   # submit them to the crowd
   project.submit_tasks()

.. image:: _static/comparison_render.png
