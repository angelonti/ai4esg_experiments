from enum import Enum
from config import config


class Model(Enum):
    Gpt3 = "gpt-3.5-turbo-16k"
    Gpt4 = config.gpt4_deployment_name


CONTEXT_SIZE = {
    Model.Gpt3: 16 * 1024,
    Model.Gpt4: 8 * 1024,
}
