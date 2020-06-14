# Org Assemble (Eventbridge Version)

It automates the AWS Organization creation process, creating 2 organizational units and 4 accounts. The first unit, Security, contains the Logging account that stores logs for the organization 
trail, and server access logs for all buckets in the other 3  accounts. The second unit, Workloads, contains a Dev, Staging, and Prod account for each stage in the software development life cycle. Each account in the Workloads 
unit contains a storage bucket and a limited role with access to said bucket.

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
  
5. Click on the **Search for a channel** drop down menu, and select the channel you created in step 1
  
6. Click on Allow
  
7. Leave this page open as you will need your webhook for step 6


#### In your AWS Account, create an organization 

1. In the AWS Mangement Console, select Organizations under 
  
2. Click on **Create organization**
  
3. Click **Create organization** once again on the Create Organization pop up
  

####  Enable trust between your organization and stacksets

1. In the left hand corner, choose **Services** and then select **Cloudformation** under
  
2. On the left hand menu click on **stacksets**
  
3. There should be a banner on the top of the screen that says, "Enable trusted access with AWS Organizations to use service managed permissions". If not, reload the page.
  
4. Click on **Enable trusted access**


#### Create a trail in your AWS account


#### Create a user with programmatic access in your AWS account
  

#### Download the repo code

1. Navigate to [Github](https://github.com/k-morgan22/s3-serverless/blob/master) and download the repo

    
#### SAM deploy from the command line


The stack will run, creating all the necesary resources in your account for this app. 
Once the stack has successfully completed, you will start receiving notification in the slack channel you created, giving you updates on the organization creation process.


## Architecture
