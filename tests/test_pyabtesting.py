import pandas as pd
from pyabtesting.audiences import Audience

def test_users():
    data = pd.read_csv('tests/data.csv')
    audience = Audience(users=data['USER_ID'].to_list()).assign_groups()
    print(len(audience))

    sample_data = pd.DataFrame({
        'user_id': ['a-123', 'a-234', 'b-123', 'b-234', 'c-000', 'd-aaa', 'f-fds', 'x-xxx', 'a-000', 'b-999'],
        'conversion': [1, 1, 0, 0, 1, 1, 1, 0, 0, 1]
    }
    )
    assert True

