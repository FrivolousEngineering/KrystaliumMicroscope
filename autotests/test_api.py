import pytest
import json

import krystalium.api as api


def test_jsonapi_object():
    json_string = """
    {
        "meta": {
            "count": 0,
            "totalPages": 0
        },
        "jsonapi": {
            "version": "1.0"
        },
        "data": {
            "id": "0",
            "type": "effect",
            "attributes": {
                "name": "string",
                "action": "increasing",
                "target": "solid",
                "strength": 0
            },
            "relationships": {}
        }
    }
    """

    jsonapi = api.JsonApiObject.from_json(json.loads(json_string))
    assert jsonapi.id == "0"
    assert jsonapi.attributes.name == "string"
    assert jsonapi.attributes.action == "increasing"
    assert jsonapi.attributes.target == "solid"
    assert jsonapi.attributes.strength == 0

    json_string = """
    {
        "meta": {
            "count": 0,
            "totalPages": 0
        },
        "jsonapi": {
            "version": "1.0"
        },
        "data": {
            "id": "string",
            "type": "blood",
            "attributes": {
                "rfid_id": "string",
                "strength": 0
            },
            "relationships": {
                "effect": {
                    "data": {
                        "id": "1",
                        "type": "effect"
                    }
                }
            }
        },
        "included": [
            {
                "id": "1",
                "type": "effect",
                "attributes": {
                    "name": "string",
                    "action": "increasing",
                    "target": "solid",
                    "strength": 0
                },
                "relationships": {}
            }
        ]
    }
    """

    jsonapi = api.JsonApiObject.from_json(json.loads(json_string))

    assert jsonapi.relationships.effect == {"data": {"id": "1", "type": "effect"}}
    assert jsonapi.included[0].id == "1"

def test_effect():
    json_string = """
    {
        "data": {
            "id": "0",
            "type": "effect",
            "attributes": {
                "name": "string",
                "action": "increasing",
                "target": "solid",
                "strength": 0
            },
            "relationships": {}
        }
    }
    """

    jsonapi = api.JsonApiObject.from_json(json.loads(json_string))
    effect = api.Effect.from_jsonapi(jsonapi)

    assert effect.id == 0
    assert effect.name == "string"
    assert effect.action == "increasing"
    assert effect.target == "solid"

def test_bloodsample():
    json_string = """
    {
        "data": {
            "id": "0",
            "type": "blood",
            "attributes": {
                "rfid_id": "string",
                "strength": 0
            },
            "relationships": {
                "effect": {
                    "data": {
                        "id": "1",
                        "type": "effect"
                    }
                }
            }
        },
        "included": [
            {
                "id": "1",
                "type": "effect",
                "attributes": {
                    "name": "string",
                    "action": "increasing",
                    "target": "solid",
                    "strength": 0
                },
                "relationships": {}
            }
        ]
    }
    """

    jsonapi = api.JsonApiObject.from_json(json.loads(json_string))
    sample = api.BloodSample.from_jsonapi(jsonapi)

    assert sample.id == 0
    assert sample.effect.name == "string"

def test_enlisted():
    json_string = """
    {
        "data": {
            "id": "0",
            "type": "enlisted",
            "attributes": {
                "name": "string",
                "number": "string"
            },
            "relationships": {
                "effects": {
                    "data": [
                        {
                            "id": "1",
                            "type": "effect"
                        },
                        {
                            "id": "2",
                            "type": "effect"
                        }
                    ]
                }
            }
        },
        "included": [
            {
                "id": "1",
                "type": "effect",
                "attributes": {
                    "name": "first",
                    "action": "increasing",
                    "target": "solid",
                    "strength": 0
                },
                "relationships": {}
            },
            {
                "id": "2",
                "type": "effect",
                "attributes": {
                    "name": "second",
                    "action": "decreasing",
                    "target": "liquid",
                    "strength": 2
                }
            }
        ]
    }
    """

    jsonapi = api.JsonApiObject.from_json(json.loads(json_string))
    enlisted = api.Enlisted.from_jsonapi(jsonapi)

    assert enlisted.id == 0
    assert enlisted.name == "string"
    assert len(enlisted.effects) == 2
