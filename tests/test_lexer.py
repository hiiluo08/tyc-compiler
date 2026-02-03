"""
Lexer test cases for TyC compiler
TODO: Implement 100 test cases for lexer
"""

import pytest
from tests.utils import Tokenizer


def test_001():
    source = """\t\r\n
    /* This is a block comment so // has no meaning here */
    // VOTIEN
"""
    expected = "EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_002():
    source = "@"
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token @"

def test_003():
    source = "auto auto1"
    expected = "auto,auto1,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_004():
    source = "+ ++"
    expected = "+,++,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_005():
    source = "votien123"
    expected = "votien123,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_006():
    source = "0   100   255   2500   -45"
    expected = "0,100,255,2500,-45,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_007():
    source = "0.0   3.14   -2.5   1.23e4   5.67E-2   1.   .5"
    expected = "0.0,3.14,-2,.5,1.23e4,5.67E-2,1.,.5,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_008():
    source = """
    "This is a string containing tab \\t"
    "He asked me: \\"Where is John?\\""
"""
    expected = "This is a string containing tab \\t,He asked me: \\\"Where is John?\\\",EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_009():
    source = """
    "This is a string \n containing tab \\t"
"""
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: This is a string \n"
    
def test_010():
    source = """
    "This is a string \\z containing tab \\t"
"""
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Illegal Escape In String: This is a string \\z"
        
        
def test_023():
    source = "000 -000 0123 -00502"
    expected = "000,-000,0123,-00502,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected
        
def test_086():
    source = "["
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token ["
