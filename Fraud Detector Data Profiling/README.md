
## Fraud Detector Data Profiling

This sample notebook and python code provides a simple data profile that can help get an understanding of your data as well as identify data quality and other issues prior to training a model with Fraud Detector. 

Instructions:
1. download the [afd_profile.py](afd_profile.py)  to your jupyter notebook, and the templates directory to your notebook. afd_profile.py contains functions to perform the profiling and the /templates directory contains .html templates to present the profile report. 
2. dowload the [Fraud_Detector_Data_Profiling.ipynb](Fraud_Detector_Data_Profiling.ipynb) to your jupyter notebook 
3. configure the notebook to point to your data, and identify the key fields
4. run your notebook, review the report.html that is produced. 

Samples:
[Fraud Detector Data Profiling-Sample_Results.ipynb](Fraud_Detector_Data_Profiling-Sample_Results.ipynb) - contains a sample result of running the data profiling notebook on the sample dataset **synthitic_newaccount_data_50k.csv** and the [report.html](https://htmlpreview.github.io/?https://github.com/aws-samples/aws-fraud-detector-samples/blob/master/Fraud%20Detector%20Data%20Profiling/report.html) contains a sample data profiling report. 

Each task is contained in its own directory, with the following structure:

```
[Jupyter Directory] /
    afd_profile.py
    Fraud_Detector_Data_Profiling.ipynb
    templates/
```

## License
This library is licensed under the MIT-0 License. See the LICENSE file.
