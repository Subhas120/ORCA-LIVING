from copy import deepcopy


CONTEXT_FIELDS = [
    "location",
    "destination",
    "date",
    "time",
    "activity",
]


class ConversationContext:

    def __init__(self):
        self._state = {
            field: None
            for field in CONTEXT_FIELDS
        }

    def update(self, entities: dict) -> dict:

        for field in CONTEXT_FIELDS:

            value = entities.get(field)

            if value is not None and value != "":
                self._state[field] = value

        return self.get()

    def get(self) -> dict:
        return deepcopy(self._state)

    def fill_missing(
        self,
        entities: dict,
    ) -> dict:

        result = {}

        for field in CONTEXT_FIELDS:

            current_value = entities.get(field)

            if current_value is not None and current_value != "":
                result[field] = current_value
            else:
                result[field] = self._state[field]

        return result

    def clear(self) -> None:

        for field in CONTEXT_FIELDS:
            self._state[field] = None
