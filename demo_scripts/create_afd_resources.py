import os
import json
import boto3
import click
import string
import random
import logging
import pandas as pd
from variable_type_config import RECIPE

random_str = ''.join(random.choices(string.ascii_lowercase, k=6))

## Fixed variables. No need to change them

# MODEL_TYPE fixed as the code is only written for external events so-far
# TO DO : Add ingested event and TFI support
MODEL_TYPE = "ONLINE_FRAUD_INSIGHTS"
MODEL_DESC     = "Demo model"
EVENT_DESC     = "Demo event"
ENTITY_TYPE    = "customer"  # this is provided in the dummy data. Will need to change if using different data
ENTITY_DESC    = "Demo entity"

# boto3 connections
client = boto3.client('frauddetector') 
s3 = boto3.client('s3')

@click.group()
def cli():
    'A script to create AFD model resources for demo purposes, depending on the fraud use-case of interest'
    pass

@cli.command()
@click.option("--s3bucket", 
              "-s",
              type=str,
              required=True,
              help="Provide S3 bucket where demo data needs to be copied."
             )
@click.option("--s3suffix", 
              "-x",
              type=str,
              default="afd-demo",
              help="Provide folder inside your S3 bucket where demo data needs to be copied. If not provided, it will save in afd-demo"
             )
@click.option("--eventtype", 
              "-e", 
              type=str, 
              default="api_call_event_{}".format(random_str), 
              help="What do you want to name your Event Type. e.g. My first event"
             ) 
@click.option("--modelname",
              "-m", 
              type=str, 
              default="api_call_model_{}".format(random_str),
              help="What do you want to name your Model. e.g. My fraud detection model"
             ) 
@click.option("--iamrole",
              "-r",
              type=str,
              required=True, 
              help="Provide IAM role ARN. Must have AmazonFraudDetectorFullAccessPolicy and AmazonS3FullAccess policies attached"
             )
@click.option("--fraudcategory", 
             "-f",
             type=click.Choice([
                 'Abuse_FreeTrialReferralAbuse', 
                 'ContentModeration_FakeReviews',
                 'Insurance_FraudulentAutoInsuranceClaims',
                 'Registration_FakeAccountCreationByBots',
                 'Registration_FakeAccountCreationByHumans',
                 'Transactions_CardNotPresentOnlineTransactions',
                 'Transactions_LoyaltyPayments'
                 ], 
             case_sensitive=True),
             help="Provide fraud category from the given list. e.g. Abuse_FreeTrialReferralAbuse"
             )
def afd_train_model_demo(s3bucket, s3suffix, eventtype, modelname, iamrole, fraudcategory):
    
    #############################################
    #####               Setup               #####
    config_file = RECIPE[fraudcategory]
                
    MODEL_NAME = modelname
    EVENT_TYPE = eventtype
    IAM_ROLE = iamrole
    
    EVENT_VARIABLES = [variable["variable_name"] for variable in config_file["variable_mappings"]]
    EVENT_LABELS = ["fraud", "legit"]

    # Variable mappings of demo data in this use case.  Important to teach this to customer
    click.echo(f'{pd.DataFrame(config_file["variable_mappings"])}')
    
    # Copy file from 
    data_path = config_file["data_path"]
    response = s3.list_objects_v2(Bucket=s3bucket, Prefix=os.path.join(s3suffix, data_path))
    if response['KeyCount'] == 0:
        s3.put_object(
            Bucket=s3bucket, 
            Key=os.path.join(s3suffix, data_path),
            Body=open(data_path, 'rb')
        )
    S3_DATA_PATH = "s3://" + os.path.join(s3bucket, s3suffix, data_path)
       
    #############################################
    ##### Create event variables and labels #####
    
    # -- create variable  --
    for variable in config_file["variable_mappings"]:
        
        DEFAULT_VALUE = '0.0' if variable["data_type"] == "FLOAT" else '<null>'
        
        try:
            resp = client.get_variables(name = variable["variable_name"])
            click.echo("{0} exists, data type: {1}".format(variable["variable_name"], resp['variables'][0]['dataType']))
        except:
            click.echo("Creating variable: {0}".format(variable["variable_name"]))
            resp = client.create_variable(
                    name         = variable["variable_name"],
                    dataType     = variable["data_type"],
                    dataSource   ='EVENT',
                    defaultValue = DEFAULT_VALUE, 
                    description  = variable["variable_name"],
                    variableType = variable["variable_type"])
            
    response = client.put_label(
        name = "fraud",
        description = "FRAUD")
    
    response = client.put_label(
        name = "legit",
        description = "LEGIT")
        

    #############################################
    #####   Define Entity and Event Types   #####
    
    # -- create entity type --
    try:
        response = client.get_entity_types(name = ENTITY_TYPE)
        click.echo("-- entity type exists --")
        click.echo(response)
    except:
        response = client.put_entity_type(
            name        = ENTITY_TYPE,
            description = ENTITY_DESC
        )
        click.echo("-- create entity type --")
        click.echo(response)


    # -- create event type --
    try:
        response = client.get_event_types(name = EVENT_TYPE)
        click.echo("\n-- event type exists --")
        click.echo(response)
    except:
        response = client.put_event_type (
            name           = EVENT_TYPE,
            eventVariables = EVENT_VARIABLES,
            labels         = EVENT_LABELS,
            entityTypes    = [ENTITY_TYPE])
        click.echo("\n-- create event type --")
        click.echo(response)


    #############################################
    #####   Create and train your model     #####
    try:
        response = client.create_model(
           description   = MODEL_DESC,
           eventTypeName = EVENT_TYPE,
           modelId       = MODEL_NAME,
           modelType     = MODEL_TYPE)
        click.echo("-- initalize model --")
        click.echo(response)
    except Exception:
        pass
    
    # -- initalized the model, it's now ready to train --
    
    # -- first define training_data_schema for model to use --
    training_data_schema = {
        'modelVariables' : EVENT_VARIABLES,
        'labelSchema'    : {
            'labelMapper' : {
                'FRAUD' : ["fraud"],
                'LEGIT' : ["legit"]
            }
        }
    }
    
    response = client.create_model_version(
        modelId             = MODEL_NAME,
        modelType           = MODEL_TYPE,
        trainingDataSource  = 'EXTERNAL_EVENTS',
        trainingDataSchema  = training_data_schema,
        externalEventsDetail = {
            'dataLocation'     : S3_DATA_PATH,
            'dataAccessRoleArn': IAM_ROLE
        }
    )
    model_version = response['modelVersionNumber']
    click.echo("-- model training --")
    click.echo(response)
    
    
if __name__=="__main__":
    cli()