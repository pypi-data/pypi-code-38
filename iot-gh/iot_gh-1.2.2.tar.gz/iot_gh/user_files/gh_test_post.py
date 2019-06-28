from iot_gh.IoTGreenhouse import IoTGreenhouse
from iot_gh.IoTGreenhouseService import IoTGreenhouseService

def test_post():
   
    print("*** GH testing ***")   
    ghs = IoTGreenhouseService()
    gh = ghs.greenhouse
    ghs.web_service.post_greenhouse()
    print(ghs.web_service.post_data.status_code)
    print(ghs.web_service.post_data.last_update)
    print(ghs.web_service.post_data.exception)
    print("GH post test completed.")   

if __name__ == "__main__":
    test_post()



