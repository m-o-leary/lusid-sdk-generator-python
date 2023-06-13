![LUSID_by_Finbourne](https://content.finbourne.com/LUSID_repo.png)

This repository contains the generation and publishing logic for each of the LUSID SDKs currently there are SDKs for:
- Python
- Java
- Javascript (Typescript)
- CSharp

## Contributing

We welcome contributions from our community. See our [contributing guide](docs/CONTRIBUTING.md) for information on how to contribute to the LUSID SDK Generators repository.
## Generate

### Prerequisites

In order to generate an sdk, you will need to have:
* Docker; installed and running
* [just](https://github.com/casey/just#installation) installed and available in your path
* [envsubst](https://www.gnu.org/software/gettext/manual/html_node/envsubst-Invocation.html) part of the gnu gettext tools should be installed and available in your path.

### Generating
If you would like to generate an SDK using a custom swagger.json file, please do the following:

1) Ensure that you have already checked out the project that you want to generate an SDK for e.g. https://github.com/finbourne/lusid-sdk-python
2) Execute `just generate` in this directory; you can use `just generate-local` if you don't want to supply a previous sdk directory - output will be in `generate/.output`

    You may preceed `just generate` or `just generate-local` with `just get-swagger` or `just --set swagger_url="https://my-domain.lusid.com/api/swagger/v0/swagger.json" get-swagger` to get the swagger file for your your custom LUSID domain. This command creates a swagger.json in the current directory which is excluded in the `.gitignore` file.
    
Some examples of generating a python SDK for LUSID:

1. for the default domain
```
# get the current swagger.json for LUSID
just get-swagger

# generate the SDK
just generate-local

# examine the output
ls generate/.output
```

2. for a specific domain, output to a pre-cloned git repository
```
# clone the repo
git clone git@github.com:finbourne/lusid-sdk-python-preview.git ../lusid-sdk-python

# get the current swagger.json from a specific domain
just --set swagger_url="https://specific-domain.lusid.com/api/swagger/v0/swagger.json" get-swagger

# generate the SDK
just generate ../lusid-sdk-python

# examine the output
ls ../lusid-sdk-python
```

----

If you would like to modify the way that the SDK is generated you can edit the `justfile`, `generate/generate.sh`, `generate/config-template.json` or `generate/.openapi-generator-ignore` files to suit your needs.

These are also used in the pipeline so if you would like to update the way the SDK is generated in there you need to commit your changes and raise a merge request.

### Templates

We've changed the default templates that they use because they didn't do exactly what we wanted. These templates live in the `generate/templates directory.

The initial templates that we edited are in the `generate/default_templates` directory. You can also find all the default templates on [github](https://github.com/OpenAPITools/openapi-generator/tree/master/modules/openapi-generator/src/main/resources/python-nextgen).

## Publish

If you would like to publish a generated SDK, please do the following:

1) Ensure that you have already checked out the project that you want to publish an SDK for e.g. https://github.com/finbourne/lusid-sdk-csharp
2) If publishing a new SDK, ensure that you have already generated the SDK following the instructions above and set the version to have your initials at the end e.g. `0.10.705-MM`. You will
want to ensure the version is set in the appropriate file e.g. package.json, __version__.py etc. and in the swagger file you used to generate the SDK
2) Navigate to the `/all/publish` directory in the lusid-sdk-generators (this) repo
3) Run the publish.sh script passing in the following variables

    a) The name of the language that you would like to generate the SDK for e.g. `python`. Options are:

        - javascript
        - python
        - csharp
        - java

    b) The folder of your project from which the SDK should be published, this should be one level above the sdk folder e.g. `../../../projects/lusid-sdk-python`

    c) The API key or password for publishing to a remote repository

    d) The URL or name of the remote repository to publish to e.g. `https://hosted_package_manager_url`.

    A command might look something like this `sh publish.sh python ../../../lusid-sdk-python abc_secret_api_key https://hosted_package_manager_url`

    P.S. Please note you will need Docker installed and running to use the publish.sh script
----

If you would like to modify the way that the SDK is published you can edit the `publish.sh` files to suit your needs.

These are also used in the pipeline so if you would like to update the way the SDK is published in there you need to commit your changes and raise a merge request.
