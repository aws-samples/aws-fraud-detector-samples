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
        "Registration_FakeAccountCreationByHumans": 
            {
                "data_path": "data/Registration_FakeAccountCreationByHumans_100k.csv",
                
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
                        "variable_name": "user_agent",
                        "variable_type": "USERAGENT",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "email_address",
                        "variable_type": "EMAIL_ADDRESS",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "date_of_birth",
                        "variable_type": "FREE_FORM_TEXT",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "email_domain",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    }
                    ],
                
                "label_mappings": {
                    "FRAUD": ["fraud"],
                    "LEGIT": ["legit"]
                }        
            },
        "Transactions_CardNotPresentOnlineTransactions": 
            {
                "data_path": "data/Transactions_CardNotPresentOnlineTransactions_100k.csv",
                
                "variable_mappings": [
                    {
                        "variable_name": "ip_address",
                        "variable_type": "IP_ADDRESS",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "user_agent",
                        "variable_type": "USERAGENT",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "email_address",
                        "variable_type": "EMAIL_ADDRESS",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "fingerprint",
                        "variable_type": "FINGERPRINT",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "phone_number",
                        "variable_type": "PHONE_NUMBER",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "billing_address",
                        "variable_type": "BILLING_ADDRESS_L1",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "billing_city",
                        "variable_type": "BILLING_CITY",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "billing_postal",
                        "variable_type": "BILLING_ZIP",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "billing_state",
                        "variable_type": "BILLING_STATE",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "billing_country",
                        "variable_type": "BILLING_COUNTRY",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "merchant_id",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "card_bin",
                        "variable_type": "CARD_BIN",
                        "data_type": "INTEGER"
                    },
                    {
                        "variable_name": "product_id",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "product_category",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "transaction_amount",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "shipping_address",
                        "variable_type": "SHIPPING_ADDRESS_L1",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "shipping_city",
                        "variable_type": "SHIPPING_CITY",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "shipping_postal",
                        "variable_type": "SHIPPING_ZIP",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "shipping_state",
                        "variable_type": "SHIPPING_STATE",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "shipping_country",
                        "variable_type": "SHIPPING_COUNTRY",
                        "data_type": "STRING"
                    }
                    ],
                
                "label_mappings": {
                    "FRAUD": ["fraud"],
                    "LEGIT": ["legit"]
                }        
            },
        "Transactions_LoyaltyPayments": 
            {
                "data_path": "data/Transactions_LoyaltyPayments_100k.csv",
                
                "variable_mappings": [
                    {
                        "variable_name": "ip_address",
                        "variable_type": "IP_ADDRESS",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "user_agent",
                        "variable_type": "USERAGENT",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "email_address",
                        "variable_type": "EMAIL_ADDRESS",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "is_code_transferred",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "is_postal_in_txn_same_as_postal_in_acnt",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "shipping_city",
                        "variable_type": "SHIPPING_CITY",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "shipping_postal",
                        "variable_type": "SHIPPING_ZIP",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "shipping_state",
                        "variable_type": "SHIPPING_STATE",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "shipping_country",
                        "variable_type": "SHIPPING_COUNTRY",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "loyalty_card_type",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "transaction_amount",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "count_previous_redemptions_device",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "count_previous_redemptions_ip",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "count_of_txns_loyalty_card_last_day",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "amount_of_txns_loyalty_card_last_day",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "total_reward_points",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "coupon_code",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "device_id",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
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
                        "variable_type": "CATEGORICAL",
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
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
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
                        "data_type": "FLOAT"
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
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "vehicle_claim",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "incident_hour",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
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
                        "variable_name": "police_report_available",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    }
                    ],
                
                "label_mappings": {
                    "FRAUD": ["fraud"],
                    "LEGIT": ["legit"]
                }        
            },
        "Advertisement_AdClickFraud": 
            {
                "data_path": "data/Advertisement_AdClickFraud_20k.csv",
                
                "variable_mappings": [
                    {
                        "variable_name": "ip_address",
                        "variable_type": "IP_ADDRESS",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "user_agent",
                        "variable_type": "USERAGENT",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "campaign_id",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "publisher_id",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "time_between_clicks_minutes",
                        "variable_type": "NUMERIC",
                        "data_type": "FLOAT"
                    },
                    {
                        "variable_name": "click_id",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    },
                    {
                        "variable_name": "app_category_id",
                        "variable_type": "CATEGORICAL",
                        "data_type": "STRING"
                    }
                    ],
                
                "label_mappings": {
                    "FRAUD": ["fraud"],
                    "LEGIT": ["legit"]
                }        
            }
}