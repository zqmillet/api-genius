from pytest import mark

from . import User

@mark.create_tables(models=[User])
def test_create_api_swagger(database_engine, application, client):
    application.add_create_api(database_engine=database_engine, path='/user/{user_id}')(User)

    properties = client.openapi['paths']['/user/{user_id}']['post']['requestBody']['content']['application/json']['schema']['properties']

    assert properties['role'] == {
        'allOf': [
            {
                'title': 'Role',
                'enum': ['admin', 'user'],
                'type': 'string',
                'description': 'An enumeration.'
            }
        ],
        'example': 'user',
        'title': 'the role of user'
    }

    assert properties['age'] == {
        'example': 99,
        'title': 'the age of user',
        'type': 'integer',
        'maximum': 100.0,
        'minimum': 18.0
    }

    assert properties['name'] == {
        'example': 'zhangbaohua',
        'title': 'the name of user',
        'type': 'string'
    }

    assert properties['department_id'] == {
        'example': 'paas',
        'title': 'the unique id of department',
        'type': 'string'
    }

    assert properties['company_id'] == {
        'example': 'huawei',
        'title': 'the unique id of company',
        'type': 'string'
    }

    assert client.openapi['paths']['/user/{user_id}']['post']['parameters'] == [
        {
            'example': 'j19260817',
            'in': 'path',
            'name': 'user_id',
            'required': True,
            'schema': {'title': 'the unique id of user', 'type': 'string'}
        }
    ]
