from enum import Enum
from app_config import config


class Model(Enum):
    Gpt3 = "gpt-3.5-turbo-16k"
    Gpt4 = "gpt-4"
    AZURE_GPT4 = config.azure_gpt4_deployment_name
    Mistral = "mistral"
    Mixtral = "mixtral"
    Fusion_Net = "fusion_net"


class ModelType(Enum):
    GPTQ = "GPTQ"
    GGUF = "GGUF"


CONTEXT_SIZE = {
    Model.Gpt3: 16 * 1024,
    Model.Gpt4: 8 * 1024,
    Model.AZURE_GPT4: 8 * 1024,
    Model.Mistral: 8 * 1024,
    Model.Mixtral: 8 * 1024,
    Model.Fusion_Net: 8 * 1024,
}
