import importlib
import json
import random
import re
from datetime import datetime
import string
import types
from lusid_drive.configuration import Configuration
from lusid_drive.extensions.api_client import SyncApiClient
import pytest
from wiremock.server import WireMockServer
from wiremock.constants import Config
from wiremock.client import Mapping, Mappings, MappingRequest, MappingResponse, Requests
from polyfactory.factories.pydantic_factory import ModelFactory
import inspect


@pytest.fixture(scope="session")
def wiremock_server():
    with WireMockServer() as wm:
        Config.base_url = f'http://localhost:{wm.port}/__admin'
        yield wm


def test_verify_endpoints(wiremock_server):
    with open("/Users/charlie/repos/lusid-sdk-generator-python/generate/.output/sdk/swagger.json", "r") as file:
        json_str = file.read()
    openapi_data = json.loads(json_str)
    for path in openapi_data["paths"]:
        for operation in openapi_data["paths"][path]:
            operation_data = openapi_data["paths"][path][operation]
            tag = operation_data["tags"][0]
            operation_id = operation_data["operationId"]
            
            print(f"{operation} {path} ({operation_id}) for {tag}")
            
            responses = operation_data["responses"]
            successful_response_code = -1
            for code in responses:
                try:
                    response_code = int(code)
                    if response_code >= 200 and response_code < 300:
                        successful_response_code = response_code
                        break
                except ValueError:
                    pass
            response_data = responses[f"{successful_response_code}"]
            is_binary_response = False
            if "content" in response_data:
                content = get_content(response_data["content"])
                if "schema" in content and "format" in content["schema"] and content["schema"]["format"] == "binary":
                    is_binary_response = True
                response = get_example_from_content(content)
                if isinstance(response, bytes):
                    Mappings.create_mapping(
                        Mapping(
                            request=MappingRequest(),
                            response=MappingResponse(status=response_code, data=response),
                            persistent=False,
                        )
                    )
                elif safe_getattr(response, 'to_dict'):
                    dict_obj = response.to_dict()
                    # make the below recursive and cover all cases
                    for key in dict_obj:
                        item = dict_obj[key]
                        if isinstance(item, list):
                            for list_item in item:
                                if isinstance(list_item, dict):
                                    for inner_key in list_item:
                                        inner_item = list_item[inner_key]
                                        if isinstance(inner_item, datetime):
                                            string_datetime = inner_item.isoformat()
                                            list_item[inner_key] = string_datetime
                                elif isinstance(item, datetime):
                                    string_datetime = item.isoformat()
                                    dict_obj[key] = string_datetime
                        elif isinstance(item, datetime):
                            string_datetime = item.isoformat()
                            dict_obj[key] = string_datetime
                    Mappings.create_mapping(
                        Mapping(
                            request=MappingRequest(),
                            response=MappingResponse(status=response_code, json_body=dict_obj),
                            persistent=False,
                        )
                    )
                else:
                    Mappings.create_mapping(
                        Mapping(
                            request=MappingRequest(),
                            response=MappingResponse(status=response_code, json_body=response),
                            persistent=False,
                        )
                    )
            else:
                response = None
                Mappings.create_mapping(
                    Mapping(
                        request=MappingRequest(),
                        response=MappingResponse(status=response_code),
                        persistent=False,
                    )
                )
            
            request_body_example = None
                        
            if "requestBody" in operation_data:
                content = get_content(operation_data["requestBody"]["content"])
                request_body_example = get_example_from_content(content)
            
            if request_body_example:
                print(f"request body: '{request_body_example}'")
            
            arguments = {}
            if "parameters" in operation_data:
                for parameter_data in operation_data["parameters"]:
                    name = parameter_data["name"]
                    parameter_kind = parameter_data["in"]
                    if parameter_kind == "header" and name == "Content-Length":
                        example = len(request_body_example)
                    elif "example" in parameter_data:
                        example = parameter_data["example"]
                    elif "examples" in parameter_data:
                        example = parameter_data[0]
                    else:
                        example = get_default_for_type_and_format(parameter_data["schema"])
                    arguments[name] = (parameter_kind, example)
                    
                for argument in arguments:
                    print(f"- {argument}: ({arguments[argument][0]},{arguments[argument][1]})")
            
            module_name = f"lusid_drive.api.{re.sub(' ', '_', tag).lower()}_api"
            class_name = f"{re.sub(' ', '', tag)}Api"
            method_name = to_snake_case(operation_id)
            kwargs = {to_snake_case(arg):arguments[arg][1] for arg in arguments}
            base_url = f"http://localhost:{wiremock_server.port}"
            Requests.reset_request_journal()
            returned_response = invoke_method(base_url, module_name, class_name, method_name, request_body_example, **kwargs)
            if response == None:
                assert returned_response == None
            elif hasattr(returned_response, 'to_dict') and callable(getattr(returned_response, 'to_dict')):
                returned_response_dict = returned_response.to_dict()
                response_type = type(response)
                if safe_getattr(response_type, 'to_dict'):
                    response_dict = response.to_dict()
                    for item in response_dict:
                        assert item in returned_response_dict
                        if (isinstance(returned_response_dict[item], datetime)):
                            date_from_string = datetime.fromisoformat(response_dict[item])
                            assert returned_response_dict[item] == date_from_string
                        else:
                            assert returned_response_dict[item] == response_dict[item]
                else:
                    for item in response:
                        assert item in returned_response_dict
                        if (isinstance(returned_response_dict[item], datetime)):
                            date_from_string = datetime.fromisoformat(response[item])
                            assert returned_response_dict[item] == date_from_string
                        else:
                            assert returned_response_dict[item] == response[item]
            elif is_binary_response:
                assert str(returned_response) == 'b\'"' + response + '"\''
            else:
                assert returned_response == response
                
            requests = Requests.get_all_received_requests()
            assert len(requests["requests"]) == 1
            request = requests["requests"][0].request
            
            # TODO - check these are as expected
            headers = request.headers
            query_parameters = request.query_parameters
            method = request.method
            body = request.body
            url = request.url
            
            Requests.reset_request_journal()

            Mappings.delete_all_mappings()

def get_content(content_data):
    if isinstance(content_data, dict):
        content_key = list(content_data.keys())[0]
        return content_data[content_key]
    else:
        return content_data[0]
        
def get_example_from_content(content):
    schema = content["schema"]
    if "$ref" in schema:
        ref = schema["$ref"]
        parts = [part for part in ref.split("/") if part != "#"]
        schema_def_name = parts[len(parts) - 1]
        if "example" in content:
            return content["example"]
        elif "examples" in content:
            return content[0]
        else:
            return get_default_for_type(schema_def_name)
    else:
        if "example" in content:
            return content["example"]
        elif "examples" in content:
            return content[0]
        else:
            return get_default_for_type_and_format(schema)
        
def invoke_method(base_url, module_name, class_name, method_name, request_body, **kwargs):
    module = __import__(module_name, fromlist=[class_name])
    cls = getattr(module, class_name)
    configuration = Configuration(host=base_url)
    api_client = SyncApiClient(configuration=configuration)
    instance = cls(api_client)
    method = getattr(instance, method_name)
    if request_body:
        signature = inspect.signature(method)
        values = signature.parameters.values()
        parameter_name = [param.name for param in values if param.name not in kwargs.keys()][0]
        kwargs[parameter_name] = request_body
    return method(**kwargs)

def get_default_for_type_and_format(schema):
    type = schema["type"]
    format = schema["format"] if "format" in schema else None
    min_length = schema["minLength"] if "minLength" in schema else 1
    max_length = schema["maxLength"] if "maxLength" in schema else 10
    # will get errors from wiremock that the uri is too long if don't do below
    if max_length > 100:
        max_length = 100
                    
    # format
    if format == "binary":
        return generate_random_string(min_length, max_length)
    if format == "byte":
        return generate_random_string(min_length, max_length).encode('utf-8')
    
    # type
    if type == "string":
        return generate_random_string(min_length, max_length)
    if type == "integer":
        return generate_random_integer(min_length, max_length)
    if type == "array":
        return []
    if type == "boolean":
        return True
    
    raise Exception("not implemented")

def get_default_for_type(class_name):
    for i in range(0, 20):
        example = generate_pydantic_type_example(class_name)
        if len(example.values) > 0:
            return example
    raise Exception(f"unable to generate valid type for '{class_name}'")

def generate_random_string(min_length, max_length):
    length = random.randint(min_length, max_length)
    characters = string.ascii_letters + string.digits
    things = [random.choice(characters) for _ in range(length)]
    return ''.join(things)

def generate_random_integer(min_length, max_length):
    length = random.randint(min_length, max_length)
    if length == 1:
        return random.randint(0, 9)  # Handle single-digit case separately
    else:
        return random.randint(10**(length-1), 10**length - 1)

def to_snake_case(input: str):
    if "-" in input:
        return re.sub(r'-', '_', input).lower()
    return re.sub(r'(?<!^)(?=[A-Z])', '_', input).lower()

def generate_pydantic_type_example(class_name: str):
    snake_cased_name = to_snake_case(class_name)
    module_name = f"lusid_drive.models.{snake_cased_name}"
    module = importlib.import_module(module_name)
    class_type = getattr(module, class_name)
    polyfactory = types.new_class(f"{class_type}Factory", (ModelFactory[class_type],), {})
    polyfactory.__randomize_collection_length__ = True
    polyfactory.__min_collection_length__ = 1
    polyfactory.__max_collection_length__ = 5
    polyfactory.__allow_none_optionals__ = False
    return polyfactory.build(factory_use_construct=True)

def safe_getattr(obj, name):
    try:
        return getattr(obj, name)
    except Exception:
        return False
