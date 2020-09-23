from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
    aws_lambda_event_sources as lambda_event_source,
    core
)


class CdkDemoStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Creates Queue
        requestqueue = sqs.Queue(
            self, "RequestsQueue",
            visibility_timeout=core.Duration.seconds(300),
        )

        # Create DDB Table
        requests_table = ddb.Table(
            self, "requests_table",
            partition_key=ddb.Attribute(
                name="id",
                type=ddb.AttributeType.STRING
            )
        )

        # Defines an AWS Lambda resource
        hello_lambda = _lambda.Function(
            self, 'HelloHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda'),
            handler='hello.handler',
        )

        # Adds DN Table as env
        hello_lambda.add_environment("TABLE_NAME", requests_table.table_name)

        # grant permission to lambda to write to demo table
        requests_table.grant_write_data(hello_lambda)

        # SQS Event Source for Lambda
        sqs_event_source = lambda_event_source.SqsEventSource(requestqueue)

        # SQS event source to Function
        hello_lambda.add_event_source(sqs_event_source)

        