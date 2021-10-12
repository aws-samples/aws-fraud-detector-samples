## Amazon Fraud Detector Samples 


Amazon Fraud Detector is a fully managed service that makes it easy to identify potentially fraudulent online activities such as online payment fraud and the creation of fake accounts. This repository contains a collection of example AWS solutions and Jupyter notebooks that interact with the Amazon Fraud Detector APIs.  

#### Sample Notebooks

- Fraud_Detector_End_to_End_External_Data_OFI.ipynb, provides an example of building a detector using Amazon Fraud Detector’s APIs for Online Fraud Inisights (OFI) model type using external data sets. 

- Fraud_Detector_End_to_End_Stored_Data.ipynb, provides an example of building a detector using Amazon Fraud Detector’s APIs for Transaction Fraud Inisights (TFI) or Online Fraud Inisights (OFI)  model type using data stored in Amazon Fraud Detector.  

- Fraud_Detector_Send_Event.ipynb, provides an example of calling Amazon Fraud Detector's SendEvent API. 
  
- Fraud_Detector_GetEventPrediction_API_example.ipynb, provides an example of calling Amazon Fraud Detector’s event prediction API.  

- Fraud_Detector_BatchPrediction_API_Example.ipynb, provides an example of working with Amazon Fraud Detector's batch prediction API.

#### Data Profiler

- profiler folder, provides a data profiler to generate a profiling report of the data. 

#### Sample Data Sets

- data folder, provides sample data sets for OFI and TFI model types. 
  - registration_data_20K_full.csv and registration_data_20K_minimum.csv, provide sample data sets for OFI. 
  - transaction_data_100K_full.csv, provides sample data set for TFI. 

## License

This library is licensed under the MIT-0 License. See the LICENSE file.


