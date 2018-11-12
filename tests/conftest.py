import os
import pytest
import json

from dictionaryutils import DataDictionary, dictionary

MOD_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def init_dictionary():
    datadictionary = DataDictionary(root_dir=os.path.join(MOD_DIR, 'schemas'))
    dictionary.init(datadictionary)
