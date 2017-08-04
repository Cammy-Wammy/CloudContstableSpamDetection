## How to Deploy

### Create Docker container with all dependencies
In the docker folder run (replace cammywammy with your own docker hub account):
- docker login
- docker build -t emailclassifier-image .
- docker tag emailclassifier-image cammywammy/emailclassifier-image
- docker push cammywammy/emailclassifier-image

### Deploy the code to OpenWhisk
In the deploy-pkg folder run:
- wsk action create score-email --docker cammywammy/emailclassifier-image classifier.zip
Test with (may take a wee bit of time to deploy, so you may need to reun the test a few times):
- wsk action invoke score-email --param text "Hello world, this is the sample email contents to test" -b
