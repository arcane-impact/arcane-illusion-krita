from dataclasses import dataclass
from typing import List


@dataclass()
class GenerationResponse:
    images: List[str]
    parameters: dict
    info: str


@dataclass()
class ProgressResponse:
    progress: float
    eta_relative: float
