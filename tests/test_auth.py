import pytest
from flask import g, session

from recipemod.db import get_db

def test_register(client, app):
	assert client.get('/auth/register').status_code == 200