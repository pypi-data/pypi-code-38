class IoTGreenhouse(object):
    """IoT Greenhouse data object"""
    #house IDs
    name = None
    house_id = None
    group_id = None
    house_number = "00"
    version = None

    #house state
    led_red_state = None
    led_red_status = None
    led_white_state = None
    led_white_status = None
    led_dual_state = None
    led_dual_status = None
    switch_pb_state = None
    switch_pb_status = None
    switch_toggle_state = None
    switch_toggle_status = None
    fan_state = None
    fan_status = None
    servo_position = None
    servo_status = None
    heater_state = None
    heater_status = None
    buzzer_state = None
    buzzer_status = None
    ain_pot_raw = None
    ain_light_raw = None
    ain_aux_raw = None
    temp_inside_C = None
    temp_inside_F = None
    temp_outside_C = None
    temp_outside_F = None
    last_update = None
    
    message = None

    def __init__(self): 
        #use factory method in IoTGreenhouse Service
        pass

    
