import pytest


def soma(x,y):
    return x + y


def test_answer():
    assert soma(3,2) == 5