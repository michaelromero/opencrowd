.. _sections:

Sections
========

Section
-------
.. automodule:: opencrowd.model.section.section
   :members:

.. _bounding_box:

Bounding Box
------------

.. automodule:: opencrowd.model.section.bounding_box
   :members:

.. code-block:: python

   bounding_box = BoundingBox(url="http://lorempixel.com/800/400/nature")

.. figure:: /_static/_sections/bounding_box/bounding_box.png
   :align:   center

   Rendering of a bounding box section

.. _collapse_panel:

Collapse Panel
--------------

.. automodule:: opencrowd.model.section.collapse_panel
   :members:

.. code-block:: python

   collapse_panel = CollapsePanel(title="Title", body="Body", footer="Footer")

.. figure:: /_static/_sections/collapsable_panel/cp_closed.png
   :align:   center

   A closed panel

.. figure:: /_static/_sections/collapsable_panel/cp_open.png
   :align:   center

   An open panel

.. _image:

Image
-----

.. automodule:: opencrowd.model.section.image
   :members:

.. code-block:: python

   image = Image(urls=['http://lorempixel.com/400/200/nature/'])
   image2 = Image(urls=['http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/'])
   image3 = Image(urls=['http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/'])
   image4 = Image(urls=['http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/'])
   image6 = Image(urls=['http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/'])
   image12 = Image(urls=['http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/', 'http://lorempixel.com/400/200/nature/'])

.. figure:: /_static/_sections/image/images.png
   :align:   center

   An example of a 1,2,3,4,6, and 12 images stacked together in 6 sections.

.. _input_group:

Input Group
-----------

.. automodule:: opencrowd.model.section.input_group
   :members:

.. code-block:: python

   radio_option_a = Option(text='a1', on_hover='hover for a1', value='a1', correct=None)
   radio_option_b = Option(text='a2', on_hover='hover for a2', value='a2', correct=None)
   checkbox_option_a = Option(text='b1', on_hover='hover for b1', value='b1', correct=None)
   checkbox_option_b = Option(text='b2', on_hover='hover for b2', value='b2', correct=None)
   radio = RadioGroup(options=[option_a, option_a2])
   checkbox = CheckboxGroup(options=[option_b, option_b2])

.. _text_box:

Text Box
--------

.. automodule:: opencrowd.model.section.text_box
   :members:

.. raw:: html
   :file: ../../_static/_sections/text_box/text_box_rendering.html
