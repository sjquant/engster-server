#!/bin/bash

set -u
set -x

package_dir="$(poetry env info --path)/lib/python3.8/site-packages"
project_dir=$PWD
zip_excludes=("*.exe" "*.DS_Store" "*.Python" \
"*.git" ".git/*" "*.zip" "*.tar.gz" "*.hg" "pip/*" \
"docutils/*" "setuputils/*" "**/__pycache__/*" "__pycache__/*" \
"poetry/*" "black/*" "flake8/*" "rope/*" "awscli/*" \
"_pytest/*" "pytest/*" "virtualenv/*")

echo "Packaging proeject..."
cd $package_dir && zip -r9 $project_dir/lambda.zip . -x "${zip_excludes[@]}"
cd $project_dir && zip -g -r $project_dir/lambda.zip app main.py
echo "Packaging done!"

# upload to S3
function_name="engsterAPI"
bucket="engster-api"
aws s3 cp $project_dir/lambda.zip s3://$bucket/lambda.zip
aws lambda update-function-code --function-name $function_name --s3-bucket $bucket --s3-key lambda.zip