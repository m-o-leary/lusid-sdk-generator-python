#!/bin/bash -e

if [[ ${#1} -eq 0 ]]; then
    echo
    echo "[ERROR] generate folder file path not specified"
    exit 1
fi

if [[ ${#2} -eq 0 ]]; then
    echo
    echo "[ERROR] output folder file path not specified"
    exit 1
fi

if [[ ${#3} -eq 0 ]]; then
    echo
    echo "[ERROR] swagger file not specified"
    exit 1
fi

gen_root=$1
output_folder=$2
swagger_file=$3
config_file_name=$4
sdk_output_folder=$output_folder/sdk

if [[ -z $config_file_name || ! -f $gen_root/$config_file_name ]] ; then
    echo "[INFO] '$config_file_name' not found, using default config.json"
    config_file_name=.config.json
fi

echo "[INFO] root generation : $gen_root"
echo "[INFO] output folder   : $output_folder"
echo "[INFO] swagger file    : $swagger_file"
echo "[INFO] config file     : $config_file_name"

ignore_file_name=.openapi-generator-ignore
config_file=$gen_root/$config_file_name
ignore_file=$output_folder/$ignore_file_name

app_name=$(cat $config_file | jq -r .packageName)

#   remove all previously generated files
shopt -s extglob
echo "[INFO] removing previous sdk: $sdk_output_folder"
rm -rf $sdk_output_folder/$app_name/!(utilities|tcp)
shopt -u extglob

# ignore files
mkdir -p $sdk_output_folder
cp $ignore_file $sdk_output_folder

# sdk_version=$(cat $swagger_file | jq -r '.info.version')
# sdk_version=${PACKAGE_VERSION}
# cat $config_file | jq -r --arg SDK_VERSION "$sdk_version" '.packageVersion |= $SDK_VERSION' > temp && mv temp $config_file

# remove the verbose description
cat $swagger_file | jq -r '.info.description |= "FINBOURNE Technology"' > $sdk_output_folder/swagger.json

echo "[INFO] generating sdk version: ${PACKAGE_VERSION}"

# generate the SDK
java ${JAVA_OPTS} -jar /opt/openapi-generator/modules/openapi-generator-cli/target/openapi-generator-cli.jar generate \
    -i $sdk_output_folder/swagger.json \
    -g python-nextgen \
    -o $sdk_output_folder \
    -t $gen_root/templates \
    -c $config_file

    # enable the following if a manual override is required
    # --skip-validate-spec

# create a version file
cat << EOF > $sdk_output_folder/$app_name/__version__.py
__version__ = "$sdk_version"
EOF

rm -rf $sdk_output_folder/.openapi-generator/
rm -rf $sdk_output_folder/test/
rm -f $sdk_output_folder/.gitlab-ci.yml $sdk_output_folder/setup.cfg
rm -f $sdk_output_folder/.openapi-generator-ignore
rm -f $sdk_output_folder/swagger.json
rm -rf $sdk_output_folder/.github/
# rm -f $output_folder/.openapi-generator-ignore

mkdir -p $output_folder/docs
cp -R /tmp/docs/docs/* $output_folder/docs
mkdir -p $output_folder/.github/
cp -R /tmp/workflows/github/* $output_folder/.github/
touch $sdk_output_folder/$app_name/py.typed
