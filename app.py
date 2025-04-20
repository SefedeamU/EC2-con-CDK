#!/usr/bin/env python3
import aws_cdk as cdk
from mi_ec2_cdk.stack import MiEc2Stack
from aws_cdk import Environment

app = cdk.App()

env = Environment(account="065548213155", region="us-east-1")
MiEc2Stack(app, "MiEc2Stack", env=env)
app.synth()

