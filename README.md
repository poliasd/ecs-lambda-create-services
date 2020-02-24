# ecs-lambda-create-services


This is a lambda function written in Python 3.8 which creates an ESC cluster, a load balancer with a target group and deploys a service.

1. Change the values of the following parameters with the ones that you will use:

```
cluster_name = 'demo'
image_id = 'ami-image'
key_name = 'key-kp'
subnet1 = 'subnet-1'
subnet2 = 'subnet-2'
security_group = 'sg-123'
vpc_id = 'vpc-123'
instance_profile_arn = 'arn:aws:iam::11111111:instance-profile/EC2RoleECS'
```

2. You can use [aws cli](https://docs.aws.amazon.com/cli/latest/reference/lambda/create-function.html) to upload the function or can create a lambda function using AWS console and copy/paste the code.

