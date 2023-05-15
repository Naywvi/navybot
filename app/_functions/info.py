import json
class informations:
    def __init__(self) -> None:
        with open('./src/config/config.json', 'r') as f:
            self.data = json.load(f)