aws s3 sync ./staging s3://orderich-templates/staging --delete --acl public-read --profile orderich && \
aws s3 sync ./prod s3://orderich-templates/prod --delete --acl public-read --profile orderich && \
aws s3 sync ./config s3://orderich-templates/config --profile orderich
