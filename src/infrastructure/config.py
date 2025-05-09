import os
from dotenv import load_dotenv

load_dotenv()

def get_env(var, default=None):
    value = os.getenv(var, default)
    if value is None:
        raise ValueError(f"Variável de ambiente ausente: {var}")
    return value 