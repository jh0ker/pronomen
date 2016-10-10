

"""Parses the JSON pronoun database. Do not look at the code, you will regret it."""

try:
    import ujson as json
except ImportError:
    import json

from os.path import join, splitext, split
from os import walk
import os
import re

from pprint import pprint

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

JSON_DIR = join(CURRENT_DIR, 'json')

SCHEMA_DIR = join(JSON_DIR, 'schema')
PART_DIR = join(SCHEMA_DIR, 'partial')

META_DIR = join(JSON_DIR, 'metadata')

OBJECT_ROOT = join(JSON_DIR, 'instance')


def load_files(pronouns):

    for root, dirs, files in walk(OBJECT_ROOT):

        for file in files:
            object_path = join(
                *root.split(os.sep)[len(CURRENT_DIR.split(os.sep)) + 2:],
                splitext(file)[0]
            )

            print("Loading", object_path)

            with open(join(root, file), 'r') as fp:
                pronouns[object_path] = json.load(fp)


def resolve_references(pronouns):
    resolved = 0

    for object_path in sorted(pronouns, key=lambda k: -k.count(os.sep)):

        for key, value in pronouns[object_path].items():
            if key == "children" or key == 'questions':
                for i, reference in enumerate(value[:]):
                    if isinstance(reference, str):
                        if reference.startswith('/'):
                            target = pronouns[reference[1:]]
                        else:
                            target = pronouns[join(split(object_path)[0], reference)]

                        value[i] = target
                        resolved += 1

    return resolved


def assign_metadata(pronouns, metadata, path):
    if isinstance(pronouns, dict) and 'type' in pronouns.keys():
        if isinstance(pronouns['type'], list):
            path.append(pronouns['type'][0])
        else:
            path.append(pronouns['type'])

        meta = metadata

        for node in path:
            meta = meta[node]

        pronouns['metadata'] = meta

    if isinstance(pronouns, dict) and 'children' in pronouns.keys():
        for entry in pronouns['children']:
            assign_metadata(entry, metadata, path[:])


def load_metadata(pronouns):
    metadata = dict()

    for root, dirs, files in walk(META_DIR):
        for file in files:
            with open(join(root, file)) as fp:
                metadata_version = splitext(file)[0].partition('.')[2]
                metadata[metadata_version] = json.load(fp)

    for pronoun in pronouns.values():
        assign_metadata(pronoun, metadata['0.1'], list())


def convert(markdown):

    urls_p = r'~(?P<text>.+?)~'
    urls_s = r'<i>\g<text></i>'
    markdown = re.sub(urls_p, urls_s, markdown)

    urls_p = r'=(?P<text>.+?)='
    urls_s = r'<b>\g<text></b>'
    markdown = re.sub(urls_p, urls_s, markdown)

    urls_p = r'\[(?P<text>.+?)\]\((?P<url>.+?)\)'
    urls_s = r'<a href="\g<url>">\g<text></a>'
    markdown = re.sub(urls_p, urls_s, markdown)

    markdown = markdown.replace(' -- ', ' – ')

    return markdown


def parse_markdown(pronouns):
    if isinstance(pronouns, str):
        return

    for k in pronouns.keys():
        if isinstance(pronouns[k], str):
            pronouns[k] = convert(pronouns[k])
        elif isinstance(pronouns[k], list):
            for entry in pronouns[k]:
                parse_markdown(entry)
        elif isinstance(pronouns[k], dict):
            parse_markdown(pronouns[k])


def parse_pronouns():
    pronouns = dict()

    load_files(pronouns)

    while resolve_references(pronouns):
        pass

    # Clean up dictionary
    for key in list(pronouns.keys()):
        if '/' in key:
            del pronouns[key]

    # pprint(pronouns)

    load_metadata(pronouns)

    parse_markdown(pronouns)

    return pronouns
