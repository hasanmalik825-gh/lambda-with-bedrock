1. create lambda function on aws console and use from scratch.
2. paste app.py code in lambda_function.py and deploy it.
3. create api gateway of HTTP API, configure routes as post, define stages like dev, prod (optional) and then connect API to lambda function.
4. create s3 bucket with the name as s3_bucket variable in app.py
5. make sure to give proper permissions to lambda function to access s3 bucket and other resources.
6. create a testing.ipynb file and test the API of lambda function.
