# Org Assemble (Monolith Version)

It automates the AWS Organization creation process, creating 2 organizational units and 4 accounts. The first unit, Security, contains the Logging account that stores logs for the organization 
trail, and server access logs for all buckets in the other 3  accounts. The second unit, Workloads, contains a Dev, Staging, and Prod account for each stage in the software development life cycle. Each account in the Workloads 
unit contains a storage bucket and a limited role with access to said bucket.

## Getting Started

### Prerequisites

* AWS Account
* Slack account 
* Slack workspace to use for notifications


## Current Status
Not Functional 