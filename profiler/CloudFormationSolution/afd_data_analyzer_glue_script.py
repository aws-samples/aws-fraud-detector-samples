import urllib3
import numpy as np
import pandas as pd
import awswrangler as wr
from awsglue.utils import getResolvedOptions
import boto3
import os
import json
import re
import sys
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
import itertools
from pandas import DataFrame, Series
import scipy.stats as ss
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s :: %(asctime)s.%(msecs)03d :: %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

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
        logging.info(f'Warning: dtype {dtype} is not recognized as a valid dtype by numpy! AFD may incorrectly handle this feature...')

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
            if len(X) > 5000:
                # Sample to speed-up type inference
                X = X.sample(n=5000, random_state=0)
            
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
    return True


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

# -- Data overview -- 
def get_overview(config, df):
    """ return details of the dataframe and any issues found  """
    overview_msg = {}
    df = df.copy()    
    label = config['required_features']['EVENT_LABEL']
    df.loc[~df[label].isna(),label] = df.loc[~df[label].isna(),label].astype(str)
    
    column_cnt = len(df.columns)
    _timestamp_col = pd.to_datetime(df[config['required_features']['EVENT_TIMESTAMP']], 'coerce').dropna()
    if _timestamp_col.shape[0]>0:
        date_range = _timestamp_col.min().strftime('%Y-%m-%d') + ' to ' + _timestamp_col.max().strftime('%Y-%m-%d')
        day_cnt = (_timestamp_col.max() - _timestamp_col.min()).days 
    else:
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
        "overview_cnt"      : len(overview_msg),
        "Majority_label"    : f'''\'{config['MAJORITY_CLASS']}\'''',
        "Mapped_fraud"    : config['MAPPED_FRAUD'],
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
        message_uniq, action = "ONLY 1 UNIQUE VALUE", "EXCLUDE"
    elif feature in ['EMAIL_ADDRESS', 'IP_ADDRESS'] and row['nunique'] < 100:
        message_uniq, action = "<100 UNIQUE VALUE", "EXCLUDE"

    if row.null_pct > 0.9 and feature not in ['EMAIL_ADDRESS', 'IP_ADDRESS']:
        message_null, action = ">90% MISSING", "EXCLUDE"
    elif row.null_pct > 0.75 and feature in ['EMAIL_ADDRESS', 'IP_ADDRESS']:
        message_null, action = ">75% MISSING", "EXCLUDE"
    elif row.null_pct > 0.2:
        message_null = ">20% MISSING"

    message = '; '.join([message_uniq, message_null, action]).lstrip(';')
    message = None if len(message) < 4 else message

    return feature, message
  
def get_label(config, df):
    """ returns stats on the label and performs intial label checks  """
    _original_label_col = config['required_features']['ORIGINAL_LABEL']
    _mappled_label_col = config['required_features']['EVENT_LABEL']
    _mapped_fraud = config['MAPPED_FRAUD']
    # Label values of original label
    labels = df[_original_label_col].value_counts().keys().tolist()
    missing_count = 0
    label_dict = {}
    for c in df[_original_label_col].unique():
        if pd.isna(c):
            # Missing labels
            _df = df[df[_original_label_col].isna()][_original_label_col]
            label_dict['Missing Labels'] = {
                'Name':'Missing Labels',
                'CLS':'Undefined',
                'Count':_df.shape[0],
                'Percentage': '{:.2f}%'.format(100*_df.shape[0]/df.shape[0]),
            }
            missing_count = _df.shape[0]
        else:
            _df = df[df[_original_label_col]==c][_original_label_col]
            if _mapped_fraud:
                _mappled_label = df[df[_original_label_col]==c][_mappled_label_col].iloc[0]
            else:
                _mappled_label = 'Undefined'
            label_dict[c] = {
                'Name':c,
                'CLS':_mappled_label,
                'Count':_df.shape[0],
                'Percentage': '{:.2f}%'.format(100*_df.shape[0]/df.shape[0]),
            }
    
    label_dict = pd.DataFrame(label_dict).T
    label_dict = label_dict.sort_values('Count',ascending=False)
    # label checks
    message = {}
    message['message'] = ''
    if missing_count/df.shape[0] >= 0.01:
        message['message'] =   f"Your {_original_label_col} column contains {missing_count} missing values. AFD requires less than 1% of the values in label column are missing. Consider assigning proper labels or drop those records."
    message['length'] = len(message['message'])
    
    return label_dict, message


def get_partition(config, df):
    """ evaluates your dataset partitions and checks the distribution of fraud lables """
    df = df.copy()
    required_features = config['required_features']
    _is_mapped_fraud = config['MAPPED_FRAUD']
    _mapped_label_col = required_features['EVENT_LABEL']
    _original_label_col = required_features['ORIGINAL_LABEL']
    
    message = {}
    stats ={'mapped_labels':{},
            'original_labels':{}}
    try:
        df['_event_timestamp'] = pd.to_datetime(df[required_features['EVENT_TIMESTAMP']])
        df['_dt'] = pd.to_datetime(df['_event_timestamp'].dt.date).astype(str)
    except:
        message['_event_timestamp'] = "Could not parse " + required_features['EVENT_TIMESTAMP'] + " into a date or timestamp object for some records."
        df['_event_timestamp'] = pd.to_datetime(df[required_features['EVENT_TIMESTAMP']],'coerce')
        df = df[~df['_event_timestamp'].isna()]
        df['_dt'] = df['_event_timestamp'].dt.date.astype(str)
        
    df[_mapped_label_col] = df[_mapped_label_col].fillna('Missing Labels')
    df[_original_label_col] = df[_original_label_col].fillna('Missing Labels')

    df = df.sort_values(by=['_event_timestamp']).reset_index(drop=True)
    
    # If labels are mapped to FRAUD/NON-FRAUD in CFN, show mapped distribution
    if _is_mapped_fraud:
        ctab_mapped = df.groupby(['_dt',_mapped_label_col])[_mapped_label_col].count().unstack(fill_value=0).reset_index()
        ctab_mapped['total'] = 0

        stats['mapped_labels']['_labels'] = ctab_mapped['_dt'].tolist()
        for c in df[_mapped_label_col].unique():
            stats['mapped_labels'][c] = ctab_mapped[c].tolist()
            ctab_mapped['total'] = ctab_mapped['total'] + ctab_mapped[c]
        for c in df[_mapped_label_col].unique():
            stats['mapped_labels'][c+'_pctg'] = (ctab_mapped[c]/ctab_mapped['total']).round(4).tolist()
    
    # Distribution of original labels
    ctab_original = df.groupby(['_dt',_original_label_col])[_original_label_col].count().unstack(fill_value=0).reset_index()
    ctab_original['total'] = 0
    stats['original_labels']['_labels'] = ctab_original['_dt'].tolist()
    for c in df[_original_label_col].unique():
        stats['original_labels'][c] = ctab_original[c].tolist()
        ctab_original['total'] = ctab_original['total'] + ctab_original[c]
    for c in df[_original_label_col].unique():
        stats['original_labels'][c+'_pctg'] = (ctab_original[c]/ctab_original['total']).round(4).tolist()
    
    return stats, message 


def rename_dtypes(x):
    if x=='int':
        return 'INTEGER'
    elif x=='float':
        return 'FLOAT'
    else:
        return 'STRING'

def get_stats(config, df):
    """ generates the key column analysis statistics calls set_features function """
    type_map_raw = get_type_map_raw(df)
    type_map_special = get_type_map_special(df)
    type_map_raw.update(type_map_special)
    dt = pd.DataFrame.from_dict(type_map_raw, orient='index').reset_index().rename(columns={"index":"_column", 0:"_dtype"})
    
    if 'EMAIL_ADDRESS' in dt['_dtype'].values:
        email = dt[dt['_dtype']=='EMAIL_ADDRESS']['_column'].values.tolist()[0]
        df['_EMAIL_DOMAIN'] = df[email].str.split('@').str[1]
        dt = dt.append(pd.DataFrame([['_EMAIL_DOMAIN','object']], columns=['_column','_dtype']))
    
    rowcnt = len(df)
    df_s1  = df.agg(['count', 'nunique',]).transpose().reset_index().rename(columns={"index":"_column"})
    df_s1['count'] = df_s1['count'].astype('int64')
    df_s1['nunique'] = df_s1['nunique'].astype('int64')
    df_s1["null"] = (rowcnt - df_s1["count"]).astype('int64')
    df_s1["not_null"] = rowcnt - df_s1["null"]
    df_s1["null_pct"] = df_s1["null"] / rowcnt
    df_s1["nunique_pct"] = df_s1['nunique'] / rowcnt
    
    df_stats = pd.merge(dt, df_s1, on='_column', how='inner')
    df_stats = df_stats.round(4)
    df_stats[['_feature', '_message']] = df_stats.apply(lambda x: set_feature(x,config), axis = 1, result_type="expand")

    df_stats["_dtype"] = df_stats["_dtype"].apply(rename_dtypes)
    df_stats = df_stats[df_stats['_column']!='AFD_LABEL']

    for d in df_stats.loc[df_stats['_feature'].isin(['EVENT_TIMESTAMP','DATETIME'])]._column.tolist():
        df[d] = pd.to_datetime(df[d],'coerce')

    return df, df_stats, df_stats.dropna(subset=['_message'])

def col_stats(df, target, column, majority,MinClassCount,labels):
    """ generates column statisitcs for categorical columns """
    cat_summary = df.groupby([column,target])[target].count().unstack(fill_value=0).reset_index().sort_values(majority, ascending=True).reset_index(drop=True)
    # Total number of records
    cat_summary['total'] = 0
    sort_orders = []
    for c in labels:
        if c in cat_summary.columns:
            sort_orders.append(c)
            cat_summary['total'] = cat_summary['total'] + cat_summary[c]
    # Percentage of each label
    for c in labels:
        if c in cat_summary.columns:
            cat_summary[c+'_pctg'] = cat_summary[c]/cat_summary['total']
            
    cat_summary['pctg_minority'] = 1-cat_summary[majority+'_pctg']
    cat_summary = cat_summary[cat_summary['total']>MinClassCount]
    cat_summary["_non_majority"] = cat_summary["total"]-cat_summary[majority]
        
    # Sort options: total, # majority, # non-majority, % majority
    cat_summary_total = cat_summary.sort_values(['total']+sort_orders,ascending=False)
    cat_summary_majority = cat_summary.sort_values([majority]+sort_orders,ascending=False)
    cat_summary_non_majority = cat_summary.sort_values(['_non_majority']+sort_orders[::-1],ascending=False)
    cat_summary_pctg = cat_summary.sort_values(['pctg_minority']+[item+'_pctg' for item in sort_orders[::-1]],ascending=False)
    
    return cat_summary_total.round(4), cat_summary_majority.round(4), cat_summary_non_majority.round(4), cat_summary_pctg.round(4)

def col_stats_to_dict(_df,col_name,labels,reverse=False):
    # Convert pandas dictionary to dict for HTML render
    _rec = {
        'LABELS':_df[col_name].tolist()
    }
    _labels = labels.copy()
    if reverse:
        _labels = _labels[::-1]
    for c in _labels:
        if c in _df.columns:
            _rec[c] = _df[c].tolist()
            _rec[c+'_pctg'] = _df[c+'_pctg'].tolist()
    return _rec

def get_categorical(config, df_stats, df):
    """ gets categorical feature stats: count, nunique, nulls  """
    required_features = config['required_features']
    features = df_stats.loc[df_stats['_feature'].isin(['CATEGORY','IP_ADDRESS','EMAIL_ADDRESS','TEXT','PHONE_NUMBER'])]._column.tolist()
    if len(features)==0:
        return []
    target = required_features['EVENT_LABEL']
    labels = config['LABELS']
    majority = config['MAJORITY_CLASS']
    topN = config['TopN']
    MinClassCount = config['MinClassCount']
    # Basic statistics
    df = df[features + [target]].copy()
    rowcnt = len(df)
    df_s1  = df.agg(['count', 'nunique',]).transpose().reset_index().rename(columns={"index":"_column"})
    df_s1['count'] = df_s1['count'].astype('int64')
    df_s1['nunique'] = df_s1['nunique'].astype('int64')
    df_s1["null"] = (rowcnt - df_s1["count"]).astype('int64')
    df_s1["not_null"] = rowcnt - df_s1["null"]
    df_s1["null_pct"] = df_s1["null"] / rowcnt
    df_s1["nunique_pct"] = df_s1['nunique'] / rowcnt
    dt = df_stats[['_column','_feature']].copy()
    df_stats = pd.merge(dt, df_s1, on='_column', how='inner').round(4)
    # Distribution
    cat_list = []
    for rec in df_stats.to_dict('records'):
        if rec['_column'] != target:
            cat_summary_total, cat_summary_majority, cat_summary_non_majority, cat_summary_pctg = col_stats(df, target, rec['_column'],majority,MinClassCount,labels)
            rec['_name'] = f'''\'{rec['_column']}\''''
            rec['sort_total']=col_stats_to_dict(cat_summary_total.head(topN),rec['_column'],labels)
            rec['sort_majority']=col_stats_to_dict(cat_summary_majority.head(topN),rec['_column'],labels)
            rec['sort_nonmajority']=col_stats_to_dict(cat_summary_non_majority.head(topN),rec['_column'],labels,True)
            rec['sort_pctg']=col_stats_to_dict(cat_summary_pctg.head(topN),rec['_column'],labels)
                        
            if len(cat_summary_total)>0 and rec['nunique']!=rec['count']:
                # Do not show empty or all-unique columns, such as event_id
                rec['show_in_report'] = True
            else:
                rec['show_in_report'] = None
            cat_list.append(rec)
 
    return cat_list

def ncol_stats(df, target, column,labels):
    """ calcuates numeric column statstiics """
    df = df.copy()
    n = df[column].nunique()
    # -- rice rule -- 
    k = int(round(2*(n**(1/3)),0))
    # -- bin that mofo -- 
    try:
        df['bin'] = pd.qcut(df[column], q=k, duplicates='drop')
        num_summary = df.groupby(['bin',target])[target].count().unstack(fill_value=0).reset_index()
        # Total number of records
        num_summary['total'] = 0
        for c in num_summary.columns:
            if c in labels:
                num_summary['total'] = num_summary['total'] + num_summary[c]
        num_summary['bin_label'] = num_summary['bin'].astype(str)
    
    except:
        # Dot not show empty columns in report
        num_summary = pd.DataFrame()

    return num_summary  

def datecol_stats(df, target, column,labels):
    # Calculate datetime column statistics
    df = df.copy()
    df = df[(~df[column].isna()) & (~df[target].isna())]
    df['_dt'] = df[column].dt.date.astype(str)
    df = df.sort_values(by=[column]).reset_index(drop=True)
    num_summary = df.groupby(['_dt',target])[target].count().unstack(fill_value=0).reset_index()
    num_summary['total'] = 0
    for c in num_summary.columns:
        if c in labels:
            num_summary['total'] = num_summary['total'] + num_summary[c]
    num_summary['bin_label'] = num_summary['_dt'].astype(str)

    return num_summary

def get_numerics( config, df_stats, df):
    """ gets numeric feature descriptive statsitics and graph detalis """
    required_features = config['required_features']
    features = df_stats.loc[df_stats['_feature'].isin(['NUMERIC','DATETIME'])]._column.tolist()
    if len(features)==0:
        return []
    target = required_features['EVENT_LABEL']
    labels = config['LABELS']
    # Basic statistics
    df = df[features + [target]].copy()
    rowcnt = len(df)
    df_s1  = df[features].agg(['count', 'nunique','mean','min','max']).transpose().reset_index().rename(columns={"index":"_column"})
    df_s1['count'] = df_s1['count'].astype('int64')
    df_s1['nunique'] = df_s1['nunique'].astype('int64')
    df_s1["null"] = (rowcnt - df_s1["count"]).astype('int64')
    df_s1["not_null"] = rowcnt - df_s1["null"]
    df_s1["null_pct"] = df_s1["null"] / rowcnt
    df_s1["nunique_pct"] = df_s1['nunique'] / rowcnt
    dt = df_stats[['_column','_feature']].copy()
    df_stats = pd.merge(dt, df_s1, on='_column', how='inner').round(4)
    # Distribution
    num_list = []
    for rec in df_stats.to_dict('records'):
        if rec['_column'] != target and rec['count'] > 1:
            if rec['_feature']=='NUMERIC':
                n_summary = ncol_stats(df, target, rec['_column'],labels)
            elif rec['_feature']=='DATETIME':
                n_summary = datecol_stats(df, target, rec['_column'],labels)
            if n_summary.empty:
                continue
            rec['bin_label'] = n_summary['bin_label'].tolist()
            rec['label_count'] = {}
            rec['pctg'] = {}
            
            for c in n_summary.columns:
                if c in labels:
                    rec['label_count'][c] = n_summary[c].tolist()
                    rec['pctg'][c] = (n_summary[c]/n_summary['total']).round(4).tolist()
                    
            rec['total'] = n_summary['total'].tolist()
            num_list.append(rec)
 
    return num_list

def cramers_corrected_stat(confusion_matrix):
    """ calculate Cramers V statistic for categorial-categorial association.
        uses correction from Bergsma and Wicher, 
        Journal of the Korean Statistical Society 42 (2013): 323-328
    """
    chi2 = ss.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    r,k = confusion_matrix.shape
    if n<2:
        return 0
    phi2 = chi2/n
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))    
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    if rcorr<2 or kcorr<2:
        return 0
    return np.sqrt(phi2corr / min( (kcorr-1), (rcorr-1)))

def correlation_ratio(df_cat, df_num):
    fcat, _ = pd.factorize(df_cat)
    cat_num = np.max(fcat)+1
    y_avg_array = np.zeros(cat_num)
    n_array = np.zeros(cat_num)
    for i in range(0,cat_num):
        cat_measures = df_num.iloc[np.argwhere(fcat == i).flatten()]
        n_array[i] = len(cat_measures)
        y_avg_array[i] = cat_measures.mean()
    if np.sum(n_array)==0:
        # emtpy 
        return 0
    y_total_avg = np.sum(np.multiply(y_avg_array,n_array))/np.sum(n_array)
    numerator = np.sum(np.multiply(n_array,np.power(np.subtract(y_avg_array,y_total_avg),2)))
    denominator = np.sum(np.power(np.subtract(df_num,y_total_avg),2))
    if numerator == 0:
        eta = 0.0
    else:
        eta = np.sqrt(numerator/denominator)
    return eta

def num_corr(df):
    # Compute pearson correlation between two numerical features
    return df.fillna(-999).corr(method='pearson')

def cat_corr(df):
    # Compute cramer's V between two categorical features
    if df.shape[0]>5000:
        df = df.sample(5000).fillna('<null>')
    _features = df.columns
    res = {item:{} for item in _features}
    for i in range(len(_features)):
        column1 = _features[i]
        res[column1][column1] = 1
        for j in range(i+1,len(_features)):
            column2 = _features[j]
            logging.info(f'{column1}, {column2}')
            confusion_matrix = df.groupby([column1,column2])[column2].count().unstack(fill_value=0)
            cramer_coeff = cramers_corrected_stat(confusion_matrix)
            res[column1][column2] = cramer_coeff
            res[column2][column1] = cramer_coeff
            
    return pd.DataFrame(res)

def cat_corr_with_label(df,cat_feat,target):
    # Compute cramer's V between two categorical features
    if df.shape[0]>5000:
        df = df[cat_feat+[target]].sample(5000).fillna('<null>')
    res = {}
    for column1 in cat_feat:
        logging.info(column1)
        confusion_matrix = df.groupby([column1,target])[target].count().unstack(fill_value=0)
        cramer_coeff = cramers_corrected_stat(confusion_matrix)
        res[column1] = {target: cramer_coeff}
    return pd.DataFrame(res)

def num_cat_corr(df_num,df_cat):
    # Compute correlation ratio (eta) between two numerical features
    df_num = df_num.fillna(-999)
    if df_num.shape[0]>5000:
        df_num = df_num.sample(5000)
    df_cat = df_cat.loc[df_num.index].fillna('<null>')
    res_cat = {item:{} for item in df_cat.columns}
    res_num = {}
    for column1 in df_num.columns:
        res_num[column1] = {}
        for column2 in df_cat.columns:
            logging.info(f'{column1}, {column2}')
            eta = correlation_ratio(df_cat[column2],df_num[column1])
            res_num[column1][column2] = eta
            res_cat[column2][column1] = eta
                        
    return pd.DataFrame(res_num), pd.DataFrame(res_cat)
    
    
def get_correlation( config, df_stats, df):
    """ gets correlation between numeric features and majority label class """
    df = df.copy()
    required_features = config['required_features']
    date_features = df_stats.loc[df_stats['_feature'].isin(['EVENT_TIMESTAMP','DATETIME'])]._column.tolist()
    num_features = df_stats.loc[df_stats['_feature']=='NUMERIC']._column.tolist()
    num_features = num_features + date_features
    cat_features = df_stats.loc[(df_stats['_feature'].isin(['CATEGORY','IP_ADDRESS','EMAIL_ADDRESS','TEXT','PHONE_NUMBER'])) & (df_stats['nunique_pct']<0.95)]._column.tolist()
    label_feature = required_features['ORIGINAL_LABEL']    # Treat label as categorical 
    for c in date_features:
        df.loc[~df[c].isna(),c] = (df[~df[c].isna()][c].astype(int) / 10**9).astype(int)
    
    rec_corr = {'features':[],'data_label':[],'feature_corr':None}    
    # Calculate correlation with label
    corr_num_label,_ = num_cat_corr(df[num_features],df[[label_feature]])
    corr_cat_label = cat_corr_with_label(df,cat_features,label_feature)
    corr_all_label = pd.concat([corr_num_label,corr_cat_label],axis=1).T
    corr_all_label = corr_all_label.fillna(0)[required_features['ORIGINAL_LABEL']]
    corr_all_label = corr_all_label.sort_values(ascending=False)

    for c in corr_all_label.index:
        rec_corr['features'].append(c)
        rec_corr['data_label'].append(corr_all_label.loc[c])

    if config['FEAT_CORR']==True:
        rec_corr['feature_corr'] = 1
        # This is slow. By default it's disabled, but there's an option in CFN to enable it. 
        # Feature correlations
        cat_features = cat_features
        corr_num = num_corr(df[num_features])
        corr_num_cat, corr_cat_num = num_cat_corr(df[num_features],df[cat_features])
        corr_cat = cat_corr(df[cat_features])
        # Concat all results into a square symmetric matrix
        corr_all = pd.concat([pd.concat([corr_num,corr_cat_num],axis=1),
                    pd.concat([corr_cat,corr_num_cat],axis=1)],axis=0).round(2).abs()
        corr_all = corr_all.fillna(0)
        corr_all = corr_all.loc[corr_all_label.index]
        rec_corr['count'] = len(corr_all)
        rec_corr['data'] = []
        for c in corr_all.index:
            for i in corr_all.index:
                rec_corr['data'].append({'x':i,'y':c,'v':corr_all.loc[i,c]})
            
    return rec_corr
    

def profile_report(config):
    """ main function - generates the profile report of the CSV """
    # -- Jinja2 environment -- 
    env = Environment(autoescape=select_autoescape(['html', 'xml']), loader=FileSystemLoader("templates"))
    profile= env.get_template('profile.html')
    
    # -- all the checks -- 
    df = get_dataframe(config)
    logging.info('Generate overview.')
    df, overview_stats = get_overview(config, df)
    logging.info('Inference variable types.')
    df, df_stats, warnings = get_stats(config, df)
    logging.info('Generate label stats.')
    lbl_stats, lbl_warnings = get_label(config, df)
    logging.info('Generate label distribution.')
    p_stats, p_warnings = get_partition(config, df)
    logging.info('Profile categorical features.')
    cat_rec = get_categorical(config, df_stats, df)
    logging.info('Profile numerical features.')
    num_rec = get_numerics( config, df_stats, df)
    logging.info('Calculate correlation.')
    corr_rec = get_correlation( config, df_stats, df)
    
    colors,hover_colors,colors_original = config_html(config,df)

    logging.info('Generate report.')
    # -- render the report 
    profile_results = profile.render(file = config['file_name'], 
                                     overview = overview_stats,
                                     warnings = warnings,
                                     df_stats=df_stats.loc[df_stats['_feature'] != 'exclude'],
                                     label  = lbl_stats,
                                     label_msg = lbl_warnings,
                                     p_stats=p_stats,
                                     p_warnings = p_warnings,
                                     cat_rec=cat_rec,
                                     num_rec=num_rec,
                                     corr_rec = corr_rec,
                                     label_colors = colors,
                                    hover_colors = hover_colors,
                                    original_label_colors = colors_original) 
    return profile_results

def convert_labels(df,label_col,FraudLabels):
    # Map labels to FRAUD/NON-FRAUD based on CFN option
    df = df.copy()
    df['AFD_LABEL'] = df[label_col]
    fraud_labels = []
    label_summary = df[label_col].value_counts()
    label_values = label_summary.keys().tolist()
    for item in FraudLabels.split(','):
        item  = item.lstrip().rstrip().lower()
        if item in label_values:
            fraud_labels.append(item)
    if len(fraud_labels)>0:
        # Convert labels to binary
        df.loc[df[label_col].isin(fraud_labels),'AFD_LABEL'] = 'FRAUD'
        df.loc[(~df[label_col].isin(fraud_labels))&(~df[label_col].isna()),'AFD_LABEL'] = 'NON-FRAUD'
        return 'NON-FRAUD', ['NON-FRAUD','FRAUD'], df, True, label_summary.keys().tolist()
    else:
        # Use original labels
        return label_summary.idxmax(), label_summary.keys().tolist(), df, None, label_summary.keys().tolist()


def config_html(config,df):
    # HTML display configurations
    base_colors =  ['#36A2EB','#FF6384','#41d88c','#9966FF','#FF9F40','#8c564b','#e377c2','#7f7f7f','#FFCD56','#17becf']
    base_hover_colors = ['#F6FFFF' for i in range(len(base_colors))]
    colors = {}
    hover_colors = {}
    colors_original = {}
    count = 0
    for c in config['LABELS']:
        colors[c] = base_colors[count]
        hover_colors[c] = base_hover_colors[count]
        count = count + 1
        count = count%len(base_colors)
    colors['Missing Labels'] = base_colors[count]
    hover_colors['Missing Labels'] = base_hover_colors[count]
    count2 = 0
    for c in config['ORIGINAL_LABELS']:
        colors_original[c] = base_colors[count2]
        count2 = count2 + 1
        count2 = count2%len(base_colors)
    colors_original['Missing Labels'] = base_colors[count2]
    return colors, hover_colors, colors_original

def read_csv_from_s3(s3_path,datatype=object):
    dfs = wr.s3.read_csv(path=s3_path, dtype=datatype, sep=delimiter, chunksize=1000000)
    df_all = pd.concat([df for df in dfs])
    return df_all

# Read Glue job parameters
job_args = getResolvedOptions(sys.argv, ["CSVFilePath","FileDelimiter","EventTimestampColumn","LabelColumn","FormatCSV","ProfileCSV","DropLabelMissingRows","DropTimestampMissingRows","FraudLabels","FeatureCorr","ReportSuffix"])
file_path = job_args['CSVFilePath']
delimiter= job_args['FileDelimiter']
EventTimestampCol= job_args['EventTimestampColumn']
LabelCol= job_args['LabelColumn']
CleanCSV = (job_args['FormatCSV']=='Yes')
ProfileCSV = (job_args['ProfileCSV']=='Yes')
DropLabelMissingRows = (job_args['DropLabelMissingRows']=='Yes')
DropTimestampMissingRows = (job_args['DropTimestampMissingRows']=='Yes')
FraudLabels = job_args['FraudLabels']
FeatureCorr = (job_args['FeatureCorr']!='No')
ReportSuffix = job_args['ReportSuffix']
logging.info(job_args)


html_templates = ['https://raw.githubusercontent.com/haozhouamzn/aws-fraud-detector-samples/master/profiler/CloudFormationSolution/templates/profile.html',
'https://raw.githubusercontent.com/haozhouamzn/aws-fraud-detector-samples/master/profiler/CloudFormationSolution/templates/profile_categorical.html',
'https://raw.githubusercontent.com/haozhouamzn/aws-fraud-detector-samples/master/profiler/CloudFormationSolution/templates/profile_df.html',
'https://raw.githubusercontent.com/haozhouamzn/aws-fraud-detector-samples/master/profiler/CloudFormationSolution/templates/profile_label.html',
'https://raw.githubusercontent.com/haozhouamzn/aws-fraud-detector-samples/master/profiler/CloudFormationSolution/templates/profile_messages.html',
'https://raw.githubusercontent.com/haozhouamzn/aws-fraud-detector-samples/master/profiler/CloudFormationSolution/templates/profile_numeric.html',
'https://raw.githubusercontent.com/haozhouamzn/aws-fraud-detector-samples/master/profiler/CloudFormationSolution/templates/profile_overview.html',
'https://raw.githubusercontent.com/haozhouamzn/aws-fraud-detector-samples/master/profiler/CloudFormationSolution/templates/profile_partition.html',
'https://raw.githubusercontent.com/haozhouamzn/aws-fraud-detector-samples/master/profiler/CloudFormationSolution/templates/profile_correlation.html']

# Parse S3 path
path_parts=file_path.replace("s3://","").split("/")
bucket = path_parts.pop(0)
file_prefix = path_parts[:-1]
file_name = path_parts[-1]


# Load html templates
logging.info('Loading HTML templates.')
os.mkdir("templates")
for item in html_templates:
    _local_file = 'templates/'+item.split('/')[-1]
    logging.info(save_file_from_url(item,_local_file))
    

if delimiter=='':
    delimiter=','

if CleanCSV==True:
    logging.info('Formatting CSV.')
    # Read csv file
    logging.info('Reading CSV file.')
    df = read_csv_from_s3(file_path)  
    logging.info(f'Number of rows: {df.shape[0]}, Number of columns: {df.shape[1]}')

    # Convert timestamp to required format
    logging.info('Formatting datetime.')
    try:
        # Don't change if it's numeric
        df[EventTimestampCol].astype('int')
        logging.info('Datatime is integer, consider it as UNIX epoch.')
        df[EventTimestampCol] = df[EventTimestampCol].astype('int').astype("datetime64[s]")
    except:
        _tmp_timestamp = pd.to_datetime(df[EventTimestampCol],'coerce')
        _tmp_timestamp[~_tmp_timestamp.isna()] = _tmp_timestamp[~_tmp_timestamp.isna()].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        df[EventTimestampCol] = _tmp_timestamp
        _n_time = _tmp_timestamp.isna().sum()
        logging.info(f'Number of empty datetime is {_n_time}')

    # Convert label values to lower cases and remove spaces
    logging.info('Converting labels.')
    df.loc[~df[LabelCol].isna(),LabelCol] = df[~df[LabelCol].isna()][LabelCol].astype(str).str.lower().str.replace(r'[^a-z0-9]+', '_', regex=True)

    # Drop rows with missing labels or missing timestamps or bad timestamp formats
    if DropTimestampMissingRows:
        logging.info('Drop rows with missing timestamps or bad timestamp formats')
        df = df[~df[EventTimestampCol].isna()]
    if DropLabelMissingRows:
        logging.info('Drop rows with missing labels')
        df = df[~df[LabelCol].isna()]

    # Convert headers
    logging.info('Converting headers')
    dfc = {EventTimestampCol:'EVENT_TIMESTAMP',LabelCol:'EVENT_LABEL'}                      
    for c in df.columns:
        if c in ['LABEL_TIMESTAMP','ENTITY_ID','EVENT_ID','ENTITY_TYPE']:
            dfc[c] = c
        elif c not in dfc.keys():
            # Convert header to lower cases and remove spaces
            dfc[c] = re.sub(r'[^a-z0-9]+', '_', c.lower())
    df.rename(columns=dfc,inplace=True)
    cleaned_file = '/'.join(file_prefix+['afd_data_'+file_name.split('.')[0],'cleaned_'+file_name])
    cleaned_file = f's3://{bucket}/{cleaned_file}'
    logging.info(f'Saving cleaned file to: {cleaned_file}')
    logging.info(f'Number of rows: {df.shape[0]}, Number of columns: {df.shape[1]}')
    if df.shape[0]>0:
        wr.s3.to_csv(df=df, path=cleaned_file, index=False)
    else:
        wr.s3.to_csv(df=pd.Series(['Empty data set after formatting!']), path=cleaned_file, index=False)

if ProfileCSV==True:
    logging.info('Generating data profiler.')
    # Read csv file
    logging.info('Reading CSV file.')
    df = read_csv_from_s3(file_path,{LabelCol:'object'})  

    # Rename column to remove special characters
    dfc = {}                      
    for c in df.columns:
        # Convert header to lower cases and remove spaces
        dfc[c] = re.sub(r'[^a-zA-Z0-9]+', '_', c)
    df.rename(columns=dfc,inplace=True)
    EventTimestampCol = dfc[EventTimestampCol]
    LabelCol = dfc[LabelCol]
    logging.info(df.columns)
    

    # Get majority label class
    logging.info('Profiling labels.')
    majority_class, label_values, df, mapped_fraud, original_label_values = convert_labels(df,LabelCol,FraudLabels)

    # Update configuration
    config = {  
        "file_name": file_path,
        "input_file": df,
        "required_features" : {
            "EVENT_TIMESTAMP": EventTimestampCol,
            "EVENT_LABEL": 'AFD_LABEL',
            "ORIGINAL_LABEL": LabelCol,
        },
        "FEAT_CORR": FeatureCorr,     # Boolean, whether to calculate correlation for pair-wise features
        "MAPPED_FRAUD": mapped_fraud,   # Boolean, whether customer mapped labels to fraud
        "LABELS" : label_values,        # Mapped label values, if not mapped, same as ORIGINAL_LABELS
        "ORIGINAL_LABELS": original_label_values,   # Orignal label values
        "MAJORITY_CLASS": majority_class,    # Majority label class value
        "MinClassCount": 0,     # Do not show categories with fewer records in report plots
        "TopN":500              # Maximum number of categories to show in plots. 
    }

    # Generate report
    report = profile_report(config)
    # Save report to S3 bucket
    with open("report.html", "w") as file:
        file.write(report)
    s3_client = boto3.client('s3')
    ReportSuffix = ReportSuffix.lstrip().rstrip()
    profiler_path = '/'.join(file_prefix+['afd_data_'+file_name.split('.')[0],'report_'+ReportSuffix+'.html'])
    logging.info(f'Saving data profiler to: s3://{bucket}/{profiler_path}')
    response = s3_client.upload_file("report.html", bucket, profiler_path)

logging.info('Done.')

