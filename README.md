#  es-text-similarity-comprehend-demo

This is a demonstrantion has the purpose of how we can use Amazon Comprehend and Amazon Elasticsearch Service to create a search engine that could help us to search text similarity.

# Challenge

Brazilian Federal Senate staff waste a lot of time searching similarities between new propositions (Projeto de Lei, Projeto de Emendas Constitucionais e etc) and older propositions to avoid wasting time voting on something that was already voted in the past. The idea of this demonstration using open data to find similarities between propositions, using Amazon Comprehend or Amazon Elasticsearch

[Open Data Portal](https://dadosabertos.camara.leg.br/swagger/api.html#staticfile)

# Prerequisites

- Pre configured AWS credentials
- [Pre configured VPC](https://github.com/BRCentralSA/aws-brazil-edu-series/blob/master/utils/vpc-template.yaml)
    - The VPC should have at least 2 public subnets and 2 private subnets using NAT Gateway
- [awscli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)


# Application architecture

<p align="center"> 
<img src="images/es-text-similarity-comprehend-demo.png">
</p>

# Provisioning the infrastructure:

First you need to create a S3 bucket to store our application lambda code. (That will be used in CloudFormation Later)

Note: Replace <MY_BUCKET_NAME> to a bucket name that you are going to use. (Take note of the choosen bucket name)

```shell
aws s3 mb s3://<MY_BUCKET_NAME>
```

ZIPing (compressing) the lambda code.

```shell
cd lambda_enhance_text/ && zip ../lambda_enhance.zip lambda_function.py
```

```shell
cd ../lambda_parser_csv && zip ../lambda_csv_parser.zip lambda_function.py
```

```shell
cd ../
```

Uploading the lambda packages to the S3 bucket that we have created in the prior step.

```shell
aws s3 cp lambda_enhance.zip s3://<MY_BUCKET_NAME>/lambda/
```

```shell
aws s3 cp lambda_csv_parser.zip s3://<MY_BUCKET_NAME>/lambda/
```

Now we need to upload the Elasticsearch module that we will use to index the results of the data analysis.

```shell
cd layer && aws s3 cp elastic.zip s3://<MY_BUCKET_NAME>/layer/
```

**Now we need to create our stack using the CloudFormation template, available in cloudFormation/ folder in the root of this repository**

## Cloudformation

Now we need to open AWS Console and search for CloudFormation

<p align="center"> 
<img src="images/console01.png">
</p>

Now click in Create stack > With new resources (standard)

<p align="center"> 
<img src="images/console02.png">
</p>

We need to choose our cloudformation YAML available in this repository inside `cloudformation/` upload the file and click in next

<p align="center"> 
<img src="images/console03.png">
</p>

In Specify stack details we need to fill with the parameters to create our stack and also give the stack name.

<p align="center"> 
<img src="images/console04.png">
</p>

**BucketLambdaCode**: The bucket that we created early to upload our lambda ZIP file and also our Lambda Layer

**BucketName**: The name of the bucket that we are going to use to upload our proposition files

**LanguageCode:** Code of comprehend for text analysis

**Nat1PublicIP:** The public IP of the first NAT Gateway

**Nat2PublicIP:** The public IP of the second NAT Gateway

**PrivateSubnetID1:** ID of the first private subnet

**PrivateSubnetID2:** ID of the second private subnet

**SecurityGroup:** ID of security group to associate with Lambda (You can use anyone)

**YourPublicIP:** Your public IP

> You can use the command below to find your public IP

```shell
curl ifconfig.me
```

And click and Next > Next.

Scroll to the end of the page and mark **I acknowledge that AWS CloudFormation might create IAM resources** and Create Stack

<p align="center"> 
<img src="images/console05.png">
</p>

All the infraestructure will start to spin up, wait some minutes.

# Testing the solution

All we need to do is upload the **data/proposicoes-2020.csv** file to the S3 bucket that our CloudFormation create and visualize the information in indexed in Elasticsearch via Kibana

Check the Bucket name in the Outputs tab of CloudFormation Stack

<p align="center"> 
<img src="images/console06.png">
</p>

Upload the file to the bucket

```shell
aws s3 cp data/proposicoes-2020.csv s3://<BucketName>/data/
```

Change the value of BucketName to your bucket

After that our Lambda will start to process our file, you can check that based on the SQS items in queue

<p align="center"> 
<img src="images/console07.png">
</p>

Now go to Elasticsearch Service and click in **es-comprehend-demo** get the Kibana URL to access Kibana Application

<p align="center"> 
<img src="images/console08.png">
</p>

We have to create the index pattern to be able to visualize the data in Kibana, create the index pattern with the name **proposicoes**

<p align="center"> 
<img src="images/console09.png">
</p>

Click in Next step

For **Time Filter field name** select feed_date

<p align="center"> 
<img src="images/console10.png">
</p>

Click in Create index pattern

<p align="center"> 
<img src="images/console11.png">
</p>

Now we are able to visualize and search for patterns in our indexed data

<p align="center"> 
<img src="images/console12.png">
</p>

# Cleaning up

Delete all the files inside of the provisioned S3 bucket.

```shell
aws s3 rm s3://<BUCKET_NAME> --recursive
```

Delete the CloudFormation stack.

```shell
aws cloudformation delete-stack --stack-name your-stack-name
```

Delete the S3 bucket that we used to store the lambda codes and lambda layer.

```shell
aws s3 rb s3://<BUCKET_LAMBDA_CODE> --force
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

