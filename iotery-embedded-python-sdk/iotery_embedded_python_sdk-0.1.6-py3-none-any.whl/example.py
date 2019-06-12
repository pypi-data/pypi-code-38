from Iotery import Iotery

TEAM_ID = "165fcb74-8879-11e9-8452-d283610663ec"
iotery = Iotery()

d = iotery.getDeviceTokenBasic(data={"key": "thermal_sensor_001",
                                     "serial": "THERMAL_SENSOR_001", "secret": "thermal_sensor_001_secret", "teamUuid": TEAM_ID})
iotery.set_token(d["token"])
me = iotery.getMe()

print(me["name"])
