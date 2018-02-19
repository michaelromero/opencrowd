# from sections.image import Image
# from sections.bounding_box import BoundingBox
# from question import Question
# from task import Task

# question_a = Question()
#
# question_a.add_section(Image(urls=["https://lorempixel.com/800/400/nature"]))
# question_a.add_section(Image(urls=["https://lorempixel.com/400/200/nature",
#                                    "https://lorempixel.com/400/200/nature"]))
#
# checkbox_group_example = CheckboxGroup(identity='checkbox_group_example',
#                                        options=[Option(text='option_a checkbox',
#                                                        on_hover='option_a checkbox hover',
#                                                        value='option_a checkbox',
#                                                        correct=True),
#                                                 Option(text='option_b checkbox',
#                                                        on_hover='option_b checkbox hover',
#                                                        value='option_b checkbox',
#                                                        correct=True)])
#
# checkbox_group_example.add_option(Option(text='added option: option_c checkbox',
#                                          on_hover='option_c checkbox',
#                                          value='option_c checkbox',
#                                          correct=True))
#
# question_a.add_section(checkbox_group_example)
#
# question_b = Question()
#
# question_b.add_section(Image(urls=["https://lorempixel.com/800/400/nature"]))
# question_b.add_section(Image(urls=["https://lorempixel.com/800/400/nature"]))
# question_b.add_section(Image(urls=["https://lorempixel.com/800/400/nature"]))
# question_b.add_section(Image(urls=["https://lorempixel.com/400/200/nature",
#                                    "https://lorempixel.com/400/200/nature"]))
# question_b.add_section(Image(urls=["https://lorempixel.com/400/200/nature",
#                                    "https://lorempixel.com/400/200/nature",
#                                    "https://lorempixel.com/400/200/nature",
#                                    "https://lorempixel.com/400/200/nature",
#                                    "https://lorempixel.com/400/200/nature"]))
#
# radio_group_example = RadioGroup(identity='radio_group_example',
#                                  options=[Option(text='option_a radio',
#                                                  on_hover='option_a radio hover',
#                                                  value='option_a radio',
#                                                  correct=True),
#                                           Option(text='option_b radio',
#                                                  on_hover='option_b radio hover',
#                                                  value='option_b radio',
#                                                  correct=True),
#                                           Option(text='option_c radio',
#                                                  on_hover='option_c radio hover',
#                                                  value='option_c radio',
#                                                  correct=True)
#                                           ])
#
# radio_group_example.add_option(Option(text='added option: option_d radio',
#                                       on_hover='option_d radio',
#                                       value='option_d radio',
#                                       correct=True))
#
# question_b.add_section(radio_group_example)
# question_a.add_section(radio_group_example)
#
#
# # generate 10 tasks, fill with 20 questions,
# # generate 2 HITs (10 questions each)
# tasks = []
# text_box = TextBox(main_title='Instruction Box', text=['Paragraph 1', 'Paragraph 2'])
# bounding_box1 = BoundingBox()
# bounding_box1.set_url("https://lorempixel.com/800/400/nature")
# bounding_box2 = BoundingBox()
# bounding_box2.set_url("https://lorempixel.com/800/400/nature")
# bounding_box3 = BoundingBox()
# bounding_box3.set_url("https://lorempixel.com/800/400/nature")
#
#
# bb = Question()
# bb.add_section(text_box)
# bb.add_section(bounding_box1)
# bb.add_section(bounding_box2)
# bb.add_section(bounding_box3)
#
#
# for i in range(10):
#     new_task = Task()
#     for j in range(10):
#         new_task.add_question(question_a)
#         new_task.add_question(question_b)
#         new_task.add_question(bb)
#         new_task.add_question(bb)
#
#     new_task.create_HITs(4, 3)
#     tasks.append(new_task)
#
