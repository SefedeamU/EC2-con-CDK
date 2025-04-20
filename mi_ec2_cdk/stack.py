from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    LegacyStackSynthesizer  # <-- Usamos LegacyStackSynthesizer
)
from constructs import Construct

class MiEc2Stack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        # Configuramos LegacyStackSynthesizer para evitar SSM y bootstrap.
        synthesizer = LegacyStackSynthesizer()
        super().__init__(scope, id, synthesizer=synthesizer, **kwargs)

        # 1) VPC mínima: 1 AZ, sin NAT (solo subred pública)
        vpc = ec2.Vpc(self, "MiVPC",
            max_azs=1,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )

        # 2) Security Group: abre 22 y 80 a todo el mundo
        sg = ec2.SecurityGroup(self, "MiSG", vpc=vpc, allow_all_outbound=True)
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "SSH")
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "HTTP")

        # 3) Importa el rol IAM existente para la instancia (LabRole)
        role = iam.Role.from_role_arn(
            self, "InstanceRole",
            role_arn="arn:aws:iam::065548213155:role/LabRole",
            mutable=False
        )

        # 4) Instancia EC2: AMI fija, disco raíz de 20 GiB, SG y rol asignado
        ec2.Instance(self, "MiInstanciaEC2",
            vpc=vpc,
            security_group=sg,
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.GenericLinuxImage({
                "us-east-1": "ami-0363234289a7b6202"
            }),
            block_devices=[ec2.BlockDevice(
                device_name="/dev/xvda",
                volume=ec2.BlockDeviceVolume.ebs(20)
            )],
            role=role
        )
