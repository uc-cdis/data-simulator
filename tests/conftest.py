import os
import pytest

from dictionaryutils import DataDictionary, dictionary

MOD_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def default_dictionary():
    datadictionary = DataDictionary(root_dir=os.path.join(MOD_DIR, "schemas/default"))
    dictionary.init(datadictionary)
