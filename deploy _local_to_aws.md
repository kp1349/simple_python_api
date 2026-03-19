### AWS cloud commands
VPC
```sh
# create vpc
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=my-vpc}]'
# save off VPC_ID in .env
VPC_ID="<from output>"

# create subnets
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-1}]'

aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-2}]'
# save off subnet IDs in .env
SUBNET_1_ID="<from output>"
SUBNET_2_ID="<from output>"

# create and attach internet gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=my-igw}]'
# save off internet gateway ID in .env
INTERNET_GATEWAY_ID="<from output>"

aws ec2 attach-internet-gateway \
  --internet-gateway-id $INTERNET_GATEWAY_ID \
  --vpc-id $VPC_ID

# create route table and add route to gateway
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=public-rt}]'
# save off route table ID in .env
ROUTE_TABLE_ID="<from output>"

aws ec2 create-route \
  --route-table-id $ROUTE_TABLE_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $INTERNET_GATEWAY_ID

# associate route table to both subnets
aws ec2 associate-route-table \
  --route-table-id $ROUTE_TABLE_ID \
  --subnet-id $SUBNET_1_ID

aws ec2 associate-route-table \
  --route-table-id $ROUTE_TABLE_ID \
  --subnet-id $SUBNET_2_ID
```
IAM
```sh
# create role
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ecs-tasks.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'
# save off role ARN in .env
EXECUTION_ROLE_ARN="arn:aws:iam::130595998424:role/ecsTaskExecutionRole"

# attach AWS managed policy (no need to create it manually on real AWS)
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```
ECR
```sh
# create ECR repo
aws ecr create-repository \
  --repository-name simple-python-api
# save off repo URI in .env
ECR_REPO_URI="130595998424.dkr.ecr.us-east-1.amazonaws.com/simple-python-api"

# authenticate docker to ECR
aws ecr get-login-password \
  | docker login \
    --username AWS \
    --password-stdin 130595998424.dkr.ecr.us-east-1.amazonaws.com

# tag your local image for ECR
docker tag kp1349/simple_python_api:latest $ECR_REPO_URI:latest

# push to ECR
docker push $ECR_REPO_URI:latest

# save off full image URI in .env
IMAGE_URI="130595998424.dkr.ecr.us-east-1.amazonaws.com/simple-python-api:latest"
```
ECS
```sh
# create ECS cluster
aws ecs create-cluster \
  --cluster-name simple-python-api-cluster
# save off cluster ARN in .env
CLUSTER_ARN="arn:aws:ecs:us-east-1:130595998424:cluster/simple-python-api-cluster"
# create task definition
aws ecs register-task-definition \
  --family simple-python-api \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 256 \
  --memory 512 \
  --execution-role-arn $EXECUTION_ROLE_ARN \
  --container-definitions '[
    {
      "name": "simple-python-api",
      "image": "130595998424.dkr.ecr.us-east-1.amazonaws.com/simple-python-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/simple-python-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]'
# save off task definition ARN in .env
TASK_DEF_ARN="<from output>"
```
ALB
```sh
# create security group for ALB
aws ec2 create-security-group \
  --group-name alb-sg \
  --description "ALB security group" \
  --vpc-id $VPC_ID
# save off security group ID in .env
ALB_SG_ID="<from output>"

# allow inbound HTTP traffic on ALB
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# create security group for ECS tasks
aws ec2 create-security-group \
  --group-name ecs-sg \
  --description "ECS task security group" \
  --vpc-id $VPC_ID
# save off security group ID in .env
ECS_SG_ID="<from output>"

# allow inbound traffic from ALB to ECS tasks on port 8000
aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG_ID \
  --protocol tcp \
  --port 8000 \
  --source-group $ALB_SG_ID

# create ALB
aws elbv2 create-load-balancer \
  --name simple-python-api-alb \
  --subnets $SUBNET_1_ID $SUBNET_2_ID \
  --security-groups $ALB_SG_ID \
  --scheme internet-facing \
  --type application
# save off ALB ARN in .env
ALB_ARN="<from output>"

# create target group
aws elbv2 create-target-group \
  --name simple-python-api-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-path /health
# save off target group ARN in .env
TARGET_GROUP_ARN="<from output>"

# create listener
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN
```
ECS service
```sh
aws ecs create-service \
  --cluster simple-python-api-cluster \
  --service-name simple-python-api-service \
  --task-definition simple-python-api \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[$SUBNET_1_ID,$SUBNET_2_ID],
    securityGroups=[$ECS_SG_ID],
    assignPublicIp=ENABLED
  }" \
  --load-balancers "targetGroupArn=$TARGET_GROUP_ARN,containerName=simple-python-api,containerPort=8000"
# save off service ARN in .env
SERVICE_ARN="<from output>"

# get the ALB DNS name to test your app
aws elbv2 describe-load-balancers \
  --load-balancer-arns $ALB_ARN \
  --query 'LoadBalancers[0].DNSName'
```
extra steps:
```sh
# check status:
aws ecs describe-services \
  --cluster simple-python-api-cluster \
  --services simple-python-api-service \
  --query 'services[0].{status:status,running:runningCount,desired:desiredCount}'
# check health
aws elbv2 describe-target-health \
  --target-group-arn $TARGET_GROUP_ARN
# check errors
aws ecs describe-services \
  --cluster simple-python-api-cluster \
  --services simple-python-api-service \
  --query 'services[0].events[:5]'
# create the cloudwatch log stream:
aws logs create-log-group \
  --log-group-name /ecs/simple-python-api
# force retry:
aws ecs update-service \
  --cluster simple-python-api-cluster \
  --service simple-python-api-service \
  --force-new-deployment
```
hit the endpoints:
```sh
curl http://simple-python-api-alb-651638832.us-east-1.elb.amazonaws.com/health

curl -X POST http://simple-python-api-alb-651638832.us-east-1.elb.amazonaws.com/hello \
  -H "Content-Type: application/json" \
  -d '{"name": "John"}'
