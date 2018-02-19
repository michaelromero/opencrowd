

class Response(object):
    def __init__(self, assignment):
        self.assignment = assignment

    def dump(self):
        raise NotImplementedError


class Default(Response):
    def __init__(self, assignment):
        super(Default, self).__init__(assignment)

    def dump(self):
        return self.assignment.__dict__


class AnswersOnly(Response):
    def __init__(self, assignment):
        super(AnswersOnly, self).__init__(assignment)

    def dump(self):
        return self.assignment['Answer']
