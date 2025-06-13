import time
import urequests

HA_AUTH='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZTNiYjQxZGViYzY0ZjgzYTk5NWE4NTBjOTE5MzgyMSIsImlhdCI6MTc0ODg1MjM3MywiZXhwIjoyMDY0MjEyMzczfQ.GjVoM4ogDhv8uYEozObWh-70Nu1u5crsX0WGP1s3RJs'
HOME_ASSISTANT_URL = f"http://192.168.86.52:8123/api"
def toggle_entity(domain='light',entity='light.tv_light',action='toggle',timeout:float=2.0):
    url=f"{HOME_ASSISTANT_URL}/services/{domain}/{action}"
    headers = {
        "Authorization": f"{HA_AUTH}",
        "Content-Type": "application/json",
    }

    payload = {"entity_id": entity}
    
    try:
        response = urequests.post(url, json=payload, headers=headers)
    except:
        print('Connection error!')
        response.close()
        return

    if response.status_code == 200:
        print(f"{entity} did {action.replace('_', ' ')} successfully!")
        response.close()
    else:
        print(f"Error: {response.text}")


def update_state_entity(entity:str,update_data:dict,timeout: float = 2.0):
    """
    Example:
       update_data:
    {
    "state": "below_horizon",
    "attributes": {
        "next_rising":"2016-05-31T03:39:14+00:00",
        "next_setting":"2016-05-31T19:16:42+00:00"
        }
    }
    """
    url = f"{HOME_ASSISTANT_URL}/states/{entity}"

    headers = {
        "Authorization": f"{HA_AUTH}",
        "Content-Type": "application/json",
    }
    
    if not isinstance(update_data,dict):
        print("Update data should be in dictionary format!")
        return
    payload = update_data
    
    try:
       response = urequests.post(url, json=payload, headers=headers)
    except Exception as e:
        print('Connection error:',e)
        response.close()
        return

    if response.status_code == 200:
        print(f"{entity} did update successfully!")
        response.close()
    else:
        print(f"Error: {response.text}")
