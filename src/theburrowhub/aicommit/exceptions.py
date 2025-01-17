class DiffIsZeroLen(Exception):
    def __init__(self):
        super().__init__('git diff is empty')


class MessageIsEmpty(Exception):
    def __init__(self):
        super().__init__('commit message is empty')
