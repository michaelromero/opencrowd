import jinja2
from . import section

from opencrowd.config.opencrowd import TEMPLATES_DIR


class InputGroup(section.Section):
    def __init__(self, input_type, opencrowd_id=None, options=None, hidden=False):
        super(InputGroup, self).__init__(opencrowd_id, hidden)
        self.input_type = input_type
        # convert options to ids
        if options is None:
            options = list()
        if len(options):
            self.option_ids = [option.opencrowd_id for option in options]
            for option in options:
                option.save()

    def to_json(self):
        json_obj = {'type': 'InputGroup',
                    'options': [option_id for option_id in self.option_ids],
                    'input_type': self.input_type,
                    'hidden': self.hidden}

        json_obj.update(super(InputGroup, self).to_json())
        return json_obj

    # def get_load_function(self):
    #     env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
    #     env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + self.get_type())
    #     template = env.get_template('load.js')
    #     return template.render()

    def render(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "InputGroup")
        template = env.get_template('InputGroup.html')
        return template.render(InputGroup=self)

    def add_option(self, option):
        self.option_ids.append(option.opencrowd_id)
        option.save()

    def call_save_function(self):
        return "saveInputs(current_answer);"

    def dynamicGenerateGraphLogic(self):
        return "if (node.type == \"InputGroup\") {\n\
            var html_template = generate_inputgroup(node, root_id);\n\
            $(\"#\"+anchor_id).after(html_template);\n\
        }"

    def staticGenerateGraphLogic(self):
        env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        env.loader = jinja2.FileSystemLoader(TEMPLATES_DIR + 'section/' + "InputGroup")
        template = env.get_template('graph.js')
        return template.render()


class RadioGroup(InputGroup):
    """
    Create and manage a new RadioGroup section. Options are buttons that can be optionally loaded on init.
    A RadioGroup is composed of Options, which are the HTML buttons. In this case, they're radio buttons.

    :param options: list of option sections
    :type options: list of Option sections
    """

    def __init__(self, opencrowd_id=None, hidden=False, options=None):
        super(RadioGroup, self).__init__('radio', opencrowd_id, options, hidden)


class CheckboxGroup(InputGroup):
    """
    Create and manage a new CheckboxGroup section. Options are buttons that can be optionally loaded on init.
    A CheckboxGroup is composed of Options, which are HTML buttons. In this case, they're checkbox buttons.

    :param options: list of option sections
    :type options: list of Option sections
    """

    def __init__(self, opencrowd_id=None, hidden=False, options=None):
        super(CheckboxGroup, self).__init__('checkbox', opencrowd_id, options, hidden)


class Option(section.Section):
    """
    Create and manage a new Option section. Options are the building blocks of InputGroups (Checkbox and Radio). Each
    Option corresponds to a button that will be rendered within the InputGroup.

    :param text: list of option sections
    :type text: list of Option sections
    :param on_hover: list of option sections
    :type on_hover: list of Option sections
    :param value: list of option sections
    :type value: list of Option sections
    :param correct: if this answer is deemed "correct", which is used in later analysis of workers
    :type correct: bool
    :param children: will make the child section appear if this button is clicked, and render a new DAG according to that sections children
    :type children: list of Sections
    """

    def __init__(self, opencrowd_id=None, hidden=False, text='', on_hover='', value='', correct=None, children=None):
        super(Option, self).__init__(opencrowd_id, hidden)
        if children is None:
            children = list()
        self.text = text
        self.on_hover = on_hover
        self.value = value
        self.correct = correct
        if type(children) is not list:
            children = [children]
        self.children = children  # links to next sections if necessary

    def add_children(self, child):
        """
        Create and manage a new Option section. Options are the building blocks of InputGroups (Checkbox and Radio). Each
        Option corresponds to a button that will be rendered within the InputGroup.

        :param child: the child to add
        :type child: Section

        .. code-block:: python

            # in this example, we display an image that we know has a shower
            # we displayed a textbox to ask the user if there is a shower
            # the user is supposed to select 'Yes', which is correct.
            # After selecting yes, the showerbutton has a child named bathroom checkbox group
            # which further asks the user if the shower has other attributes

            shower_button = Option(text='Yes', on_hover='The image doesn't have a shower', value='shower', correct=True)
            no_shower_button = Option(text='No', on_hover='The image does have a shower', value='no_shower', correct=None)

            shower_radio_group = RadioGroup(options=[shower_button, no_shower_button])
            bathroom_checkbox_group = CheckboxGroup(options=[spout_checkbox, tub_checkbox])

            shower_button.add_children(bathroom_checkbox_group)


        """

        self.children.append(child.opencrowd_id)
        self.save()

    def to_json(self):
        json_obj = {'text': self.text,
                    'on_hover': self.on_hover,
                    'value': self.value,
                    'children': self.children}

        json_obj.update(super(Option, self).to_json())
        return json_obj
