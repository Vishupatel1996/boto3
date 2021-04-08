###create a VPC with one public subnet and one private subnet. Then create security groups for these two subnets and run instance in each subnet.

import boto3
import time

ec2 = boto3.resource('ec2',
    region_name='us-east-2',
    aws_access_key_id='AKIA4HZJGKUNY6FYG7CL',
    aws_secret_access_key='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',
)

# Creating a new key pair
outfile = open('/Users/vishwapatel/Desktop/Cloud_Computing/vishwa.pem','w')
key_pair = ec2.create_key_pair(KeyName ='vishwa')
KeyPairOut = str(key_pair.key_material)
print(KeyPairOut)
outfile.write(KeyPairOut)
outfile.close()


# create VPC
vpc = ec2.create_vpc(CidrBlock='192.168.1.0/24')
vpc.create_tags(Tags=[{"Key": "Name",
	"Value": "my_new_vpc"}])
vpcName = vpc.tags[0]['Value']
vpc.wait_until_available()
print(vpcName + ' ' + vpc.id)


time.sleep(10)

# creating subnet for private virtual cloud
private_subnet = ec2.create_subnet(CidrBlock='192.168.1.16/28',
            AvailabilityZone='us-east-2a',
	VpcId=vpc.id)
private_subnet.create_tags(Tags=[{"Key": "Name",
	"Value": "my-subnet-2a"}])
private_subnetName = private_subnet.tags[0]['Value']
print(private_subnetName +' '+private_subnet.id+' '+private_subnet.availability_zone)

# create then attach internet gateway
ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=ig.id)
print(ig.id)

# create a route table and a public route
route_table = vpc.create_route_table()
route = route_table.create_route(
    DestinationCidrBlock= '0.0.0.0/0',
    GatewayId=ig.id
)
print(route_table.id)

# creating subnet for public virtual cloud
public_subnet = ec2.create_subnet(CidrBlock='0.0.0.0/0',
            AvailabilityZone='us-east-2a',
	VpcId=vpc.id)
public_subnet.create_tags(Tags=[{"Key": "Name",
	"Value": "my-subnet-2b"}])
public_subnetName = public_subnet.tags[0]['Value']
print(public_subnetName +' '+public_subnet.id+' '+public_subnet.availability_zone)

# associate the route table with the subnet
route_table.associate_with_subnet(SubnetId=public_subnet.id)
time.sleep(15)

#Creating private security group
private_sec_group = ec2.create_security_group(
    GroupName='my-vpc-private-security-group',
    Description='my vpc private security group',
    VpcId=vpc.id)
private_sec_group.authorize_ingress(
    #CidrIp='0.0.0.0/0',   # allowing traffic from public ip
    CidrIp='192.168.1.0/24',   # allowing traffic from private ip
    IpProtocol='tcp',
    FromPort=80,
    ToPort=80
)
print(private_sec_group.id)

#Creating public security group
public_sec_group = ec2.create_security_group(
    GroupName='my-vpc-public-security-group',
    Description='my vpc public security group',
    VpcId=vpc.id)
public_sec_group.authorize_ingress(
    CidrIp='0.0.0.0/0',   # allowing traffic from public ip
    #CidrIp='192.168.1.0/24',   # allowing traffic from private ip
    IpProtocol='tcp',
    FromPort=-1,
    ToPort=-1
)
print(public_sec_group.id)

#Creating instances for private subnet
private_instances = ec2.create_instances(
     ImageId='ami-05aa8ea8a7f911839',
     MinCount=1,
     MaxCount=1,
     InstanceType='t2.micro',
     KeyName='vishwa',
     NetworkInterfaces=[{
        'SubnetId': private_subnet.id,
        'DeviceIndex': 0,
        'AssociatePublicIpAddress': False,
        'Groups': [private_sec_group.id]
    }],
)

#Creating instances for public subnet
public_instances = ec2.create_instances(
     ImageId='ami-05aa8ea8a7f911839',
     MinCount=1,
     MaxCount=1,
     InstanceType='t2.micro',
     KeyName='vishwa',
     NetworkInterfaces=[{
        'SubnetId': public_subnet.id,
        'DeviceIndex': 0,
        'AssociatePublicIpAddress': True,
        'Groups': [public_sec_group.id]
    }],
)

time.sleep(35)

for i in ec2.public_instances.all():
    print("Instance Id " + i.id + ", " +
          "Instance AMI " + i.image_id + ", " +
          "Instance type " + i.instance_type + ", " +
          "Instance state " + i.state['Name'])

for i in ec2.private_instances.all():
    print("Instance Id " + i.id + ", " +
          "Instance AMI " + i.image_id + ", " +
          "Instance type " + i.instance_type + ", " +
          "Instance state " + i.state['Name'])
