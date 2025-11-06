from abc import ABC, abstractmethod
from typing import List

class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> list[list[float]]:
        ...
