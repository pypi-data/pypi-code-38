DEFAULTCODES = {
    "setuint16_t": "uint16_t temp;memcpy(&temp,data,2);{NAME}=temp;write_data({NAME},{BYTEID});",
    "setuint32_t": "uint32_t temp;memcpy(&temp,data,4);{NAME}=temp;write_data({NAME},{BYTEID});",
    "setuint32_t_silent": "uint32_t temp;memcpy(&temp,data,4);{NAME}=temp;",
    "setpin_output": "if(data[0]>0){{NAME}=data[0];}write_data({NAME},{BYTEID});pinMode({NAME}, OUTPUT);",
    "setpin_input": "if(data[0]>0){{NAME}=data[0];}write_data({NAME},{BYTEID});pinMode({NAME}, INPUT);",
    "setbool": "{NAME}=(bool)data[0];write_data({NAME},{BYTEID});",
}
