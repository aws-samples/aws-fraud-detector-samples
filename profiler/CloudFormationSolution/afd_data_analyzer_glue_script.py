import urllib3
import numpy as np
import pandas as pd
import awswrangler as wr
from awsglue.utils import getResolvedOptions
import boto3
import os
import json
import math
import re
import sys
import csv
from jinja2 import Environment, PackageLoader, FileSystemLoader

import itertools
from pandas import DataFrame, Series


DATE_FORMATS = [
    '%m/%d/%Y',
    '%m/%d/%Y',
    '%Y/%m/%d',
    '%m-%d-%Y',
    '%m-%d-%Y',
    '%Y-%m-%d',
]

TIME_FORMATS = [
    '%I:%M:%S.%f %p',
    '%I:%M:%S %p',
    '%I:%M %p',
    '%H:%M:%S.%f',
    '%H:%M:%S',
    '%H:%M',
]

SPECIAL_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%f"
]

SUPPORTED_FORMATS = []
SUPPORTED_FORMATS += DATE_FORMATS
SUPPORTED_FORMATS += [f'{d} {t}' for d, t in itertools.product(DATE_FORMATS, TIME_FORMATS)]
SUPPORTED_FORMATS += SPECIAL_FORMATS

# make it consistent with validation container
email_regex = """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
ip_regex = "((^\\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\\s*$)|(^\\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)){3}))|:)))(%.+)?\\s*$))"


def get_type_family_raw(dtype) -> str:
    """From dtype, gets the dtype family."""
    try:
        if dtype.name == 'category':
            return 'category'
        if 'datetime' in dtype.name:
            return 'datetime'
        elif np.issubdtype(dtype, np.integer):
            return 'int'
        elif np.issubdtype(dtype, np.floating):
            return 'float'
    except Exception as err:
        print(f'Warning: dtype {dtype} is not recognized as a valid dtype by numpy! AFD may incorrectly handle this feature...')

    if dtype.name in ['bool', 'bool_']:
        return 'bool'
    elif dtype.name in ['str', 'string', 'object']:
        return 'object'
    else:
        return dtype.name

# Raw dtypes (Real dtypes family)
def get_type_map_raw(df: DataFrame) -> dict:
    features_types = df.dtypes.to_dict()
    return {k: get_type_family_raw(v) for k, v in features_types.items()}


def get_type_map_special(X: DataFrame) -> dict:
    type_map_special = {}
    for column in X:
        type_special = get_type_special(X[column])
        if type_special is not None:
            type_map_special[column] = type_special
    return type_map_special


def get_type_special(X: Series) -> str:
    if check_if_datetime_as_object_feature(X):
        type_special = 'datetime'
    elif check_if_nlp_feature(X):
        type_special = 'text'
    elif check_if_regex_feature(X, email_regex):
        type_special = 'EMAIL_ADDRESS'
    elif check_if_regex_feature(X, ip_regex):
        type_special = 'IP_ADDRESS'
    else:    
        type_special = None
    return type_special


def check_if_datetime_as_object_feature(X: Series) -> bool:
    type_family = get_type_family_raw(X.dtype)

    if X.isnull().all():    
        return False
    if type_family != 'object':  # TODO: seconds from epoch support
        return False
    try:
        pd.to_numeric(X)
    except:
        try:
            if len(X) > 500:
                # Sample to speed-up type inference
                X = X.sample(n=500, random_state=0)
            
            result = pd.DataFrame(columns=['format', 'mismatch_rate'])
            for fm in SUPPORTED_FORMATS:
                result = result.append({'format':fm, 
                                        'mismatch_rate':pd.to_datetime(X, format = fm, errors='coerce').isnull().mean()},
                                        ignore_index=True)        
            if result['mismatch_rate'].min() > 0.8:  # If over 80% of the rows are NaN
                return False
            return True
        except:
            return False


def check_if_nlp_feature(X: Series) -> bool:
    type_family = get_type_family_raw(X.dtype)
    if type_family != 'object':
        return False
    if len(X) > 5000:
        # Sample to speed-up type inference
        X = X.sample(n=5000, random_state=0)
    X_unique = X.unique()
    num_unique = len(X_unique)
    num_rows = len(X)
    unique_ratio = num_unique / num_rows
    if unique_ratio <= 0.01:
        return False
    try:
        avg_words = Series(X_unique).str.split().str.len().mean()
    except AttributeError:
        return False
    if avg_words < 3:
        return False


# check if the column is email/ip by regex
def check_if_regex_feature(X:Series, regex:str) -> bool:
    dtype = get_type_family_raw(X.dtype)
    if dtype not in ['category', 'object']:
        return False
    
    X = X.dropna()
    if len(X) > 100:
        # Sample to speed-up type inference
        X = X.sample(n=100, random_state=0)
    match = X.str.match(regex).all()    
    return match   


def save_file_from_url(url,local_name):
    # Load HTML templates from Github
    http_glue = urllib3.PoolManager()
    remote_file = http_glue.request('GET', url)
    with open(local_name, 'wb') as outfile:
        outfile.write(remote_file.data)
    return local_name

# --- functions ---
def get_config(config):
    """ convert json config file into a python dict  """
    with open(config, 'r') as f:
        config_dict = json.load(f)[0]
    return config_dict

# -- load data --
def get_dataframe(config):
    """ load csv into python dataframe """
    if type(config['input_file'])==pd.DataFrame:
        return config['input_file']
    else:
        df = pd.read_csv(config['input_file'], low_memory=False)
    return df

# -- 
def get_overview(config, df):
    """ return details of the dataframe and any issues found  """
    overview_msg = {}
    df = df.copy()
    column_cnt = len(df.columns)
    try:
        df['EVENT_TIMESTAMP'] = pd.to_datetime(df[config['required_features']['EVENT_TIMESTAMP']], infer_datetime_format=True)
        date_range = df['EVENT_TIMESTAMP'].min().strftime('%Y-%m-%d') + ' to ' + df['EVENT_TIMESTAMP'].max().strftime('%Y-%m-%d')
        day_cnt = (df['EVENT_TIMESTAMP'].max() - df['EVENT_TIMESTAMP'].min()).days 
    except:
        overview_msg[config['required_features']['EVENT_TIMESTAMP']] = " Unable to convert" + config['required_features']['EVENT_TIMESTAMP'] + " to timestamp"
        date_range = ""
        day_cnt = 0 
       
    record_cnt  = df.shape[0]
    memory_size = df.memory_usage(index=True).sum()
    record_size = round(float(memory_size) / record_cnt,2)
    n_dupe      = record_cnt - len(df.drop_duplicates())

    if record_cnt <= 10000:
        overview_msg["Record count"] = "A minimum of 10,000 rows are required to train the model, your dataset contains " + str(record_cnt)

    overview_stats = {
        "Record count"      : "{:,}".format(record_cnt) ,
        "Column count"      : "{:,}".format(column_cnt),
        "Duplicate count"   : "{:,}".format(n_dupe),
        "Memory size"       : "{:.2f}".format(memory_size/1024**2) + " MB",
        "Record size"       : "{:,}".format(record_size) + " bytes",
        "Date range"        : date_range,
        "Day count"         : "{:,}".format(day_cnt) + " days",
        "overview_msg"      : overview_msg,
        "overview_cnt"      : len(overview_msg)
    }

    return df, overview_stats

def set_feature(row, config):

    feature = ""
    message_uniq, message_null, action = "", "", ""
    required_features = config['required_features']

    # date type to variable type map
    dtype_to_vtype_map = {
        'category': 'CATEGORY',
        'object': 'CATEGORY',
        'int': 'NUMERIC',
        'float': 'NUMERIC',
        'text': 'TEXT',
        'datetime': 'DATETIME',
        'EMAIL_ADDRESS': 'EMAIL_ADDRESS',
        'IP_ADDRESS': 'IP_ADDRESS',
        'PHONE_NUMBER': 'PHONE_NUMBER'
    }
    
    feature = dtype_to_vtype_map[row._dtype]

    if row._column == required_features['EVENT_TIMESTAMP']:
        feature = "EVENT_TIMESTAMP"
    if row._column == required_features['ORIGINAL_LABEL']:
        feature = "EVENT_LABEL"
    
    # -- variable warnings -- 
    if feature == 'CATEGORY' and row['nunique'] < 2:
        message_uniq, action = "GT 1 UNIQUE VALUE", "EXCLUDE"
    elif feature in ['EMAIL_ADDRESS', 'IP_ADDRESS'] and row['nunique'] < 100:
        message_uniq, action = "GT <100 UNIQUE VALUE", "EXCLUDE"

    if row.null_pct > 0.9 and feature not in ['EMAIL_ADDRESS', 'IP_ADDRESS']:
        message_null, action = "GT >90% MISSING", "EXCLUDE"
    elif row.null_pct > 0.75 and feature in ['EMAIL_ADDRESS', 'IP_ADDRESS']:
        message_null, action = "GT >75% MISSING", "EXCLUDE"
    elif row.null_pct > 0.2:
        message_null = "GT >20% MISSING"

    message = '; '.join([message_uniq, message_null, action]).lstrip(';')
    message = None if len(message) < 4 else message

    return feature, message
  

def get_label(config, df):
    """ returns stats on the label and performs intial label checks  """
    message = {}
    label = config['required_features']['ORIGINAL_LABEL']
    label_summary = df[label].value_counts()
    legit_label = str(label_summary.idxmax())
    fraud_labels = [str(i) for i in label_summary.keys() if str(i)!=legit_label]
    fraud_counts = (df['AFD_LABEL']=='fraud').sum()
    rowcnt = df.shape[0]
    label_dict = {
        "label_field"  : label,
        "label_values" : df[label].unique(),
        "label_dtype"  : label_summary.dtype,
        "fraud_rate"   : "{:.2f}".format((fraud_counts/label_summary.sum())*100),
        "fraud_label": ','.join(fraud_labels),
        "fraud_count": fraud_counts,
        "legit_rate" : "{:.2f}".format((label_summary.max()/label_summary.sum())*100),
        "legit_count": label_summary.max(),
        "legit_label": str(label_summary.idxmax()),
        "null_count" : "{:,}".format(df[label].isnull().sum(axis = 0)),
        "null_rate"  : "{:.2f}".format(df[label].isnull().sum(axis = 0)/rowcnt),
    }
    
    """
    label checks
    """
    if label_dict['fraud_count'] <= 500:
        message['fraud_count'] = "Fraud count " + str(label_dict['fraud_count']) + " is less than 500\n"
    
    if df[label].isnull().sum(axis = 0)/rowcnt >= 0.01:
        message['label_nulls'] =   "Your LABEL column contains  " + label_dict["null_count"] +" a significant number of null values"
    
    label_dict['warnings'] = len(message)
    
    return label_dict, message

def get_partition(config, df):
    """ evaluates your dataset partitions and checks the distribution of fraud lables """
   
    df = df.copy()
    row_count = df.shape[0]
    required_features = config['required_features']
    message = {}
    stats ={}
    try:
        df['_event_timestamp'] = pd.to_datetime(df[required_features['EVENT_TIMESTAMP']])
        df['_dt'] = pd.to_datetime(df['_event_timestamp'].dt.date)
    except:
        message['_event_timestamp'] = "could not parse " + required_features['EVENT_TIMESTAMP'] + " into a date or timestamp object"
        df['_event_timestamp'] = df[required_features['EVENT_TIMESTAMP']]
        df['_dt'] = df['_event_timestamp']
    
    label_summary = df[required_features['EVENT_LABEL']].value_counts()
     
    legit_label = 'legit' 
    fraud_label = 'fraud' 
    
    df = df.sort_values(by=['_event_timestamp']).reset_index(drop=True)
    ctab = pd.crosstab(df['_dt'].astype(str), df[required_features['EVENT_LABEL']]).reset_index()
    stats['labels'] = ctab['_dt'].tolist()
    stats['legit_rates'] = ctab[legit_label].tolist()
    stats['fraud_rates'] = ctab[fraud_label].tolist()
    
    # -- set partitions -- 
    df['partition'] = 'training'
    df.loc[math.ceil(row_count*.7):math.ceil(row_count*.85),'partition'] = 'evaluation'
    df.loc[math.ceil(row_count*.85):,'partition'] = 'testing'
    
    message = ""
    
    return stats, message 

def get_stats(config, df):
    """ generates the key column analysis statistics calls set_features function """
    df = df.copy().drop(columns='AFD_LABEL')
    rowcnt = len(df)
    df_s1  = df.agg(['count', 'nunique',]).transpose().reset_index().rename(columns={"index":"_column"})
    df_s1['count'] = df_s1['count'].astype('int64')
    df_s1['nunique'] = df_s1['nunique'].astype('int64')
    df_s1["null"] = (rowcnt - df_s1["count"]).astype('int64')
    df_s1["not_null"] = rowcnt - df_s1["null"]
    df_s1["null_pct"] = df_s1["null"] / rowcnt
    df_s1["nunique_pct"] = df_s1['nunique'] / rowcnt

    type_map_raw = get_type_map_raw(df)
    type_map_special = get_type_map_special(df)
    type_map_raw.update(type_map_special)
    dt = pd.DataFrame.from_dict(type_map_raw, orient='index').reset_index().rename(columns={"index":"_column", 0:"_dtype"})
    
    df_stats = pd.merge(dt, df_s1, on='_column', how='inner')
    df_stats = df_stats.round(4)
    df_stats[['_feature', '_message']] = df_stats.apply(lambda x: set_feature(x,config), axis = 1, result_type="expand")
    
    return df_stats, df_stats.dropna(subset=['_message'])

def get_email(config, df):
    """ gets the email statisitcs and performs email checks """
    message = {}
    required_features = config['required_features']
    email = required_features['EMAIL_ADDRESS']
    email_recs = df.shape[0]
    email_null = df[email].isna().sum()
    emails = pd.Series(pd.unique(df[email].values))
    email_unique  = len(emails)
    email_valid = df[email].str.count('\w+\@\w+').sum()
    email_invalid = email_recs - ( email_valid + email_null) 

    df['domain'] = df[email].str.split('@').str[1]
    top_10 = df['domain'].value_counts().head(10)
    top_dict = top_10.to_dict()
    
    label_summary = df[required_features['EVENT_LABEL']].value_counts()
    fraud_label   = 'fraud'
    legit_label   = 'legit'
    
    ctab = pd.crosstab(df['domain'], df[required_features['EVENT_LABEL']],).reset_index()
    ctab['tot'] = ctab[fraud_label] + ctab[legit_label]
    ctab['fraud_rate'] = ctab[fraud_label]/ctab['tot'] 
    ctab = ctab.sort_values(['tot'],ascending=False)
    top_n= ctab.head(10)
    
    domain_count = df['domain'].nunique()
    domain_list = top_n['domain'].tolist()
    domain_fraud = top_n[fraud_label].tolist()
    domain_legit = top_n[legit_label].tolist()
    
    # -- email checks --
    if email_unique <= 100: 
        message['unique_count'] = "Low number of unique emails: " + str(email_unique)
        
    if email_null/len(df) >= 0.20:
        message['null_email'] = "High percentage of null emails: " + '{0: >#016.2f}'.format(email_null/len(df)) + "%"
        
    if email_invalid/len(df) >= 0.5:
        message['invalid_email'] = "High number of invalid emails: " + '{0: >#016.2f}'.format(email_invalid/len(df)) + "%"
    
    domain_list = list(top_dict.keys())
    #domain_value = list(top_dict.values())
    
    email_dict = {
        "email_addr"    : email,
        "email_recs"    : "{:,}".format(email_recs),
        "email_null"    : "{:,}".format(email_null),
        "email_pctnull" : "{:.2f}".format((email_null/email_recs)*100),
        "email_unique"  : "{:,}".format(email_unique),
        "email_pctunq"  : "{:.2f}".format((email_unique/email_recs)*100),
        "email_valid"   : "{:,}".format(email_valid),
        "email_invalid" : "{:,}".format(email_invalid),
        "email_warnings": len(message),
        "domain_count"  : "{:,}".format(domain_count),
        "domain_list"   : domain_list,
        "domain_fraud"  : domain_fraud,
        "domain_legit"  : domain_legit
    }
    
    return email_dict, message
def valid_ip(ip):
    """ checks to insure we have a valid ip address """
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) < 256 for part in parts)
    except ValueError:
        return False # one of the 'parts' not convertible to integer
    except (AttributeError, TypeError):
        return False # `ip` isn't even a string
        
def get_ip_address(config, df):
    """ gets ip address statisitcs and performs ip address checks """
    message = {}
    required_features = config['required_features']
    ip = required_features['IP_ADDRESS']
    ip_recs = df.shape[0] - df[ip].isna().sum()
    ip_null = df[ip].isna().sum()
    ips = pd.Series(pd.unique(df[ip].values))
    ip_unique  = len(ips)
    df['_ip'] = df[ip].apply(valid_ip)
    ip_valid = df['_ip'].sum()
    ip_invalid = ip_recs - ip_valid
    print(ip_null)
    label_summary = df[required_features['EVENT_LABEL']].value_counts()
    fraud_label   = 'fraud'
    legit_label   = 'legit'
    
    ctab = pd.crosstab(df[required_features['IP_ADDRESS']], df[required_features['EVENT_LABEL']],).reset_index()
    
    ctab['tot'] = ctab[fraud_label] + ctab[legit_label]
    ctab['fraud_rate'] = ctab[fraud_label]/ctab['tot'] 
    ctab = ctab.sort_values(['tot'],ascending=False)
    top_n= ctab.head(10)
    
    ip_list = top_n[ip].tolist()
    ip_fraud = top_n[fraud_label].tolist()
    ip_legit = top_n[legit_label].tolist()
    
    # -- ip checks --
    if ip_unique <= 100: 
        message['unique_count'] = "Low number of unique ip addresses: " + str(ip_unique)
        
    if ip_null/len(df) >= 0.20:
        message['null_ip'] = "High percentage of null ip addresses: " + '{0: >#016.2f}'.format(ip_null/len(df)) + "%"
        
    if ip_invalid/len(df) >= 0.5:
        message['invalid_ip'] = "High number of invalid ip addresses: " + '{0: >#016.2f}'.format(ip_invalid/len(df)) + "%"
    
    ip_dict = {
        "ip_addr"    : ip,
        "ip_recs"    : "{:,}".format(ip_recs),
        "ip_null"    : "{:,}".format(ip_null),
        "ip_pctnull" : "{:.2f}".format((ip_null/ip_recs)*100),
        "ip_unique"  : "{:,}".format(ip_unique),
        "ip_pctunq"  : "{:.2f}".format((ip_unique/ip_recs)*100),
        "ip_valid"   : "{:,}".format(ip_valid),
        "ip_invalid" : "{:,}".format(ip_invalid), 
        "ip_warnings": len(message),
        "ip_list"   : ip_list,
        "ip_fraud"  : ip_fraud,
        "ip_legit"  : ip_legit
    }
    
    return ip_dict, message

def col_stats(df, target, column):
    """ generates column statisitcs for categorical columns """
    legit = 'legit'
    fraud = 'fraud'
    try:
        cat_summary = pd.crosstab(df[column],df[target]).reset_index().sort_values(fraud, ascending=False).reset_index(drop=True).head(10).rename(columns={legit:"legit", fraud:"fraud"})
        cat_summary['total'] = cat_summary['fraud'] + cat_summary['legit']
        cat_summary['fraud_pct'] = cat_summary['fraud']/(cat_summary['fraud']+ cat_summary['legit'])
        cat_summary['legit_pct'] = 1 - cat_summary['fraud_pct']
        cat_summary = cat_summary.sort_values('fraud_pct', ascending=False).round(4)
    except:
        cat_summary = pd.crosstab(df[column],df[target]).reset_index().sort_values(legit, ascending=True).reset_index(drop=True).head(10).rename(columns={legit:"legit", fraud:"fraud"})
        cat_summary['fraud'] = 0
        cat_summary['total'] = cat_summary['legit']
        cat_summary['fraud_pct'] = 0.0
        cat_summary['legit_pct'] = 1 - cat_summary['fraud_pct']
        cat_summary = cat_summary.sort_values('fraud_pct', ascending=False).round(4)
    return cat_summary  
    
def get_categorical(config, df_stats, df):
    """ gets categorical feature stats: count, nunique, nulls  """
    required_features = config['required_features']
    features = df_stats.loc[df_stats['_feature'].isin(['CATEGORY','IP_ADDRESS','EMAIL_ADDRESS','TEXT','PHONE_NUMBER'])]._column.tolist()
    target = required_features['EVENT_LABEL']
    df = df[features + [target]].copy()
    rowcnt = len(df)
    df_s1  = df.agg(['count', 'nunique',]).transpose().reset_index().rename(columns={"index":"_column"})
    df_s1['count'] = df_s1['count'].astype('int64')
    df_s1['nunique'] = df_s1['nunique'].astype('int64')
    df_s1["null"] = (rowcnt - df_s1["count"]).astype('int64')
    df_s1["not_null"] = rowcnt - df_s1["null"]
    df_s1["null_pct"] = df_s1["null"] / rowcnt
    df_s1["nunique_pct"] = df_s1['nunique'] / rowcnt
    dt = pd.DataFrame(df.dtypes).reset_index().rename(columns={"index":"_column", 0:"_dtype"})
    df_stats = pd.merge(dt, df_s1, on='_column', how='inner').round(4)
 
    cat_list = []
    for rec in df_stats.to_dict('records'):
        if rec['_column'] != target:
            cat_summary = col_stats(df, target, rec['_column'])
            rec['top_n'] = cat_summary[rec['_column']].tolist()
            rec['top_n_count'] = cat_summary['total'].tolist()
            rec['fraud_pct'] = cat_summary['fraud_pct'].tolist()
            rec['legit_pct'] = cat_summary['legit_pct'].tolist()
            rec['fraud_count'] = cat_summary['fraud'].tolist()
            rec['legit_count'] = cat_summary['legit'].tolist()
            cat_list.append(rec)
 
    return cat_list

def ncol_stats(df, target, column):
    """ calcuates numeric column statstiics """
    df = df.copy()
    n = df[column].nunique()
    # -- rice rule -- 
    k = int(round(2*(n**(1/3)),0)) 
    # -- bin that mofo -- 
    try:
        df['bin'] = pd.qcut(df[column], q=k, duplicates='drop')
        legit = 'legit'
        fraud = 'fraud'
        try:
            num_summary = pd.crosstab(df['bin'],df[target]).reset_index().rename(columns={legit:"legit", fraud:"fraud"})
            num_summary['total'] = num_summary['fraud'] + num_summary['legit']
            num_summary['empty_label'] = [""] * df['bin'].nunique()
            num_summary['bin_label'] = num_summary['bin'].astype(str)
        except:
            num_summary = pd.crosstab(df['bin'],df[target]).reset_index().rename(columns={legit:"legit", fraud:"fraud"})
            num_summary['fraud'] = 0
            num_summary['total'] = num_summary['legit']
            num_summary['empty_label'] = [""] * df['bin'].nunique()
            num_summary['bin_label'] = num_summary['bin'].astype(str)
    except:
        num_summary = pd.DataFrame()
        num_summary['legit'] = 0
        num_summary['fraud'] = 0
        num_summary['total'] = 0
        num_summary['empty_label'] = [""]
        num_summary['bin_label'] = [""]

    return num_summary  
    
def get_numerics( config, df_stats, df):
    """ gets numeric feature descriptive statsitics and graph detalis """
    required_features = config['required_features']
    features = df_stats.loc[df_stats['_feature']=='NUMERIC']._column.tolist()
    target = required_features['EVENT_LABEL']

    df = df[features + [target]].copy()
    rowcnt = len(df)
    df_s1  = df.agg(['count', 'nunique','mean','min','max']).transpose().reset_index().rename(columns={"index":"_column"})
    df_s1['count'] = df_s1['count'].astype('int64')
    df_s1['nunique'] = df_s1['nunique'].astype('int64')
    df_s1["null"] = (rowcnt - df_s1["count"]).astype('int64')
    df_s1["not_null"] = rowcnt - df_s1["null"]
    df_s1["null_pct"] = df_s1["null"] / rowcnt
    df_s1["nunique_pct"] = df_s1['nunique'] / rowcnt
    dt = pd.DataFrame(df.dtypes).reset_index().rename(columns={"index":"_column", 0:"_dtype"})
    df_stats = pd.merge(dt, df_s1, on='_column', how='inner').round(4)
    num_list = []
    for rec in df_stats.to_dict('records'):
        if rec['_column'] != target and rec['count'] > 1:
            n_summary = ncol_stats(df, target, rec['_column'])
            rec['bin_label'] = n_summary['bin_label'].tolist()
            rec['legit_count'] = n_summary['legit'].tolist()
            rec['fraud_count'] = n_summary['fraud'].tolist()
            rec['total'] = n_summary['total'].tolist()
            rec['empty_label'] = n_summary['empty_label'].tolist()
            num_list.append(rec)
 
    return num_list

def profile_report(config):
    """ main function - generates the profile report of the CSV """
    # -- Jinja2 environment -- 
    env = Environment(loader=FileSystemLoader("templates")) #PackageLoader('afd_profile', 'templates'))
    profile= env.get_template('profile.html')
    
    # -- all the checks -- 
    required_features = config['required_features']
    df = get_dataframe(config)
    df, overview_stats = get_overview(config, df)
    df_stats, warnings = get_stats(config, df)
    lbl_stats, lbl_warnings = get_label(config, df)
    p_stats, p_warnings = get_partition(config, df)
    if 'EMAIL_ADDRESS' in required_features:        
        e_stats, e_warnings = get_email(config, df)
    else:
        e_stats, e_warnings = None, None
    if 'IP_ADDRESS' in required_features:       
        i_stats, i_warnings = get_ip_address(config, df)
    else:
        i_stats, i_warnings = None, None
    cat_rec = get_categorical(config, df_stats, df)
    num_rec = get_numerics( config, df_stats, df)
    
    # -- render the report 
    profile_results = profile.render(file = config['file_name'], 
                                     overview = overview_stats,
                                     warnings = warnings,
                                     df_stats=df_stats.loc[df_stats['_feature'] != 'exclude'],
                                     label  = lbl_stats,
                                     label_msg = lbl_warnings,
                                     p_stats=p_stats,
                                     p_warnings = p_warnings,
                                     e_stats = e_stats,
                                     e_warnings = e_warnings,
                                     i_stats=i_stats,
                                     i_warnings=i_warnings,
                                     cat_rec=cat_rec,
                                     num_rec=num_rec) 
    return profile_results
    
def convert_dtypes(df,label_col):
    prog = re.compile(r'[\-]?[0-9]*[\.]?[0-9]*')
    for c in df.columns:
        if c==label_col:
            continue
        else:
            non_numeric_count = df[c].astype(str).apply(lambda x: re.fullmatch(prog,x)==None).sum()
            if non_numeric_count==0:
                df[c] = df[c].astype('float64')
            else:
                print(f'Column {c} has {non_numeric_count} non-numeric rows.')
    return df

def convert_labels(df,label_col):
    label_summary = df[label_col].value_counts()
    legit_label = label_summary.idxmax()
    fraud_labels = [i for i in label_summary.keys() if i!=legit_label]
    df['AFD_LABEL'] = 'legit'
    df.loc[df[label_col].isin(fraud_labels),'AFD_LABEL'] = 'fraud'
    df.loc[df[label_col].isna(),'AFD_LABEL'] = np.nan
    return df

# Read Glue job parameters
job_args = getResolvedOptions(sys.argv, ["CSVFilePath","FileDelimiter","EventTimestampColumn","LabelColumn","CleanCSV","ProfileCSV"])
file_path = job_args['CSVFilePath']
delimiter= job_args['FileDelimiter']
EventTimestampCol= job_args['EventTimestampColumn']
LabelCol= job_args['LabelColumn']
CleanCSV = (job_args['CleanCSV']=='Yes')
ProfileCSV = (job_args['ProfileCSV']=='Yes')

html_templates = ['https://raw.githubusercontent.com/aws-samples/aws-fraud-detector-samples/master/profiler/templates/profile.html',
'https://raw.githubusercontent.com/aws-samples/aws-fraud-detector-samples/master/profiler/templates/profile_categorical.html',
'https://raw.githubusercontent.com/aws-samples/aws-fraud-detector-samples/master/profiler/templates/profile_df.html',
'https://raw.githubusercontent.com/aws-samples/aws-fraud-detector-samples/master/profiler/templates/profile_email.html',
'https://raw.githubusercontent.com/aws-samples/aws-fraud-detector-samples/master/profiler/templates/profile_ip.html',
'https://raw.githubusercontent.com/aws-samples/aws-fraud-detector-samples/master/profiler/templates/profile_label.html',
'https://raw.githubusercontent.com/aws-samples/aws-fraud-detector-samples/master/profiler/templates/profile_messages.html',
'https://raw.githubusercontent.com/aws-samples/aws-fraud-detector-samples/master/profiler/templates/profile_numeric.html',
'https://raw.githubusercontent.com/aws-samples/aws-fraud-detector-samples/master/profiler/templates/profile_overview.html',
'https://raw.githubusercontent.com/aws-samples/aws-fraud-detector-samples/master/profiler/templates/profile_partition.html']

# Parse S3 path
path_parts=file_path.replace("s3://","").split("/")
bucket = path_parts.pop(0)
file_prefix = path_parts[:-1]
file_name = path_parts[-1]


# Load html templates
print('Loading HTML templates.')
os.mkdir("templates")
for item in html_templates:
    _local_file = 'templates/'+item.split('/')[-1]
    print(save_file_from_url(item,_local_file))
    

# Read csv file
print('Reading CSV file.')
if delimiter=='':
    delimiter=','
df = wr.s3.read_csv(path=file_path, dtype=object, sep=delimiter)

if CleanCSV==True:
    print('Cleaning CSV.')
    # Convert timestamp to required format
    print('Transforming datetime.')
    df[EventTimestampCol] = pd.to_datetime(df[EventTimestampCol]).apply(lambda x: x.strftime("%Y-%m-%dT%H:%M:%SZ"))

    # Convert label values to lower cases and remove spaces
    print('Converting labels.')
    df.loc[~df[LabelCol].isna(),LabelCol] = df[~df[LabelCol].isna()][LabelCol].astype(str).str.lower().str.replace(r'[^a-z0-9]+', '_', regex=True)

    # Convert headers
    print('Converting headers')
    dfc = {EventTimestampCol:'EVENT_TIMESTAMP',LabelCol:'EVENT_LABEL'}                      
    for c in df.columns:
        if c not in dfc.keys():
            # Convert header to lower cases and remove spaces
            dfc[c] = re.sub(r'[^a-z0-9]+', '_', c.lower())
    df.rename(columns=dfc,inplace=True)
    EventTimestampCol = 'EVENT_TIMESTAMP'
    LabelCol = 'EVENT_LABEL'
    cleaned_file = '/'.join(file_prefix+['afd_data_'+file_name.split('.')[0],'cleaned_'+file_name])
    cleaned_file = f's3://{bucket}/{cleaned_file}'
    print(f'Saving cleaned file to: {cleaned_file}')
    wr.s3.to_csv(df=df, path=cleaned_file, index=False)

if ProfileCSV==True:
    print('Generating data profiler.')
    # Convert df type
    df = convert_dtypes(df,LabelCol)  

    # Convert labels: add a column AFD_LABEL with values legit and fraud. 
    df = convert_labels(df,LabelCol)

    # Update configuration
    config = {  
        "file_name":file_path,
        "input_file"        : df,
        "required_features" : {
            "EVENT_TIMESTAMP" : EventTimestampCol,
            "ORIGINAL_LABEL": LabelCol,
            "EVENT_LABEL"     : 'AFD_LABEL',
        }
    }

    # Generate report
    report = profile_report(config)

    # Save report to S3 bucket
    with open("report.html", "w") as file:
        file.write(report)
    s3_client = boto3.client('s3')
    profiler_path = '/'.join(file_prefix+['afd_data_'+file_name.split('.')[0],'report.html'])
    print(f'Saving data profiler to: s3://{bucket}/{profiler_path}')
    response = s3_client.upload_file("report.html", bucket, profiler_path)

print('Done.')

