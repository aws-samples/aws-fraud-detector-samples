## Amazon Fraud Detector Data Profiler

-----

### Automated Solution

The AWS CloudFormation template - afd_data_analyzer_cfn_template.yaml and Glue job script - afd_data_analyzer_glue_script.py under CloudFormationSolution provides an automated profiler using AWS CloudFormation, AWS Lambda, and AWS Glue.

To use it, follow steps below:
1. Open the [CloudFormation quick launch link.](https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?templateURL=https://amazon-frauddetector-cfn-templates.s3.amazonaws.com/AFD_Data_Cleaner/afd_data_analyzer_cfn_template.yaml)
2. Fill in the parameters including: path to your CSV file in S3, some header names, and options. 
3. Click create stack. 
4. Wait a few minutes and open your S3 folder with your CSV file (e.g. myfile.csv). The profiling report is under folder /afd_data_myfile/report.html. 


### Manual Solution 

From Github download and copy the notebook - Fraud_Detector_Data_Profiling.ipynb, the python program - afd_profile.py and the template directory to a directory where you will run the profiling from. 

- Fraud_Detector_Data_Profiling.ipynb - is the notebook to run the profile report from. 
- afd_profile.py - is the python package which will generate your profile report, you can also run it via command line.  
- /templates - directory contains the supporting profile templates
