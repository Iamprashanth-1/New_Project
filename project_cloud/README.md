# Mutual Fund Data Storage

This Projects helps us to fetch the data everyday from amfiindia portal and store it in database 

This Automation Can be done in Two Methods

The Following Services or tools or database are used in this Project
- Database : MongoDb (We can use Redshift as well due to resource restrictions unable to use it)
- Programming : Python3
- Cloud services : AWS (ECS , ECR , Lambda , ClodWatch , EC2)

## Method 1 (Temo)

 Using Serverless Application Model (SAM) we can directly deploy the services which are mentioned in the template
- First we need to install SAM CLI
- Start with this command 
```bash
 sam init
```
- Choose template and language 
- Name the application
- Open the Project and write set of services in template.yaml file to deploy in AWS
- Build the application using the below command
```bash
 sam build
```
- use this command to test application
```bash
sam local invoke
```
- use this command to deploy
```bash
sam deploy --guided
```

#### Note : Configure aws credentials in    .aws folder

Flow


![Flow](https://github.com/Iamprashanth-1/New_Project/blob/main/project_cloud/method1.PNG)
```
If we want to use this approach we need to load older data manually since loading older data takes more than 15 min

Upon Evey day the lambda gets triggered by Cloudwatch event ( insertion time at max 3 minutes)

we can add retry in template so that any exception occurs it gets retried


This approach has drawback if we want to start with initial load
- Lambda gets timeout for 15 minutes

```
## Method 2 (affi)
We can containerize the Script and Push it to ECR

Code is Available in Source Folder

Connect to ECR using below push Commands 
```
 aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin {account_id}.dkr.ecr.us-east-1.amazonaws.com
```
Build the Docker Image using below Command
```
docker build -t project_name .
```
Tag the latest changes
```
docker tag project_name:latest {account_id}.dkr.ecr.us-east-1.amazonaws.com/project_name:latest
```
Push the Changes to ECR
```
docker push {account_id}.dkr.ecr.us-east-1.amazonaws.com/project_name:latest
```
Note :  Replace project_name with respective project name and {account_id} with AWS Account ID

The Flow 

![Flow](https://github.com/Iamprashanth-1/New_Project/blob/main/project_cloud/method2.PNG)































