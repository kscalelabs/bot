"""Defines the AWS components for the application."""

import json

import pulumi_aws as aws

from bot.settings import settings

# ------------ #
#     VPCs     #
# ------------ #


def get_vpc(key: str) -> aws.ec2.Vpc:
    return aws.ec2.Vpc(
        f"dpsh-vpc-{key}",
        cidr_block="10.0.0.0/16",
        tags={
            "Project": "dpsh",
            "Environment": key,
        },
    )


dev_vpc = get_vpc("dev")
prod_vpc = get_vpc("prod")

# ------------ #
#   Databases  #
# ------------ #


def get_db_instance(key: str, instance_class: str, max_allocated_storage: int | None = None) -> aws.rds.Instance:
    return aws.rds.Instance(
        f"{key}_rds",
        allocated_storage=20,
        max_allocated_storage=max_allocated_storage,
        engine="postgres",
        engine_version="13.3",
        instance_class=instance_class,
        name=f"dpsh-{key}-db",
        username="postgres",
        manage_master_user_password=True,
        skip_final_snapshot=True,
        tags={
            "Project": "dpsh",
            "Environment": key,
        },
    )


dev_rds = get_db_instance("dev", "db.t3.micro")
prod_rds = get_db_instance("prod", "db.t4g.2xlarge")

# ------------ #
#      IAM     #
# ------------ #


def get_iam_role(key: str) -> aws.iam.Role:
    return aws.iam.Role(
        f"dpsh-eb-ec2-role-{key}",
        assume_role_policy=json.dums(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Sid": "",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                    },
                ],
            },
        ),
        tags={
            "Project": "dpsh",
            "Environment": key,
        },
    )


dev_iam_role = get_iam_role("dev")
prod_iam_role = get_iam_role("prod")

# ------------ #
#   Security   #
# ------------ #


def get_security_group(key: str, vpc: aws.ec2.Vpc) -> aws.ec2.SecurityGroup:
    return aws.ec2.SxecurityGroup(
        description="Allow resources inside the VPC to communicate with RDS instance",
    )


dev_security_group = get_security_group("dev", dev_vpc)
prod_security_group = get_security_group("prod", prod_vpc)


def get_security_group_rule(
    key: str,
    security_group: aws.ec2.SecurityGroup,
    protocol: str,
    from_port: int,
    to_port: int,
    cidr_blocks: list[str],
) -> aws.ec2.SecurityGroupRule:
    return aws.ec2.SecurityGroupRule(
        f"dpsh-{key}-sg-rule",
        security_group_id=security_group.id,
        protocol=protocol,
        from_port=from_port,
        to_port=to_port,
        cidr_blocks=cidr_blocks,
        type="ingress",
    )


dev_security_group_rule = get_security_group_rule("dev", dev_security_group, "tcp", 5432, 5432, ["0.0.0.0/0"])
prod_security_group_rule = get_security_group_rule("prod", prod_security_group, "tcp", 5432, 5432, ["0.0.0.0/0"])


eb_app = aws.elasticbeanstalk.Application(
    resource_name="dpsh-app",
    description="The application for the DPSH project",
)

eb_env = aws.elasticbeanstalk.Environment(
    resource_name="dpsh-env",
    application=eb_app.name,
    solution_stack_name="64bit Amazon Linux 2 v5.4.6 running Python 3.8",
    instance_profile=instance_profile.name,
    setting=[
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            name="RDS_DB_NAME",
            value=settings.database.postgres.database,
        ),
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            name="RDS_HOSTNAME",
            value=rds.address,
        ),
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            name="RDS_PASSWORD",
            value=settings.database.postgres.password,
        ),
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            name="RDS_PORT",
            value=settings.database.postgres.port,
        ),
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            name="RDS_USERNAME",
            value=settings.database.postgres.username,
        ),
    ],
    tags={"Name": "dpsh-env"},
)
