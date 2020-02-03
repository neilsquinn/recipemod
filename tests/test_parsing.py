import os
import urllib

import pytest
import requests

from recipemod import parsing    

def url_to_filepath(url):
    url_split = urllib.parse.urlsplit(url) 
    return url_split.netloc + url_split.path.replace('/', '_')

def test_same_keys(recipe, target):
    assert recipe.keys() == target.keys()
    