### instant-vpn

Setup your very own ephemeral VPN in AWS.

The goal of this project is to create a VPN on demand every time you need it, resulting in a near zero cost.

## Prerequisites

* An [AWS](https://aws.amazon.com/) account. You can set one up in minutes.
* An IAM user/role with the full access to the account.
* AWS credentials found in your AWS credentials directory (~/.aws/credentials).

**If you do not have an account that qualifies under the AWS free tier, the creation of the resources in this repository will incur in AWS costs. I do not take responsibility for these.**

Clone this repo and continue as follows:

```bash
git clone https://github.com/afdezl/instant-vpn.git && cd instant-vpn
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Usage

This project makes use of [sceptre](https://github.com/cloudreach/sceptre) to manage the AWS infrastructure. Refer to the docs for more info on configuration.

### Setup

By default the resources will deploy in the `eu-west-2` (London) region. To deploy into another region simply copy the `config/prod/ew2` directory and rename it, then modify the following variables:

* `region`: variable in `config/prod/<region>/config.yaml` to `<aws-region>`
* `Az1`: parameter in `config/prod/<region>/subnets.yaml` to `<aws-region-az>`

To successfully deploy the resources the following parameters will have to be configured in the `config/prod/<region>/vpn.yaml` and `config/prod/<region>/recordsets.yaml`:

* `KeyName` **[REQUIRED]**: The keypair name to log into your AWS EC2 VPN instance.
* `HostedZone` **[OPTIONAL]**: The name of your Hosted zone if you wish to create an A record in the form of `vpn.<domain>`.


### Deployment

To deploy the resources in the selected region:

```bash
export AWS_DEFAULT_PROFILE=<your AWS profile>
sceptre launch-env prod/ew2
```

Once the resources have finished deploying you can SSH into the box and configure the OpenVPN server.

To obatin the SSH IP, simply:

```bash
eval $(sceptre describe-stack-outputs prod/ew2 vpn --export=envvar)
ssh -i /path/to/pem-key openvpnas@${SCEPTRE_OpenVpnPublicIp}
```

It is good practice to remove SSH access to the box via the AWS security group to prevent unwanted intrusions, for this simply edit the `config/prod/ew2/vpn.yaml` file and change the `enable_ssh` parameter to `false`.

Perform an update of the stack as follows:

```bash
sceptre update-stack prod/ew2 vpn
```

### Optional steps

If you own a domain and is configured in Route53, modify the `variables.yaml` file with your domain name in Route53. The CloudFormation template will create an entry in the format `vpn.<domain>`.

You can then run:

```bash
sceptre create-stack prod/ew2 recordsets
```

To make the VPN publicly accessible, edit the `config/prod/ew2` file and modify the `AccessIP` variable to match your desired access IP, including the mask. The VPN will otherwise be only accessible from your current IP.

You will then need to update the template via:

```bash
sceptre update-stack prod/ew2 vpn
```


## Lambdas

A set of lambdas is included to avoid using EIPs and adding optional shutdown times for the instance.
Assuming the serverless package is installed and the parameters in the `.serverless.yml` file are have been updated with your values, these can be deployed as follows:

```bash
cd lambdas
eval $(sceptre describe-stack-outputs prod/ew2 vpn --export=envvar)
sls deploy
```

### Scheduling

The project includes a lambda function deployed via [Serverless](https://serverless.com/) that shuts down the instance at night. The rate and configuration of the lambda can be modified in the `lambdas/serverless.yaml` file.

### Avoiding Elastic IPs

In order to reduce the stack cost, the VPN does not make use of an elastic IP, thus on every restart of the instance, the public IP will be different. A lambda called `update_r53.py` bypasses this by listening to an AWS RunInstances event and updating a R53 record with the instance public IP on every instance start.
