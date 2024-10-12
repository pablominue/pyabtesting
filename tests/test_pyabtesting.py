import pandas as pd
from abtestools.audiences import Audience

data = pd.read_csv('tests/data.csv')

def test_users():
    audience = Audience(users=data['USER_ID'].to_list()).assign_groups()
    print(len(audience))

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
    print(audience.users[:10])