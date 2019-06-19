import json


def build_template(config, stream):
    template_object = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "tc-integrations\nSample SAM Template for tc-integrations\n",
        "Globals": {
            "Function": {
                "Environment": {"Variables": generate_environmental_variables(config)},
                "Timeout": 3,
            }
        },
        "Outputs": generate_outputs(config),
        "Resources": generate_resources(config),
        "Transform": "AWS::Serverless-2016-10-31",
    }
    json.dump(template_object, stream, indent=2, sort_keys=True)


def generate_environmental_variables(config, **defaults):
    functions = config["Functions"]
    env_vars = {"TC_THIS_BUCKET": {"Ref": "ResultBucket"}}
    for function in functions:
        env_vars[f"TC_{function.upper()}_QUEUE"] = {"Ref": f"{function}Sqs"}
        env_vars[f"TC_{function.upper()}_BUCKET"] = {"Ref": f"ResultBucket"}
    env_vars.update(defaults)
    return env_vars


def generate_outputs(config):
    functions = config["Functions"]
    return {
        f"{function}Queue": {"Description": "SQSUrl", "Value": f"{function}Sqs"}
        for function in functions
    }


def generate_resources(config):
    functions = config["Functions"]

    resources = {}
    resources["ResultBucket"] = {
        "Properties": {
            "LifecycleConfiguration": {
                "Rules": [
                    {
                        "ExpirationInDays": "30",
                        "Id": "RemoveAfter30Days",
                        "Status": "Enabled",
                    }
                ]
            }
        },
        "Type": "AWS::S3::Bucket",
    }

    resources["LambdaRole"] = generate_lambda_role(config)

    for function, function_data in functions.items():
        resources.update(
            {
                function: {
                    "Properties": generate_function_properties(function, function_data),
                    "Type": "AWS::Serverless::Function",
                },
                f"{function}Sqs": {
                    "Properties": {"VisibilityTimeout": function_data.get("Timeout")},
                    "Type": "AWS::SQS::Queue",
                },
                f"{function}SqsMapping": {
                    "Properties": {
                        "BatchSize": function_data.get("BatchSize", 1),
                        "Enabled": "true",
                        "EventSourceArn": {"Fn::GetAtt": [f"{function}Sqs", "Arn"]},
                        "FunctionName": {"Fn::GetAtt": [function, "Arn"]},
                    },
                    "Type": "AWS::Lambda::EventSourceMapping",
                },
            }
        )
    return resources


def generate_lambda_role(config):
    functions = config["Functions"]
    policy_statements = [
        {"Action": ["cloudwatch:PutMetricData"], "Effect": "Allow", "Resource": "*"},
        {
            "Action": ["xray:PutTraceSegments", "xray:PutTelemetryRecords"],
            "Effect": "Allow",
            "Resource": "*",
        },
        {"Action": ["logs:*"], "Effect": "Allow", "Resource": "arn:aws:logs:*:*:*"},
        {
            "Action": [
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
                "sqs:ChangeMessageVisibility",
            ],
            "Effect": "Allow",
            "Resource": [
                {"Fn::GetAtt": [f"{function}Sqs", "Arn"]} for function in functions
            ],
        },
        {
            "Action": ["s3:*"],
            "Effect": "Allow",
            "Resource": [
                {"Fn::GetAtt": ["ResultBucket", "Arn"]},
                {"Fn::Join": ["/", [{"Fn::GetAtt": ["ResultBucket", "Arn"]}, "*"]]},
            ],
        },
    ]

    policy_statements.extend(config.get("ExtraPolicies", []))

    return {
        "Properties": {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": ["sts:AssumeRole"],
                        "Effect": "Allow",
                        "Principal": {"Service": ["lambda.amazonaws.com"]},
                    }
                ],
                "Version": "2012-10-17",
            },
            "Policies": [
                {
                    "PolicyDocument": {
                        "Statement": policy_statements,
                        "Version": "2012-10-17",
                    },
                    "PolicyName": "allowLambdaLogs",
                }
            ],
        },
        "Type": "AWS::IAM::Role",
    }


def generate_function_properties(function, function_data):
    properties = {
        "CodeUri": function_data.get("CodeUri"),
        "Environment": {
            "Variables": generate_function_environmental_variables(
                function, function_data
            )
        },
        "Handler": function_data.get("Handler"),
        "MemorySize": function_data.get("MemorySize"),
        "Role": {"Fn::GetAtt": ["LambdaRole", "Arn"]},
        "Runtime": "python3.7",
        "Timeout": function_data.get("Timeout"),
        "Tracing": "Active" if function_data.get("Tracing") else "PassThrough",
    }
    if function_data.get("ReservedConcurrentExecutions") is not None:
        properties["ReservedConcurrentExecutions"] = function_data.get(
            "ReservedConcurrentExecutions"
        )
    if function_data.get("Events"):
        properties["Events"] = {}
        for event_name, event_data in function_data["Events"].items():
            properties["Events"][event_name] = {
                "Type": "Schedule",
                "Properties": {
                    "Schedule": event_data.get("Schedule"),
                    "Input": json.dumps({"function": event_data.get("Function")}),
                },
            }
    return properties


def generate_function_environmental_variables(function, function_data):
    env_vars = {"TC_THIS_QUEUE": {"Ref": f"{function}Sqs"}}
    env_vars.update(function_data.get("Environment", {}))
    return env_vars
