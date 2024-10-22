#!/usr/bin/env python3
'''Task 8's module.
'''


def list_all(mongo_collection):
    '''Lists all documents in a collection.
    '''
    if mongo_collection:
        return list(mongo_collection.find())
    return []
