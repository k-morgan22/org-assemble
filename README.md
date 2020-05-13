# Org Assemble

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
  

#### Run the initial.yml template

1. If you already have the template on your local system, skip this step
  
	a. If not, navigate to [Github](https://github.com/k-morgan22/s3-serverless/blob/master/initial.yml) and download the yml file 
    
2. In the Cloudformation console, click on the left hand menu and select **stacks**
  
3. Click on **Create stack**
  
4. Choose **Template is ready** 
  
5. Choose **Upload a template file**
  
6. Select **Choose file** and navigate to your local copy of initial.yml
  
7. Select **Next**
  
8. On the Parameters page, give the stack a name 
  
9. Enter the 4 unique email address for your log, dev, staging, and prod accounts
  
10. Go back to the slack app page and copy the webhook url you created in step 3
  
11. Paste that url in the **Slack Webhook Url** parameter
  
12. Click **Next**
  
13. On the Configure stack options page, leave everything as default and click **Next** on the bottom of the page
  
14. On the Review page, double check you enter your email addresses correctly and scroll down to the bottom
  
15. Click the check box next to "I acknowledge that AWS Cloudformation might create IAM resources with custom names."
  
16. Click **Create stack**
  

The stack will run, creating all the necesary resources in your account for this app. 
Once the stack has successfully completed, you will start receiving notification in the slack channel you created, giving you updates on the organization creation process.


## Architecture
