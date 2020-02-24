import boto3
import os

ecs_client = boto3.client('ecs')
ec2_client = boto3.client('ec2')
elb_client = boto3.client('elbv2')
autoscaling_client = boto3.client('autoscaling')

cluster_name = 'demo'
image_id = 'ami-image'
key_name = 'key-kp'
subnet1 = 'subnet-1'
subnet2 = 'subnet-2'
security_group = 'sg-123'
vpc_id = 'vpc-123'
instance_profile_arn = 'arn:aws:iam::11111111:instance-profile/EC2RoleECS'
target_group_arn =''

def create_cluster():
    launch_configuration_name = 'ecs-' + cluster_name + '-launch-configuration'
    auto_scaling_group_name = 'ecs-' + cluster_name + '-auto-scaling'
    capacity_provider_name = cluster_name + '-capacity-provider13'

    response_launch_configuration = autoscaling_client.create_launch_configuration(
        LaunchConfigurationName = launch_configuration_name,
        ImageId = image_id,
        KeyName = key_name,
        InstanceType = 't2.micro',
        IamInstanceProfile = instance_profile_arn,
        UserData='#!/bin/bash \n echo ECS_CLUSTER=' + cluster_name + ' >> /etc/ecs/ecs.config',
        SecurityGroups=[
            security_group
        ]
    )
    
    print('--response_launch_configuration'--)
    print(response_launch_configuration)
    
    response_scaling_group = autoscaling_client.create_auto_scaling_group(
        AutoScalingGroupName = auto_scaling_group_name,
        LaunchConfigurationName = launch_configuration_name,
        MinSize = 0,
        MaxSize = 2,
        DesiredCapacity = 2,
        VPCZoneIdentifier = subnet1 + ', ' + subnet2
    )
    
    print('--response_scaling_group--')
    print(response_scaling_group)
    
    response_cluster = ecs_client.create_cluster(
        clusterName = cluster_name,
    )
    
    cluster_status = response_cluster['cluster']['status']
    print(cluster_status)


def create_load_balancer(): 
    target_group_name = 'ecs-' + cluster_name + '-target-group'
    load_balancer_name = 'ecs-' + cluster_name + '-load-balancer'

    response_target_group = elb_client.create_target_group(
        Name = target_group_name,
        Protocol = 'HTTP',
        Port = 80,
        VpcId = vpc_id
    )
    
    target_group_arn = response_target_group['TargetGroups'][0]['TargetGroupArn']
    
    response_load_balancer = elb_client.create_load_balancer(
        Name = load_balancer_name,
        Subnets=[
            subnet1, subnet2
        ],
        SecurityGroups=[
            security_group
        ],
        Type='application',
        IpAddressType='ipv4'
    )
    print(response_load_balancer['LoadBalancers'][0]['LoadBalancerArn'])

    response_listener = elb_client.create_listener(
        LoadBalancerArn = response_load_balancer['LoadBalancers'][0]['LoadBalancerArn'],
        Protocol = 'HTTP',
        Port = 80,
        DefaultActions = [
            {
                'TargetGroupArn': target_group_arn,
                'Type': 'forward'
            }
        ]
    )
    
    print(response_listener)

def create_task_definition():
    response = ecs_client.register_task_definition(
        containerDefinitions=[
            {
              "name": "game",
              "image": "poliasd/pacman:1.0",
              "essential": True,
              "portMappings": [
                {
                  "containerPort": 80,
                  "hostPort": 80
                }
              ],
              "memory": 250,
              "cpu": 10,
                tags=[
                    {
                        'key': 'game-name',
                        'value': 'pacman'
                    },
                ]
            }
        ],
        family="game"
    )
    print(response)

def create_service():
    response = ecs_client.create_service(
        cluster = cluster_name,
        serviceName = "game",
        taskDefinition = "game",
        loadBalancers=[
        {
            'targetGroupArn': target_group_arn,
            'containerName': 'game',
            'containerPort': 80
        },
        ],
        desiredCount = 2,
        launchType = 'EC2',
        deploymentConfiguration = {
            'maximumPercent': 200,
            'minimumHealthyPercent': 50
        }
    )
    print(response)

def lambda_handler(event, context):
    create_cluster()
    create_load_balancer()
    create_task_definition()
    create_service()