### instant-vpn

Setup your very own ephemeral VPN in AWS.

The goal of this project is to create a VPN on demand every time you need it, resulting in a near zero cost.

The VPN will only be accessible from your current IP address.

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

Create a file called `variables.yaml` in this project's root directory and specify the following.

```yaml
stack_prefix: <prefix>
keypair: <aws keypair name>

# OPTIONAL (uncomment)
# domain: <your domain in route53>.
```

By default the resources will deploy in the `eu-west-2` (London) region. To deploy into another region simply rename the `config/prod/ew2` and modify the `region` and `Az1` variables.

For instance, to deploy to `us-east-1`:

```bash
mv config/prod/ew2 config/prod/us1
```

Then change the following:
* `region`: variable in `config/prod/ew2/config.yaml` to `us-east-1`
* `Az1`: variable in `config/prod/ew2/subnets.yaml` to `us-east-1a`

### Deployment

To deploy the resources in the selected region:

```bash
export AWS_DEFAULT_PROFILE=<your AWS profile>
sceptre --var-file=variables.yaml create-stack prod/ew2 vpc
sceptre --var-file=variables.yaml create-stack prod/ew2 subnets
sceptre --var-file=variables.yaml create-stack prod/ew2 vpn
```

Once the resources have finished deploying you can SSH into the box and configure the OpenVPN client.

To obatin the ssh IP, simply:

```bash
sceptre --var-file=variables.yaml describe-stack-outputs prod/ew2 vpn
ssh -i <location/of/pem/key> openvpnas@<OpenVpnPublicIp>
```

It is good practice to remove SSH access to the box via the AWS security group to prevent unwanted intrusions, for this simply edit the `config/prod/ew2/vpn.yaml` file and change the `enable_ssh` attribute to `false`.

Perform an update of the stack as follows:

```bash
sceptre --var-file=variables.yaml update-stack prod/ew2 vpn
```

### Optional steps

If you own a domain and is configured in Route53, modify the `variables.yaml` file with your domain name in Route53.

You can then run:

```bash
sceptre --var-file=variables.yaml create-stack prod/ew2 recordsets
```

To make the VPN publicly accessible, edit the `config/prod/ew2` file and modify the `AccessIP` variable to match your desired access IP, including the mask.

You will then need to update the template via:

```bash
sceptre --var-file=variables.yaml update-stack prod/ew2 vpn
```


### Scheduling

The project includes a lambda function deployed via [Serverless](https://serverless.com/) that shuts down the instance at night. The rate and configuration of the lambda can be modified in the `lambdas/serverless.yaml` file.
