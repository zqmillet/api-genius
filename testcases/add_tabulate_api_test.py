from pytest import mark

from . import User

@mark.create_tables(models=[User])
def test_create_api_swagger_with_specified_path(database_engine, application, client):
    application.add_create_api(database_engine=database_engine, path='/user/{user_id}')(User)

    schema = client.openapi['paths']['/user/{user_id}']['post']['requestBody']['content']['application/json']['schema']
    assert schema['required'] == ['company_id', 'department_id', 'name']

    properties = schema['properties']
    assert properties['role'] == {
        'allOf': [
            {
                'title': 'Role',
                'enum': ['admin', 'user'],
                'type': 'string',
                'description': 'An enumeration.'
            }
        ],
        'default': 'user',
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
        'type': 'string',
        'maxLength': 50,
    }

    assert properties['department_id'] == {
        'example': 'paas',
        'maxLength': 50,
        'title': 'the unique id of department',
        'type': 'string'
    }

    assert properties['company_id'] == {
        'example': 'huawei',
        'maxLength': 50,
        'title': 'the unique id of company',
        'type': 'string'
    }

    assert 'create_time' not in properties

    assert client.openapi['paths']['/user/{user_id}']['post']['parameters'] == [
        {
            'example': 'j19260817',
            'in': 'path',
            'name': 'user_id',
            'required': True,
            'schema': {'title': 'the unique id of user', 'type': 'string', 'maxLength': 50}
        }
    ]

@mark.create_tables(models=[User])
def test_create_api_swagger_with_default_path(database_engine, application, client):
    application.add_create_api(database_engine=database_engine)(User)
    schema = client.openapi['paths']['/users/{company_id}/{department_id}/{user_id}']['post']['requestBody']['content']['application/json']['schema']

    assert schema['required'] == ['name']
    assert 'create_time' not in schema['properties']
    assert client.openapi['paths']['/users/{company_id}/{department_id}/{user_id}']['post']['parameters'] == [
        {
            'example': 'huawei',
            'in': 'path',
            'name': 'company_id',
            'required': True,
            'schema': {'maxLength': 50, 'title': 'the unique id of company', 'type': 'string'}
        },
        {
            'example': 'paas',
            'in': 'path',
            'name': 'department_id',
            'required': True,
            'schema': {'maxLength': 50, 'title': 'the unique id of department', 'type': 'string'}
        },
        {
            'example': 'j19260817',
            'in': 'path',
            'name': 'user_id',
            'required': True,
            'schema': {'maxLength': 50, 'title': 'the unique id of user', 'type': 'string'}
        }
    ]
