import pandas as pd
from abtestools.audiences import Audience
from abtestools.test import Metric
from abtestools.campaign import Campaign

import datetime

data = pd.read_csv('tests/data.csv')

def test_users():
    audience = Audience(users=data['USER_ID'].to_list()).assign_groups()
    assert len(audience) == len(data)

def test_mapping():
    audience = Audience(
        users=data['USER_ID'].astype(str).to_list(), 
        group_mapping=dict(
            zip(
                data['USER_ID'].astype(str), 
                list(
                    map(
                        lambda x: x.replace('variant', 'test'), 
                        data['VARIANT_NAME'].to_list()
                        )
                    )
                )
            )
        )
    assert True

def test_campaigns():
    def extract_data(date):
        print(date)
        return dict(zip(data['USER_ID'], data['REVENUE']))
    audience = Audience(
        users=data['USER_ID'].astype(str).to_list(), 
        group_mapping=dict(
            zip(
                data['USER_ID'].astype(str), 
                list(
                    map(
                        lambda x: x.replace('variant', 'test'), 
                        data['VARIANT_NAME'].to_list()
                        )
                    )
                )
            )
        )
    revenue = Metric(name='revenue', type='continuous')
    campaign = Campaign(audience=audience, metrics=[revenue], date_range=[datetime.datetime.today() - datetime.timedelta(days=i) for i in range(5)])
    print(list(campaign.backfill(metric=revenue, extract_data=extract_data)))