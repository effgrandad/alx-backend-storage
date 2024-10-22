#!/usr/bin/env python3

"""
modify all topics of a school document
"""


def update_topics(mongo_collection, name, topics):
    """
    straightforward function that modifies a document's values
    """
    filter_ = {
        "name": name
    }

    new_topics = {
        "$set": {
            "topics": topics
        }
    }
    return mongo_collection.update_many(filter_, new_topics)
