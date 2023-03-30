aws cloudformation create-stack  --stack-name orderich-prod-vpc --template-url "https://orderich-templates.s3.eu-central-1.amazonaws.com/prod/public-vpc.yml" --capabilities CAPABILITY_NAMED_IAM
aws cloudformation create-stack  --stack-name orderich-prod-task --template-url "https://orderich-templates.s3.eu-central-1.amazonaws.com/prod/public-service.yml" --capabilities CAPABILITY_NAMED_IAM

aws s3 sync ./staging s3://orderich-templates/staging --delete --acl public-read --profile orderich && \
aws s3 sync ./prod s3://orderich-templates/prod --delete --acl public-read --profile orderich && \
aws s3 sync ./config s3://orderich-templates/config --profile orderich
