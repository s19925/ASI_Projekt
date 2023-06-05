from os.path import isfile

import pandas as pd

from kedro.io import AbstractDataSet
from typing import Any, Dict


class PythonCSV(AbstractDataSet):
    def __init__(
        self,
        filepath: str,
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
    ):
        self._filepath = filepath
        self._load_args = load_args if load_args is not None else {}
        self._save_args = save_args if save_args is not None else {}

    def _load(self) -> Any:
        return pd.read_csv(self._filepath, **self._load_args)

    def _save(self, data: Any) -> None:
        return data.to_csv(self._filepath, **self._save_args)

    def _describe(self) -> Dict[str, Any]:
        return self.__dict__

    def _exists(self) -> bool:
        return isfile(self._filepath)