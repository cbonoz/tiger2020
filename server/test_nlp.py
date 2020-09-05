import pytest
from tigernlp import generate_gsql


EXAMPLE_1 = "I have a graph called Bankworld. A person has an account at a bank. A bank has an name and location. A person has a string name and datetime birthday."

EXAMPLE_2 = f"""
Person is a person who participates in a forum.
A person has a birthday datetime and a name.
Forum is a place where persons discuss topics.
Company and University are organizations with which a person can be affiliated.
Comment and Post are the interaction messages created by a person in a forum.
A comments lives in a forum
A person studies at a university.
A person works at a company.
Tag is a topic or a concept.
TagClass is a class or a category. 
TagClass are a hierarchy of tags.
"""

EXAMPLE_3 = f"""
A person can know another person
"""

EXAMPLE_4 = "A person has a datetime amount. A person has an int birthyear."

def test_generate_gsql_empty():
    run_test('', '')

def test_generate_gsql_basic():
    run_test(EXAMPLE_1)


def test_generate_gsql_var():
    run_test(EXAMPLE_2)

def test_generate_gsql_undirected():
    run_test(EXAMPLE_3)

def test_generate_gsql_type():
    run_test(EXAMPLE_4)


def run_test(input_text, expected=None):
    code, reasons = generate_gsql(input_text)
    print(code)
    print(reasons)
    # assert code == expected # TODO: add check.
