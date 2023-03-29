- **ato_data_800K_full.csv.zip**: sample dataset for Account Takeover Insights. Suitable for both [internal storage and external storage](https://docs.aws.amazon.com/frauddetector/latest/ug/event-data-storage.html).

- **registration_data_20K_full.csv**: sample dataset for Online Fraud Insights. Suitable for only [external storage](https://docs.aws.amazon.com/frauddetector/latest/ug/event-data-storage.html).

- **registration_data_20K_minimum.csv**: sample dataset for Online Fraud Insights. Suitable for only [external storage](https://docs.aws.amazon.com/frauddetector/latest/ug/event-data-storage.html).

- **transaction_data_100K_full.csv**: sample dataset for Transaction Fraud Insights. Suitable for both [internal storage and external storage](https://docs.aws.amazon.com/frauddetector/latest/ug/event-data-storage.html). 

- **UpdateDatasetTimestamp.ipynb**: notebook to update EVENT_TIMESTAMP of all events to last 18 months. 

- **coldstart**: folder contains datasets for [cold-start](https://aws.amazon.com/about-aws/whats-new/2023/02/amazon-fraud-detector-cold-start-model-training-limited-historical-data/) use cases. 
  - registration_data_2K_coldstart.csv: sample coldstart dataset for registration fraud use case.
  - Insurance_FraudulentAutoInsuranceClaims_2K_coldstart.csv: sample coldstart dataset for insurance fraud use case.
  - transaction_data_2K_coldstart.csv: sample coldstart dataset for online transaction fraud use case.
