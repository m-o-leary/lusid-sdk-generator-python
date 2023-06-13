export PACKAGE_NAME := `echo ${PACKAGE_NAME:-lusid}`
export PROJECT_NAME := `echo ${PROJECT_NAME:-lusid-sdk}`
export PACKAGE_VERSION := `echo ${PACKAGE_VERSION:-2.0.0}`

export PYPI_PACKAGE_LOCATION := `echo ${PYPI_PACKAGE_LOCATION:-~/.pypi/packages}`

swagger_path := "./swagger.json"

swagger_url := "https://example.lusid.com/api/swagger/v0/swagger.json"

get-swagger:
    echo {{swagger_url}}
    curl -s {{swagger_url}} > swagger.json

build-docker-images: 
    docker build -t lusid-sdk-gen-python:latest --ssh default=$SSH_AUTH_SOCK -f Dockerfile generate
    docker build -t lusid-sdk-pub-python:latest -f publish/Dockerfile publish

generate-local:
    mkdir -p /tmp/${PROJECT_NAME}_${PACKAGE_VERSION}
    envsubst < generate/config-template.json > generate/.config.json
    docker run \
        -e JAVA_OPTS="-Dlog.level=error" \
        -e PACKAGE_VERSION=${PACKAGE_VERSION} \
        -v $(pwd)/generate/:/usr/src/generate/ \
        -v $(pwd)/generate/.openapi-generator-ignore:/usr/src/generate/.output/.openapi-generator-ignore \
        -v $(pwd)/{{swagger_path}}:/tmp/swagger.json \
        lusid-sdk-gen-python:latest -- ./generate/generate.sh ./generate ./generate/.output /tmp/swagger.json .config.json
    rm -f generate/.output/.openapi-generator-ignore
    docker run \
        -v $(pwd)/generate/.output:/usr/src \
        lusid-sdk-pub-python:latest -- "cd sdk; poetry add --group dev lusidfeature"

    docker run \
        -v $(pwd)/generate/.output:/usr/src \
        lusid-sdk-pub-python:latest -- "cd sdk; poetry install"
    
generate TARGET_DIR:
    @just generate-local
    
    # need to remove the created content before copying over the top of it.
    # this prevents deleted content from hanging around indefinitely.
    rm -rf {{TARGET_DIR}}/sdk/lusid
    rm -rf {{TARGET_DIR}}/sdk/docs
    
    cp -R generate/.output/* {{TARGET_DIR}}

publish-only-local:
    docker run \
        -v $(pwd)/generate/.output:/usr/src \
        lusid-sdk-pub-python:latest -- "cd sdk; poetry build"
    mkdir -p ${PYPI_PACKAGE_LOCATION}
    cp generate/.output/sdk/dist/* ${PYPI_PACKAGE_LOCATION}

publish-only:
    docker run \
        -e POETRY_PYPI_TOKEN_PYPI:${PYPI_TOKEN} \
        -v $(pwd)/generate/.output:/usr/src \
        lusid-sdk-pub-python:latest -- "cd sdk; poetry publish"

generate-and-publish TARGET_DIR:
    @just generate {{TARGET_DIR}}
    @just publish-only

generate-and-publish-local:
    @just generate-local
    @just publish-only-local

test:
    ./test/test.sh
