from enum import Enum


class Model(Enum):
    Gpt3 = "gpt-3.5-turbo-16k"
    Gpt4 = "gpt-4"


CONTEXT_SIZE = {
    Model.Gpt3: 16 * 1024,
    Model.Gpt4: 8 * 1024,
}
