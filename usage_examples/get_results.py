import json
from opencrowd.model.server import Opencrowd

opencrowd = Opencrowd.regenerate()

responses = []
for assignment in opencrowd.get_assignment_objects():
    responses.append(opencrowd.generate_response(assignment))
for response in responses:
    print(json.dumps(response.dump(), indent=5))
