RECIPE = \
    {
        "Registration_FakeAccountCreationByBots": 
            {
                "data_path": "data/Registration_FakeAccountCreationByBots_100k.csv",
                
                "variable_mappings": [
                    {
                        "variable_name": "first_name",
                        "variable_type": "SHIPPING_NAME",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "last_name",
                        "variable_type": "BILLING_NAME",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "ip_address",
                        "variable_type": "IP_ADDRESS",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "honeypot_hits_with_given_user_agent_last_hour",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "email_address",
                        "variable_type": "EMAIL_ADDRESS",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "user_agent",
                        "variable_type": "USERAGENT",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "honeypot_hits_with_given_ip_address_last_hour",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    }
                    ],
                
                "label_mappings": {
                    "FRAUD": ["fraud"],
                    "LEGIT": ["legit"]
                }        
            },
        "Abuse_FreeTrialReferralAbuse": 
            {
                "data_path": "data/Abuse_FreeTrialReferralAbuse_100k.csv",
                
                "variable_mappings": [
                    {
                        "variable_name": "referral_code",
                        "variable_type": "FREE_FORM_TEXT",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "first_name",
                        "variable_type": "SHIPPING_NAME",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "card_bin",
                        "variable_type": "CARD_BIN",
                        "data_type": "INTEGER"
                    },
                    {
                        "variable_name": "last_name",
                        "variable_type": "BILLING_NAME",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "email_address",
                        "variable_type": "EMAIL_ADDRESS",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "ip_address",
                        "variable_type": "IP_ADDRESS",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "phone_number",
                        "variable_type": "PHONE_NUMBER",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "postal_code",
                        "variable_type": "BILLING_ZIP",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "referral_medium",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    }
                    ],
                
                "label_mappings": {
                    "FRAUD": ["fraud"],
                    "LEGIT": ["legit"]
                }        
            },
        "ContentModeration_FakeReviews": 
            {
                "data_path": "data/ContentModeration_FakeReviews_100k.csv",
                
                "variable_mappings": [
                    {
                        "variable_name": "hour_of_review",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "asin",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "review_text",
                        "variable_type": "FREE_FORM_TEXT",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "rating",
                        "variable_type": "NUMERIC",
                        "data_type": "INTEGER"
                    }
                    ],
                
                "label_mappings": {
                    "FRAUD": ["fraud"],
                    "LEGIT": ["legit"]
                }        
            },
        "Insurance_FraudulentAutoInsuranceClaims": 
            {
                "data_path": "data/Insurance_FraudulentAutoInsuranceClaims_100k.csv",
                
                "variable_mappings": [
                    {
                        "variable_name": "first_name",
                        "variable_type": "SHIPPING_NAME",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "last_name",
                        "variable_type": "BILLING_NAME",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "policy_id",
                        "variable_type": "ORDER_ID",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "policy_deductable",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "customer_age",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "policy_annual_premium",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "incident_severity",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "vehicle_claim",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "incident_hour",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "num_injuries",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "num_claims_past_year",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "injury_claim",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "num_vehicles_involved",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "num_witnesses",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "incident_type",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "incident_type",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    ],
                
                "label_mappings": {
                    "FRAUD": ["fraud"],
                    "LEGIT": ["legit"]
                }        
            },

}