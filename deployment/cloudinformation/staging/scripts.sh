aws cloudformation create-stack  --stack-name orderich-staging-vpc --template-url "https://orderich-templates.s3.eu-central-1.amazonaws.com/staging/public-vpc.yml" --capabilities CAPABILITY_NAMED_IAM
aws cloudformation create-stack  --stack-name orderich-staging-task --template-url "https://orderich-templates.s3.eu-central-1.amazonaws.com/staging/public-service.yml" --capabilities CAPABILITY_NAMED_IAM

aws s3 sync ./staging s3://orderich-templates/staging --delete --acl public-read && \
aws s3 sync ./prod s3://orderich-templates/prod --delete --acl public-read && \
aws s3 sync ./config s3://orderich-templates/config
