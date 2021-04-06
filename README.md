# Local-s3-app

This project is a Kata for clean coding with AWS Serverless Application Model.

Kata projects have the following requirements at the time of this writing:

- To demonstrate clean code practice
- To follow strict type-checking 
- To have full unit-test coverage
- To have full integration testing coverage
- To follow strict access and security policies
- To have automated scripts for set up and tear down

# Development environment

This Kata was developed with
- IntelliJ Idea, Ultimate version, 2020.3.3
- Python 3.9
- Python Plugin 203.7717.81
- AWS Plugin 1.25-33

The information in this Readme file is edited from the auto-generated Readme which was created using the
```sam init``` command

[boot3-stubs](https://pypi.org/project/boto3-stubs/) package was installed to allow for
autocomplete and type matching in the IDE

# Kata Scenario

The lambda in this scenario returns all objects in an S3 bucket.

- It expects the bucket name to be in the `event.queryStringParameters`
  - otherwise, it will return a 400 (bad request) complaining about missing bucket name
  - If the bucket does not exist, it returns a 404 (not found) complaining about the bucket not present
  - If the bucket is not accessible, it returns a 403 (not authorized) complaining about lack of access
- If the bucket can be queried successfully, it will be returned via the json response.
- Otherwise, an error will be returned.

# Unit and Integration Testing

The Kata sets up and tears down its own testing environment. This means that the Kata will create all resources
it needs for testing its scenarios on the fly, then destroys them on exit.

- For Unit tests
  - The ```mock``` and ```moto``` libraries are used to mock the s3 resource usage in the lambda file
  - The ```setUp()``` function is used to create a bucket in mocked s3 resource, create some files and upload it
    at the start of each test
  - The ```tearDown()``` function is used to delete the files and the bucket at the end of each test.


- For Integration tests:
  - The ```setUpClass()``` class method is used to create the files and the bucket, whose name is read from the
  environment variable, at the start of the test suite. this means the bucket will be created only once for all tests.
    - Such approach is needed because tests can run close to each other, and if the buckets keeps being created and deleted, the next test may fail.
  - The ```tearDownClass()``` class method is used to remove the files and the bucket when all tests are done.
  - The ```setUp()``` method is used to get the endpoint for the lambda to call at each test.
  
# Project files 

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- get_s3_objects - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit and Integration tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

# Running the unit tests

Unit tests can run without deploying the application. To run unit tests, first install the requirements for
each test:

```bash
local-s3-app$ pip install -r tests/requirements.txt --user
```

From that point, you can run the tests from the command line. For example, a CI/CD tool, can run the unit tests using
the following command

```bash
# unit test
local-s3-app$ PYTHONPATH=".:/usr/local/lib/python3.9/site-packages:$PYTHONPATH" /usr/local/bin/python3.9 tests/unit/test_handler.py
```

This will ensure that the current directory is searched for required files and modules, however based on the operating
system or the directory structure, the above command may require some editing. for example, in some operating systems,
paths are separated by ```;``` instead of ```:```

Please note that recent versions of python are required to support strict type checking and mocking.

# Debugging the application in the IDE

In the case of IntelliJ Idea, directly form inside the IDE. This allows you to put breakpoints in Lambda and inspect
local variables and other state information.


# Building the application


Build your application with the `sam build --use-container` command.

```bash
local-s3-app$ sam build --use-container
```

The SAM CLI installs dependencies defined in `get_s3_objects/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.

# Deploying Locally

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
local-s3-app$ sam local invoke GetS3ObjectsFunction --event events/event.json
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
local-s3-app$ sam local start-api
local-s3-app$ curl http://localhost:3000/
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        GetS3ObjectsAPI:
          Type: Api
          Properties:
            Path: /GetS3Objects
            Method: get
```



# Deploying the application to the cloud

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your 
application to AWS.

If you are using a specific profile, you need to add that to the end of the ```deploy``` command:

```bash
sam deploy --guided --profile myprofile
```

Guided deployment presents a series of prompts:


* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

So, assuming the stack-name was local-s3-app, you will get the logs like this:

```bash
local-s3-app$ sam logs -n GetS3ObjectsFunction --stack-name local-s3-app --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Integration Tests

Once your application is deployed, integration tests can run with the following command

```bash
# integration test, requiring deploying the stack first.
local-s3-app$ AWS_SAM_STACK_NAME=<stack-name> AWS_DEFAULT_REGION=<region> AWS_PROFILE=<profile> BUCKET_NAME=<bucketName> python -m pytest tests/integration -v
```
- The `AWS_SAM_STACK_NAME` is the name of the stack you used to deploy your app. you will use this to get logs, add resources, and clean up.
- The `AWS_DEFAULT_REGION` is the region in which you have deployed the stack. 
- The `AWS_PROFILE` is optional, in case you would use a non-default profile for deployment
- The `BUCKET_NAME` is specific to this Kata and is a name of bucket to create for tests. it should start with `s3kata`. it will be destroyed when the tests are done.
  
`NOTE` that since the bucket is created on the fly, it will be a private bucket. for the lambda to access that, we need to have a policy
  this policy is set in the template file, as shown below:
  
```yaml
Policies:
  - S3ReadPolicy:
      BucketName: s3kata*
```
This means that the bucket name for integration tests should start with `s3kata`


## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name <stack-name>
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

