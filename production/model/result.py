import json


class Result:
    def __init__(self, status, message):
        self.status = status  # 实例变量
        self.message = message  # 实例变量

    def to_json(self):
        return json.dumps(self.__dict__)