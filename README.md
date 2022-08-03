## Amazon Fraud Detector Samples 


[Amazon Fraud Detector](https://aws.amazon.com/fraud-detector/) is a fully managed service that makes it easy to identify potentially fraudulent online activities such as online payment fraud and the creation of fake accounts. This repository contains a collection of example AWS solutions and Jupyter notebooks that interact with the Amazon Fraud Detector APIs. For more videos, blogs, and tutorials about Amazon Fraud Detector, refer to [Amazon Fraud Detector resource](https://aws.amazon.com/fraud-detector/resources/?blog-posts-cards.sort-by=item.additionalFields.createdDate&blog-posts-cards.sort-order=desc). 

#### Sample Notebooks

- Fraud_Detector_End_to_End_External_Data_OFI.ipynb, provides an example of building a detector using Amazon Fraud Detector’s APIs for Online Fraud Inisights (OFI) model type using external data sets. 

- Fraud_Detector_End_to_End_Stored_Data.ipynb, provides an example of building a detector using Amazon Fraud Detector’s APIs for Transaction Fraud Inisights (TFI) or Online Fraud Inisights (OFI) model type using data stored in Amazon Fraud Detector.  

- Fraud_Detector_End_to_End_ATI.ipynb, provides an example of building a detector using Amazon Fraud Detector’s APIs for Account Takeover Inisights (ATI) model type using data stored in Amazon Fraud Detector. Sample dataset is available under ```data``` folder. 

- Fraud_Detector_Send_Event.ipynb, provides an example of calling Amazon Fraud Detector's SendEvent API. 
  
- Fraud_Detector_GetEventPrediction_API_example.ipynb, provides an example of calling Amazon Fraud Detector’s event prediction API.  

- Fraud_Detector_BatchPrediction_API_Example.ipynb, provides an example of working with Amazon Fraud Detector's batch prediction API.

#### Automated Data Profiler

The profiler generates an intuitive and comprehensive report of your dataset, including variable statistics, label distribution, categorical and numeric analysis, and even variable&label correlations. It provides guidance on variable types as well as an option to transform the dataset into the format in compliance with AFD. Refer to [this blog post](https://aws.amazon.com/blogs/machine-learning/train-models-faster-with-an-automated-data-profiler-for-amazon-fraud-detector/) for more information. 

To use it, follow steps below:

1. Open the [CloudFormation quick launch link.](https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?templateURL=https://amazon-frauddetector-cfn-templates.s3.amazonaws.com/AFD_Data_Cleaner/afd_data_analyzer_cfn_template.yaml)
2. Fill in the parameters including: path to your CSV file in S3, some header names, and options. 
3. Click create stack. 
4. Wait a few minutes and open your S3 folder with your CSV file (e.g. myfile.csv). The profiling report is under folder /afd_data_myfile/report.html. 

#### Sample Data Sets

- data folder, provides sample data sets for OFI and TFI model types. 
  - registration_data_20K_full.csv and registration_data_20K_minimum.csv, provide sample data sets for OFI. 
  - transaction_data_100K_full.csv, provides sample data set for TFI. 
  - ato_data_800K_full.csv.zip, provides sample data set for ATI. Download and unzip to get the CSV data. 

## License

This library is licensed under the MIT-0 License. See the LICENSE file.


