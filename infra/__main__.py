"""Defines the AWS components for the application."""

import pulumi
import pulumi_aws as aws

# ------------------ #
#       Config       #
# ------------------ #

config = pulumi.Config()

env = config.require("key")

# Database parameters.
db_username = config.require("db_username")
db_password = config.require_secret("db_password")
db_instance_class = config.require("db_instance_class")
db_allocated_storage = config.require("db_allocated_storage")
db_max_allocated_storage = config.require("db_max_allocated_storage")
db_skip_final_snapshot = config.require_bool("db_skip_final_snapshot")

# API parameters.
api_instance_type = config.require("api_instance_type")
api_ami = config.require("api_ami")
min_num_api_instances = config.require("min_num_api_instances")
max_num_api_instances = config.require("max_num_api_instances")

# Worker parameters.
worker_instance_type = config.require("worker_instance_type")
worker_ami = config.require("worker_ami")
min_num_worker_instances = config.require("min_num_worker_instances")
max_num_worker_instances = config.require("max_num_worker_instances")

# ------------------ #
#         VPC        #
# ------------------ #

vpc = aws.ec2.Vpc(
    "DpshVpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Project": "dpsh", "Environment": env, "Name": f"{env.upper()} VPC"},
)

internet_gateway = aws.ec2.InternetGateway(
    "DpshInternetGateway",
    vpc_id=vpc.id,
    tags={"Project": "dpsh", "Environment": env, "Name": f"{env.upper()} Internet Gateway"},
)

# ------------------ #
#      Subnets       #
# ------------------ #


def get_subnet(key: str, i: int, az: str) -> tuple[aws.ec2.Subnet, int]:
    letter = az[-1]
    subnet = aws.ec2.Subnet(
        f"Dpsh{key.capitalize()}Subnet{letter.upper()}",
        cidr_block=f"10.0.{i}.0/24",
        vpc_id=vpc.id,
        availability_zone=az,
    )
    return subnet, i + 1


i = 0
api_subnet_a, i = get_subnet("api", i, "us-east-1a")
api_subnet_b, i = get_subnet("api", i, "us-east-1b")
api_subnet_c, i = get_subnet("api", i, "us-east-1c")
api_subnet_d, i = get_subnet("api", i, "us-east-1d")
api_subnet_e, i = get_subnet("api", i, "us-east-1e")
api_subnet_f, i = get_subnet("api", i, "us-east-1f")
api_subnet_ids = [api_subnet_a.id, api_subnet_b.id, api_subnet_c.id, api_subnet_d.id, api_subnet_e.id, api_subnet_f.id]

gpu_subnet_a, i = get_subnet("gpu", i, "us-east-1a")
gpu_subnet_b, i = get_subnet("gpu", i, "us-east-1b")
gpu_subnet_c, i = get_subnet("gpu", i, "us-east-1c")
gpu_subnet_d, i = get_subnet("gpu", i, "us-east-1d")
gpu_subnet_f, i = get_subnet("gpu", i, "us-east-1f")
gpu_subnet_ids = [gpu_subnet_a.id, gpu_subnet_b.id, gpu_subnet_c.id, gpu_subnet_d.id, gpu_subnet_f.id]

db_subnet = aws.rds.SubnetGroup("DpshDBSubnet", subnet_ids=api_subnet_ids + gpu_subnet_ids, name="db-subnet")

# ------------------ #
#  Security Groups   #
# ------------------ #

api_sg = aws.ec2.SecurityGroup(
    "DpshApiSecurityGroup",
    description="Allow the API to be accessed from the internet.",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(protocol="tcp", from_port=80, to_port=80, cidr_blocks=["0.0.0.0/0"]),
        aws.ec2.SecurityGroupIngressArgs(protocol="tcp", from_port=443, to_port=443, cidr_blocks=["0.0.0.0/0"]),
    ],
    tags={"Project": "dpsh", "Environment": env, "Name": f"{env.upper()} API Security Group"},
)

gpu_sg = aws.ec2.SecurityGroup(
    "DpshGpuSecurityGroup",
    description="Allow the GPU instances to communicate with the API, and vice versa",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(protocol="tcp", from_port=80, to_port=80, security_groups=[api_sg.id]),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(protocol="tcp", from_port=80, to_port=80, security_groups=[api_sg.id]),
    ],
    tags={"Project": "dpsh", "Environment": env, "Name": f"{env.upper()} GPU Security Group"},
)

db_sg = aws.ec2.SecurityGroup(
    "DpshDatabaseSecurityGroup",
    description="Allow the API to communicate with the database",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=5432,
            to_port=5432,
            security_groups=[api_sg.id, gpu_sg.id],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="tcp",
            from_port=5432,
            to_port=5432,
            security_groups=[api_sg.id, gpu_sg.id],
        ),
    ],
    tags={"Project": "dpsh", "Environment": env, "Name": f"{env.upper()} Database Security Group"},
)

# ------------------ #
#         S3         #
# ------------------ #

s3_bucket = aws.s3.Bucket(
    f"DpshData{env.capitalize()}",
    acl="private",
    bucket=f"dpsh-data-{env}",
    tags={"Project": "dpsh", "Environment": env, "Name": f"{env.upper()} S3 Bucket"},
)

api_s3_role = aws.iam.Role(
    "DpshApplicationApiS3Role",
    assume_role_policy=pulumi.Output.from_input(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Effect": "Allow",
                    "Sid": "",
                }
            ],
        }
    ),
)

gpu_s3_role = aws.iam.Role("DpshApplicationGpuS3Role", assume_role_policy=api_s3_role.assume_role_policy)

# ------------------ #
#        IAM         #
# ------------------ #

api_instance_profile = aws.iam.InstanceProfile(
    "DpshApplicationApiInstanceProfile",
    role=api_s3_role,
)

gpu_instance_profile = aws.iam.InstanceProfile(
    "DpshApplicationGpuInstanceProfile",
    role=gpu_s3_role,
)

api_role_policy_attachment = aws.iam.RolePolicyAttachment(
    "DpshApiRolePolicyAttachment",
    role=api_s3_role,
    policy_arn="arn:aws:iam::aws:policy/AmazonS3FullAccess",
)

gpu_role_policy_attachment = aws.iam.RolePolicyAttachment(
    "DpshGpuRolePolicyAttachment",
    role=gpu_s3_role,
    policy_arn="arn:aws:iam::aws:policy/AmazonS3FullAccess",
)

# ------------------ #
#      Database      #
# ------------------ #

aurora_cluster = aws.rds.Cluster(
    "DpshAuroraCluster",
    engine="aurora-postgresql",
    engine_version="15.3",
    database_name=f"dpsh{env}",
    master_username=db_username,
    master_password=db_password,
    db_subnet_group_name=db_subnet.id,
    vpc_security_group_ids=[db_sg.id],
    skip_final_snapshot=db_skip_final_snapshot,
    tags={"Project": "dpsh", "Environment": env, "Name": f"{env.upper()} Database"},
)

aurora_cluster_instance = aws.rds.ClusterInstance(
    "DpshAuroraClusterInstance",
    identifier=f"aurora-cluster-instance-{env}",
    cluster_identifier=aurora_cluster.id,
    instance_class=db_instance_class,
    engine="aurora-postgresql",
    engine_version="15.3",
    publicly_accessible=False,
    db_subnet_group_name=db_subnet.id,
    tags={"Project": "dpsh", "Environment": env, "Name": f"{env.upper()} Database"},
)

# ------------------ #
#  Launch Templates  #
# ------------------ #

api_launch_template = aws.ec2.LaunchTemplate(
    "DpshApplicationApiLaunchTemplate",
    image_id=api_ami,
    instance_type=api_instance_type,
    vpc_security_group_ids=[api_sg.id],
    iam_instance_profile={
        "name": api_instance_profile.name,
    },
    tag_specifications=[
        {
            "resourceType": "instance",
            "tags": {
                "Name": f"{env.upper()} API Instance",
                "Project": "dpsh",
                "Environment": env,
            },
        },
    ],
)

gpu_launch_template = aws.ec2.LaunchTemplate(
    "DpshApplicationGpuLaunchTemplate",
    image_id=worker_ami,
    instance_type=worker_instance_type,
    vpc_security_group_ids=[gpu_sg.id],
    iam_instance_profile={
        "name": gpu_instance_profile.name,
    },
    tag_specifications=[
        {
            "resourceType": "instance",
            "tags": {
                "Name": f"{env.upper()} GPU Instance",
                "Project": "dpsh",
                "Environment": env,
            },
        },
    ],
)

# ------------------ #
#     Autoscaling    #
# ------------------ #

api_asg = aws.autoscaling.Group(
    "DpshApiAutoScalingGroup",
    min_size=min_num_api_instances,
    max_size=max_num_api_instances,
    vpc_zone_identifiers=api_subnet_ids,
    launch_template={
        "id": api_launch_template.id,
        "version": "$Latest",
    },
    force_delete=True,
)

gpu_asg = aws.autoscaling.Group(
    "DpshGpuAutoScalingGroup",
    min_size=min_num_worker_instances,
    max_size=max_num_worker_instances,
    vpc_zone_identifiers=gpu_subnet_ids,
    launch_template={
        "id": gpu_launch_template.id,
        "version": "$Latest",
    },
    force_delete=True,
)

# ------------------ #
#   Load Balancers   #
# ------------------ #

api_load_balancer = aws.elb.LoadBalancer(
    "DpshApiLoadBalancer",
    subnets=api_subnet_ids,
    security_groups=[api_sg.id],
    tags={"Project": "dpsh", "Environment": env, "Name": f"{env.upper()} API Load Balancer"},
    listeners=[
        aws.elb.LoadBalancerListenerArgs(
            instance_port=80,
            instance_protocol="http",
            lb_port=80,
            lb_protocol="http",
        ),
        aws.elb.LoadBalancerListenerArgs(
            instance_port=443,
            instance_protocol="http",
            lb_port=443,
            lb_protocol="https",
        ),
    ],
    health_check=aws.elb.LoadBalancerHealthCheckArgs(
        target="HTTP:80/",
        healthy_threshold=2,
        unhealthy_threshold=2,
        interval=30,
        timeout=5,
    ),
    instances=[api_asg.name],
)

gpu_load_balancer = aws.elb.LoadBalancer(
    "DpshGpuLoadBalancer",
    subnets=gpu_subnet_ids,
    security_groups=[gpu_sg.id],
    tags={"Project": "dpsh", "Environment": env, "Name": f"{env.upper()} GPU Load Balancer"},
    listeners=[
        aws.elb.LoadBalancerListenerArgs(
            instance_port=80,
            instance_protocol="http",
            lb_port=80,
            lb_protocol="http",
        ),
    ],
    health_check=aws.elb.LoadBalancerHealthCheckArgs(
        target="HTTP:80/",
        healthy_threshold=2,
        unhealthy_threshold=2,
        interval=30,
        timeout=5,
    ),
    instances=[gpu_asg.name],
)

# Export the URL of the API and GPU load balancers.
pulumi.export("api_url", api_load_balancer.dns_name)
pulumi.export("gpu_url", gpu_load_balancer.dns_name)
