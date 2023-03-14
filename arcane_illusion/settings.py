from dataclasses import dataclass, asdict, field
from typing import TypeVar

try:
    from PyQt5.QtCore import QSettings
except:
    class QSettings(dict):
        IniFormat = None
        UserScope = None

        def __init__(self, *_) -> None:
            super().__init__()

        def contains(self, key):
            return self.__contains__(key)

        def setValue(self, key, value):
            self.__setitem__(key, value)

        def value(self, key, type):
            return self.get(key)

try:
    from .constants import KRITA_NAME, EXTENSION_ID
except:
    KRITA_NAME, EXTENSION_ID = (None, None)

T = TypeVar("T")

_settings = QSettings(QSettings.IniFormat, QSettings.UserScope, KRITA_NAME, EXTENSION_ID)


class _Base:
    def as_dict(self):
        return asdict(self)

    def save(self):
        d = self.as_dict()
        for key in d.keys():
            value = getattr(self, key)
            _settings.setValue(key, value)

    def load(self):
        annotations = self.__annotations__
        d = self.as_dict()
        for key in d.keys():
            if _settings.contains(key):
                value = _settings.value(key, type=annotations[key])
                setattr(self, key, value)


@dataclass
class Options(_Base):
    url: str = field(default="http://localhost:7860")


@dataclass
class Parameters(_Base):
    sd_model: str = field(default=None)
    prompt: str = field(default="")
    negative_prompt: str = field(default="")
    sampler: str = field(default=None)
    steps: int = field(default=20)
    width: int = field(default=512)
    height: int = field(default=512)
    seed: int = field(default=-1)
    cfg_scale: float = field(default=7)


if __name__ == "__main__":
    import code

    code.interact(local=locals())
