# Org Assemble (Eventbridge Version)

It automates the AWS Organization creation process, creating 2 organizational units and 4 accounts. The first unit, Security, contains the Logging account that stores logs for the organization 
trail, and server access logs for the centralized logging bucket. The second unit, Workloads, contains a Dev, Staging, and Prod account for each stage in the software development life cycle. Each account in the Workloads 
unit contains a storage bucket, a limited role with access to said bucket and server access logs for the storage bucket.

## Getting Started

### Prerequisites

* AWS Account
* Slack account 
* Slack workspace to use for notifications


### Installing

#### Create a new channel in your slack workspace

1. On the left hand side of your slack workspace, click the plus button next to Channels

2. Click on **Create a channel**

3. Give the channel a name, for example notifications.

4. Click on **Create**

5. On the Add People page, click on **Skip for now**


#### Create a new slack app for your current workspace

1. Go to [Slack App](https://api.slack.com/apps) homepage
  
2. Click on **Create New App** 
  
3. Give the app a name, for example org-notifications
  
4. Click on the **Development Slack Workspace** drop down menu, choose your current workspace 
  
5. Click **Create App**
  

#### Create an Incoming Webhook for the app, connecting it to the channel you created in step 1 

1. After creating an app you should be redirected to the Building Apps for Slack page
  
2.  Click on **Incoming Webhooks** under Add Features and Functionality 
  
3. Click on the on/off toggle next to Activate Incoming Webhooks to activate this feature
  
4. Scroll down to the bottom, click on **Add New Webhook to Workspace** under Webhook URL

5. This will take you to a page requesting app permissions
  
6. Click on the **Search for a channel** drop down menu, and select the channel you created in step 1
  
7. Click on **Allow**
  
8. Leave this page open as you will need your webhook to run the code later


#### In your AWS Account, create an organization 

1. In the AWS Management Console, select Organizations under Management & Governance
  
2. Click on **Create organization**
  
3. Click **Create organization** once again on the Create Organization pop up
  

####  Enable trust between your organization and stacksets

1. In the left hand corner, choose **Services** and then select **Cloudformation** under
  
2. On the left hand menu click on **stacksets**
  
3. There should be a banner on the top of the screen that says, "Enable trusted access with AWS Organizations to use service managed permissions". If not, reload the page.
  
4. Click on **Enable trusted access**


#### Create a trail in your AWS account

1. In the left hand corner, choose **Services** and then select **Cloudtrail** under Management & Governance
  
2. On the left hand menu click on **Trails**
  
3. Click on **Create Trail**
  
4. Give the trail a name, for example org-trail
 
5. Click **Yes** next to **Apply trail to my organization**

6. Scroll down to **Storage Location** and create a new S3 bucket
 
7. Give the bucket a unique name

8. Click **Create**


#### Create a user with programmatic access in your AWS account
  
1. In the left hand corner, choose **Services** and then select **IAM** under Security, Identity, & Compliance

2. On the left hand menu click on **Users** under Access Management

3. Click on **Add User**

4. Give the user a name

5. Click on **Programmatic access**

6. Click **Next:Permissions**

7. Under Set Permissions, click on **Create Group**

8. Give the group a name

9. Under policies, click **AdministratorAccess**

10. Click **Create Group**

11. Once redirected back to the Set Permissions page, click **Next:Tags**

12. Nothing to add on this page, so click **Next:Review**

13. Review the information, then click **Create User**

14. On the Success Page, click on **Download .csv** as you will need this information to create a user for the AWS CLI  


#### Setup your command line user

1. Make sure you already have the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) installed

2. Open up your computer’s terminal 

3. Configure your user profile: `aws configure --profile profileName`

4. Use the .csv file downloaded earlier to enter the AWS Access Key ID & AWS Secret Access Key ID

5. Set the environment variables for your terminal session: `export AWS_PROFILE=profileName`


#### Download the repo code

1. Navigate to [Github](https://github.com/k-morgan22/s3-serverless/blob/master) and download the repo

2. In your computer’s terminal, navigate to the directory where the repo is stored 

3. Unzip the repo: `unzip s3-serverless-master.zip`

4. CD in the unzipped repo: `cd s3-serverless-master`

    
#### SAM deploy from the command line

1. In the s3-serverless-master directory, deploy the SAM app: `sam deploy --guided`
 
2. When prompted, input the necessary parameters: 
    1. **Stack Name**, either leave blank and use the default name or give the stack a name

    2. **AWS Region**, the region should be us-east-1

    3. **Parameter LoggingAccountEmail**, enter a unique email address for the logging account 

    4. **Parameter DevAccountEmail**, enter a unique email address for the dev account 

    5. **Parameter StagingAccountEmail**, enter a unique email address for the staging account 

    6. **Parameter ProdAccountEmail**, enter a unique email address for the prod account 

    7. **Parameter SlackWebHookUrl**, enter the slack webhook url created earlier

    8. **Confirm changes before deploy**, enter y to see the cloudformation changeset before deployment

    9. **Allow SAM CLI IAM role creation**, enter y or deployment will fail

    10. **Save arguments to samconfig.toml**, enter either y or n, this does not affect deployment  

3. SAM will start the deployment process and create a changeset. 

    * If you entered **y** for **Confirm changes before deploy**, review the changeset and enter **y** when prompted to **deploy the changeset** and continue the deployment process. 

    * If you entered **n**, the deployment process will continue without your input

4. The stack will run until the process is complete. When you see **Successfully created/updated stack - stackName in us-east-1**, SAM has successfully created all the necessary resources in your account for this app to run. 

Once the stack has successfully completed, you will start receiving notifications in the slack channel you created, giving you updates on the organization creation process.


## Architecture
