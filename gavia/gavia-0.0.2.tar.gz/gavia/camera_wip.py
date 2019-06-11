# import sys

def footprint(imheight,imwidth,alt,roll=0,pitch=0,yaw=0,focal=8,sensorh=10.2, sensorv=8.3,inwater=True,refract=1.339):
    '''
        Calculates the footprint of an image given the camera specs and 
        AUV positioning data.

        This function assumes that the camera is facing directly down, 90 degrees from the AUV
        trajectory angle (as is the case on the Gavia AUV).

        Defaults:
            - assumes AUV is perpendicular to the ground plane, else input roll/pitch/yaw angles
            - focal length taken as 8mm
            - sensor size taken as 10.2mm x 8.3mm
            - refraction index in air taken as 1.0 
            - refraction index in water taken as 1.339 

        Parameters
        ----------
        imheight : int
            image height in pixels 
        imwidth : int
            image width in pixels
        alt : float 
            altitude of AUV
        sensorh : float 
            size of sensor in mm in the horizontal plane
        sensorv : float 
            size of sensor in mm in the vertical plane
    '''
    # convert to radians
    yaw     = (yaw/180.0)*np.pi
    pitch   = (pitch/180.0)*np.pi
    roll    = (roll/180.0)*np.pi

    # Angle of View in horizontal (air)
    aovh         = 2.0*np.arctan(sensorh / (2.0*focal))
    # Angle of View in vetical (air)
    aovv         = 2.0*np.arctan(sensorv / (2.0*focal))

    if inwater:
        # Angle of View in horizontal (water)
        aovh         = 2.0*np.arcsin(np.sin(aovh/2.0)/refract)
        # Angle of View in vetical (water)
        aovv         = 2.0*np.arcsin(np.sin(aovv/2.0)/refract)

    ## Treat the camera as the rotation point ##
    # Distance from centre -  top right 
    dx1         = alt*np.tan((aovh/2.0)+roll)
    dy1         = alt*np.tan((aovv/2.0)+pitch)
    # Distance from centre -  top left 
    dx2         = alt*np.tan((-aovh/2.0)+roll)
    dy2         = alt*np.tan((aovv/2.0)+pitch)
    # Distance from centre -  bottom right 
    dx3         = alt*np.tan((aovh/2.0)+roll)
    dy3         = alt*np.tan((-aovv/2.0)+pitch)
    # Distance from centre -  bottom left 
    dx4         = alt*np.tan((-aovh/2.0)+roll)
    dy4         = alt*np.tan((-aovv/2.0)+pitch)

    # Target size in horizontal plane given in meters - assuming no roll
    fovh        = 2.0*alt*np.tan(aovh/2.0)
    # Target size in vertical plane given in meters - assuming no pitch 
    fovv        = 2.0*alt*np.tan(aovv/2.0)

    ## Treat the centre of the image as the rotation point ##
    # offsets due to yaw - top right
    dx_offset1  = (dx1 * np.cos(yaw)) - (dy1 * np.sin(yaw))
    dy_offset1  = (dx1 * np.sin(yaw)) + (dy1 * np.cos(yaw))
    # offsets due to yaw - top left
    dx_offset2  = (dx2 * np.cos(yaw)) - (dy2 * np.sin(yaw))
    dy_offset2  = (dx2 * np.sin(yaw)) + (dy2 * np.cos(yaw))
    # offsets due to yaw - bottom right
    dx_offset3  = (dx3 * np.cos(yaw)) - (dy3 * np.sin(yaw))
    dy_offset3  = (dx3 * np.sin(yaw)) + (dy3 * np.cos(yaw))
    # offsets due to yaw - bottom left
    dx_offset4  = (dx4 * np.cos(yaw)) - (dy4 * np.sin(yaw))
    dy_offset4  = (dx4 * np.sin(yaw)) + (dy4 * np.cos(yaw))

    print('Horizontal AOV: ', aovh)
    print('Vertical AOV: ', aovv)
    print('Horizontal area: ', fovh)
    print('Vertical area: ', fovv)

    print('dx1: ', dx1)
    print('dy1: ', dy1)

    print('dx2: ', dx2)
    print('dy2: ', dy2)

    print('dx3: ', dx3)
    print('dy3: ', dy3)

    print('dx4: ', dx4)
    print('dy4: ', dy4)

    print('dx offset1: ', dx_offset1)
    print('dy_offset1: ', dy_offset1)

    print('dx offset2: ', dx_offset2)
    print('dy_offset2: ', dy_offset2)

    print('dx offset3: ', dx_offset3)
    print('dy_offset3: ', dy_offset3)

    print('dx offset4: ', dx_offset4)
    print('dy_offset4: ', dy_offset4)

    print('Top Right - Top Left:',  np.sqrt(((dx_offset3 - dx_offset4)**2) + ((dy_offset3 - dy_offset4)**2))  )
    print('Top Right - Bottom Right:',  np.sqrt(((dx_offset1 - dx_offset3)**2) + ((dy_offset1 - dy_offset3)**2))  )
    print('Bottom Right - Bottom Left:',  np.sqrt(((dx_offset1 - dx_offset2)**2) + ((dy_offset1 - dy_offset2)**2))  )
    print('Bottom Left - Top Left:',  np.sqrt(((dx_offset4 - dx_offset2)**2) + ((dy_offset4 - dy_offset2)**2))  )


    return [dx_offset1,dy_offset1], [dx_offset2,dy_offset2],[dx_offset3,dy_offset3],[dx_offset4,dy_offset4]


def rotate(vector, yaw, pitch, roll):
    Rotz = np.array([
        [np.cos(yaw), np.sin(yaw),  0], 
        [-np.sin(yaw), np.cos(yaw), 0],
        [0, 0 ,1]
    ])
    Rotx = np.array([
         [1, 0, 0], 
         [0, np.cos(pitch), np.sin(pitch)], 
        [0, -np.sin(pitch), np.cos(pitch)]
    ])
    Roty = np.array([
        [np.cos(roll), 0, -np.sin(roll)], 
        [0, 1, 0], 
        [np.sin(roll), 0, np.cos(roll)]
    ])
    rotation_matrix = np.dot(Rotz, np.dot(Roty, Rotx))
    return np.dot(rotation_matrix, vector)

def footprint2(imheight,imwidth,alt,roll=0,pitch=0,yaw=0,focal=8,sensorh=10.2, sensorv=8.3,inwater=True,refract=1.339):
    '''
        Calculates the footprint of an image given the camera specs and 
        AUV positioning data.

        This function assumes that the camera is facing directly down, 90 degrees from the AUV
        trajectory angle (as is the case on the Gavia AUV).

        Defaults:
            - assumes AUV is perpendicular to the ground plane, else input roll/pitch/yaw angles
            - focal length taken as 8mm
            - sensor size taken as 10.2mm x 8.3mm
            - refraction index in air taken as 1.0 
            - refraction index in water taken as 1.339 

        Parameters
        ----------
        imheight : int
            image height in pixels 
        imwidth : int
            image width in pixels
        alt : float 
            altitude of AUV
        sensorh : float 
            size of sensor in mm in the horizontal plane
        sensorv : float 
            size of sensor in mm in the vertical plane
    '''
    # convert to radians
    yaw     = (yaw/180.0)*np.pi
    pitch   = (pitch/180.0)*np.pi
    roll    = (roll/180.0)*np.pi

    # Angle of View in horizontal (air)
    aovh         = 2.0*np.arctan(sensorh / (2.0*focal))
    # Angle of View in vetical (air)
    aovv         = 2.0*np.arctan(sensorv / (2.0*focal))

    if inwater:
        # Angle of View in horizontal (water)
        aovh         = 2.0*np.arcsin(np.sin(aovh/2.0)/refract)
        # Angle of View in vetical (water)
        aovv         = 2.0*np.arcsin(np.sin(aovv/2.0)/refract)

    ## Treat the camera as the rotation point ##
    # Distance from centre -  top right 
    # dx1         = alt*np.tan((aovh/2.0)+roll) 
    # dy1         = ( alt*np.tan((aovv/2.0)+pitch) ) / np.cos((aovh/2.0)+roll)
    # # Distance from centre -  top left 
    # dx2         = -alt*np.tan((aovh/2.0)-roll) 
    # dy2         = ( alt*np.tan((aovv/2.0)+pitch) ) / np.cos((aovh/2.0)-roll)
    # # Distance from centre -  bottom right 
    # dx3         = alt*np.tan((aovh/2.0)+roll)  
    # dy3         = - ( alt*np.tan((aovv/2.0)-pitch) ) / np.cos((aovh/2.0)+roll)
    # # Distance from centre -  bottom left 
    # dx4         = - alt*np.tan((aovh/2.0)-roll) 
    # dy4         = - ( alt*np.tan((aovv/2.0)-pitch) ) / np.cos((aovh/2.0)-roll)

    dx1         = alt*np.tan((aovh/2.0)+roll) 
    dy1         = alt*np.tan((aovv/2.0)+pitch)
    # Distance from centre -  top left 
    dx2         = -alt*np.tan((aovh/2.0)-roll)
    dy2         = alt*np.tan((aovv/2.0)+pitch)
    # Distance from centre -  bottom right 
    dx3         = alt*np.tan((aovh/2.0)+roll) 
    dy3         = - alt*np.tan((aovv/2.0)-pitch)
    # Distance from centre -  bottom left 
    dx4         = - alt*np.tan((aovh/2.0)-roll) 
    dy4         =  - alt*np.tan((aovv/2.0)-pitch)

    # Width with no roll 
    w1          = (alt* ( np.tan((aovh/2.0)+roll) + np.tan((aovh/2.0)-roll)  ) ) / np.sin((np.pi/2.0) - pitch - (aovv/2.0))
    w2          = (alt* ( np.tan((aovh/2.0)+roll) + np.tan((aovh/2.0)-roll)  ) ) / np.sin((np.pi/2.0) - pitch + (aovv/2.0))


    # Target size in horizontal plane given in meters - assuming no roll
    fovh        = 2.0*alt*np.tan(aovh/2.0)
    # Target size in vertical plane given in meters - assuming no pitch 
    fovv        = 2.0*alt*np.tan(aovv/2.0)

    ## Treat the centre of the image as the rotation point ##
    # offsets due to yaw - top right
    dx_offset1  = (dx1 * np.cos(yaw)) - (dy1 * np.sin(yaw))
    dy_offset1  = (dx1 * np.sin(yaw)) + (dy1 * np.cos(yaw))
    # offsets due to yaw - top left
    dx_offset2  = (dx2 * np.cos(yaw)) - (dy2 * np.sin(yaw))
    dy_offset2  = (dx2 * np.sin(yaw)) + (dy2 * np.cos(yaw))
    # offsets due to yaw - bottom right
    dx_offset3  = (dx3 * np.cos(yaw)) - (dy3 * np.sin(yaw))
    dy_offset3  = (dx3 * np.sin(yaw)) + (dy3 * np.cos(yaw))
    # offsets due to yaw - bottom left
    dx_offset4  = (dx4 * np.cos(yaw)) - (dy4 * np.sin(yaw))
    dy_offset4  = (dx4 * np.sin(yaw)) + (dy4 * np.cos(yaw))

    print('Horizontal AOV: ', aovh)
    print('Vertical AOV: ', aovv)
    print('Horizontal area: ', fovh)
    print('Vertical area: ', fovv)

    print('dx1: ', dx1)
    print('dy1: ', dy1)

    print('dx2: ', dx2)
    print('dy2: ', dy2)

    print('dx3: ', dx3)
    print('dy3: ', dy3)

    print('dx4: ', dx4)
    print('dy4: ', dy4)

    print('dx offset1: ', dx_offset1)
    print('dy_offset1: ', dy_offset1)

    print('dx offset2: ', dx_offset2)
    print('dy_offset2: ', dy_offset2)

    print('dx offset3: ', dx_offset3)
    print('dy_offset3: ', dy_offset3)

    print('dx offset4: ', dx_offset4)
    print('dy_offset4: ', dy_offset4)

    print('Top Right - Top Left:',  np.sqrt(((dx_offset3 - dx_offset4)**2) + ((dy_offset3 - dy_offset4)**2))  )
    print('Top Right - Bottom Right:',  np.sqrt(((dx_offset1 - dx_offset3)**2) + ((dy_offset1 - dy_offset3)**2))  )
    print('Bottom Right - Bottom Left:',  np.sqrt(((dx_offset1 - dx_offset2)**2) + ((dy_offset1 - dy_offset2)**2))  )
    print('Bottom Left - Top Left:',  np.sqrt(((dx_offset4 - dx_offset2)**2) + ((dy_offset4 - dy_offset2)**2))  )


    return [dx_offset1,dy_offset1], [dx_offset2,dy_offset2],[dx_offset3,dy_offset3],[dx_offset4,dy_offset4],fovh,fovv, w1,w2
