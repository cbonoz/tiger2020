from enum import Enum

import spacy

from stop_words import STOP_WORDS

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")


class ObjectType(str, Enum):
    VERTEX = 'vertex'
    EDGE = 'edge'


class EdgeType(str, Enum):
    UNDIRECTED = 'undirected'
    DIRECTED = 'directed'


class PropertyType(str, Enum):
    INT = 'int'
    UINT = 'uint'
    FLOAT = 'float'
    DOUBLE = 'double'
    STRING = 'string'
    BOOL = 'bool'
    DATE_TIME = 'datetime'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

# ex: CREATE VERTEX Company (PRIMARY_ID id UINT, name STRING, url STRING) WITH primary_id_as_attribute="TRUE"


def create_vertex(name, **kwargs):
    kwargs.pop('type')
    prop_str = ', '.join([f"{k[1:]} {kwargs[k].upper()}" for k in kwargs])
    if prop_str:
        prop_str = ', ' + prop_str
    return f"CREATE VERTEX {name.capitalize()} (PRIMARY_ID id UINT{prop_str}) WITH primary_id_as_attribute=\"TRUE\""

# ex: CREATE DIRECTED EDGE HAS_TAG (FROM Comment|Post|Forum, TO Tag) WITH REVERSE_EDGE="HAS_TAG_REVERSE"


def create_edge(verb, from_list, to_list, is_directed=True, **kwargs):
    directed_str = 'DIRECTED' if is_directed else 'UNDIRECTED'
    from_str = '|'.join(from_list)
    to_str = '|'.join(to_list)
    return f"CREATE {directed_str} EDGE {verb} (FROM {from_str}, TO {to_str}) WITH REVERSE_EDGE=\"{verb}_REVERSE\""


def create_graph(graph_name):
    if not graph_name:
        return ""
    return f"// Create graph type.\nCREATE GRAPH {graph_name} (*)"


def create_gsql(graph_name=None, vertices=[], edges=[]):
    vertex_commands = '\n'.join([create_vertex(**v) for v in vertices])
    edge_commands = '\n'.join([create_edge(**e) for e in edges])
    graph_command = create_graph(graph_name)
    return f"""
// Clear the current catalog.
DROP ALL

// Create vertex types.
{vertex_commands}

// Create edge types.
{edge_commands}

{graph_command}
    """


GRAPH_NAMING_WORDS = set(['named', 'called'])

# https://spacy.io/usage/linguistic-features


def generate_gsql(text: str):
    doc = nlp(text)

    data = {
        'graph_name': None,
        'vertices': [],
        'edges': []
    }
    reasons = []
    objects = {}

    def add_edge(verb, from_list, to_list):
        if verb in objects:
            from_list.extend(objects[verb]['from_list'])
            from_list = list(set(from_list))
            to_list.extend(objects[verb]['to_list'])
            to_list = list(set(to_list))

        objects[verb] = {
            'type': ObjectType.EDGE,
            'verb': verb,
            'from_list': from_list,
            'to_list': to_list
        }

    for i, sentence in enumerate(doc.sents):
        sentence_doc = nlp(sentence.string)
        print('\nNext sentence\n')
        type_map = {}
        last_dobj = {}
        last_verb = None
        last_subject = None
        subject = {}
        for j, token in enumerate(sentence_doc):
            word = token.lemma_
            if word.lower() in STOP_WORDS:
                continue

            obj = None
            token_children = [str(child) for child in token.children]
            print(word, token.dep_, token.head.text, token.head.pos_, token_children)
            raw_word = word
            word = word.lower().capitalize()
            if token.head.text in GRAPH_NAMING_WORDS and token.dep_ == 'oprd':
                data['graph_name'] = raw_word
                reasons.append('We detected the graph name ' + word)
                objects = {}
                # if last_dobj:
                #     del objects[last_dobj['name']]
            elif token.dep_ == 'nsubj' or token.dep_ == 'nsubjpass':
                obj = {
                    'type': ObjectType.VERTEX,
                    'name': word
                }

                if token.head.pos_ == 'VERB':
                    last_verb = token.head.text
                    last_subject = word

                if word == '-pron-':
                    continue

                subject = obj
                reasons.append(
                    f"Adding {word} as a vertex since it appeared as a sentence subject")
            elif token.dep_ == 'pobj':
                obj = {
                    'type': ObjectType.VERTEX,
                    'name': word
                }
                if 'name' in last_dobj or last_verb:
                    edge = last_dobj.get('name', last_verb)
                    # action = 'is' if last_verb else 'has'
                    verb = edge.upper()
                    add_edge(verb, [subject['name']], [token.text.capitalize()])
                    reasons.append(
                        f"We reclassified {edge.capitalize()} as an edge since it appeared as a predicate object for another vertex")

                    if subject:
                        objects[subject['name']].pop(f"~{edge}", None)
            elif token.dep_ == 'dobj' or token.dep_ == 'prep':
                is_naming = set(token_children).intersection(
                    GRAPH_NAMING_WORDS)
                # print('is_naming', is_naming, token_children, GRAPH_NAMING_WORDS)
                if is_naming and not data['graph_name']:
                    # Skip if we don't have a graph name yet and this is a name clause
                    continue
                last_dobj = {
                    'type': ObjectType.VERTEX,
                    'name': word
                }
                print('dobj', token.head.pos_, token.lemma_, objects)
                if token.head.text == 'has' and subject.get('name') in objects:
                    subject_name = subject.get('name')
                    objects[subject_name][f"~{raw_word}"] = type_map.get(raw_word, PropertyType.STRING)
                elif token.dep_ == 'dobj':
                    obj = last_dobj
                    reasons.append(
                        f"Adding {word} as a vertex since it is a direct object")

                # Check for possible edge.
                if token.head.pos_ == 'VERB' and last_subject:
                    target = last_subject.capitalize()
                    if target:
                        verb = token.head.text.upper()
                        add_edge(verb, [target], [word])
                        reason = f"""Adding {verb} an edge between {word} and {target}"""
                        reasons.append(reason)
            elif token.dep_ in ['compound', 'amod'] and PropertyType.has_value(word.lower()):
                target = token.head.text
                type_map[target] = word.lower()
                print('setting type', target, word)
            elif token.dep_ == 'conj' and subject.get('name') in objects:
                print('adding type', raw_word, type_map)
                objects[subject['name']][f"~{raw_word}"] = type_map.get(raw_word, PropertyType.STRING)

            if obj and obj['name'] not in objects:
                objects[obj['name']] = obj

    print('\nobjects', objects)

    for d in objects.values():
        print('adding', d)
        if d['type'] == ObjectType.VERTEX:
            data['vertices'].append(d)
        elif d['type'] == ObjectType.EDGE:
            data['edges'].append(d)

    print('\ndata', data)

    has_data = (len(data['edges']) + len(data['vertices'])) > 0
    if has_data:
        code = create_gsql(data['graph_name'], data['vertices'], data['edges'])
    else:
        code = 'Keep typing...'

    return code, list(set(reasons))


if __name__ == '__main__':
    print(STOP_WORDS)
