
## About this notebook

This notebook provides an example of how to configure and run the data profiling notebook. Fraud_Detector_Data Profling.ipynb is the notebook that performs the profiling. afd_profile.py is the python package which will generate your profile report.  /templates is the directory that contains the supporting profile templates. Make sure your directory contains the notebook, afd_profile.py, and the templates directory.

Instructions:
1. download the [afd_profile.py](afd_profile.py)  to your jupyter notebook, and the templates directory to your notebook. afd_profile.py contains functions to perform the profiling and the /templates directory contains .html templates to present the profile report. 
2. dowload the [Fraud_Detector_Data_Profiling.ipynb](Fraud_Detector_Data_Profiling.ipynb) to your jupyter notebook 
3. configure the notebook to point to your data, and identify the key fields
4. run your notebook, review the report.html that is produced. 

Samples:
[Fraud Detector Data Profiling-Sample_Results.ipynb](Fraud_Detector_Data_Profiling-Sample_Results.ipynb) - contains a sample result of running the data profiling notebook on the sample dataset **synthitic_newaccount_data_50k.csv** and the [report.html](report.html) contains a sample data profiling report. 

Each task is contained in its own directory, with the following structure:

```
[Jupyter Directory] /
    afd_profile.py
    Fraud_Detector_Data_Profiling.ipynb
    templates/
```

## License
This library is licensed under the MIT-0 License. See the LICENSE file.
