from typing import List
from pydantic import BaseModel
import yaml


class Config(BaseModel):
    name: str
    version: str
    pages: List[str]
    routes: List[str]


def load_config(file_path: str) -> Config:
    with open(file_path, 'r') as file:
        yaml_content = yaml.safe_load(file)
    return Config(**yaml_content)
