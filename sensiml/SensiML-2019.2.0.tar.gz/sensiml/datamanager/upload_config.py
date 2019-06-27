##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017  SensiML Corporation.                                      #
#                                                                                #
#  The source code contained or  described  herein and all documents related     #
#  to the  source  code ("Material")  are  owned by SensiML Corporation or its   #
#  suppliers or licensors. Title to the Material remains with SensiML Corpora-   #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade      #
#  secrets and proprietary and confidential information of SensiML Corporation   #
#  and its suppliers and licensors, and is protected by worldwide copyright      #
#  and trade secret laws and treaty provisions. No part of the Material may      #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,     #
#  transmitted, distributed,  or disclosed in any way without SensiML's prior    #
#  express written permission.                                                   #
#                                                                                #
#  No license under any patent, copyright,trade secret or other intellectual     #
#  property  right  is  granted  to  or  conferred upon you by disclosure or     #
#  delivery of the Materials, either expressly, by implication,  inducement,     #
#  estoppel or otherwise.Any license under such intellectual property rights     #
#  must be express and approved by SensiML in writing.                           #
#                                                                                #
#  Unless otherwise agreed by SensiML in writing, you may not remove or alter    #
#  this notice or any other notice embedded in Materials by SensiML or SensiML's #
#  suppliers or licensors in any way.                                            #
#                                                                                #
##################################################################################


from glob import glob
try:
    import configparser as ConfigParser
except:
    import ConfigParser
import os.path


def get_config(config_info_file=None):
    """ Sample Use Case
    ============================================================================
    config_info_file="C:\\Users\\username\\project\\nbi_jv-nbijv\\notebooks\\upload_config.ini"
    data = get_config("your config file")
    files = data[0]   /* file path
    group_names = data[1]  /* ['Accelerator', 'Gyroscrop']
    group_columns = data[2]  /* ['3,4,5', '6,7,8']
    data_column_names = data[3]  /* ['accelx,accely,accelz', 'gyrox,gyroy,gyroz']
    metadata_columns = data[4]  /* [0,1]
    """
    if config_info_file is None:
        raise Exception("*** Sorry, Config File Missing *** " + "file exist? " +
                        str(os.path.isfile(config_info_file)) + '..filename: ' + config_info_file)

    config = ConfigParser.ConfigParser()
    config.read(config_info_file)
    sections = config.sections()
    if "File_Path" in sections[0]:
        filePath = config.get(sections[0], 'path')
    else:
        print("Can not read config file...")

    # First try absolute path
    files = glob(filePath)
    if not files:
        # Then try relative to upload config file
        files = glob(os.path.join(
            os.path.split(config_info_file)[0], filePath))

    for i in range(len(files)):
        if os.path.splitext(files[i])[1] == '.h5':
            return [files, None, None, None, None]

    group_names = config.get(sections[1], 'group_name')
    group_columns = config.get(sections[1], 'group_column')
    data_column_names = config.get(sections[1], 'data_column_name')
    metadata_columns = (config.get(sections[2], 'metadata_column')).split(
        ',') if len(sections) > 2 else None
    groupnames = group_names.split('/')
    groupcolumns = group_columns.split('/')
    datacolumnnames = data_column_names.split('/')
    #metadatacolumns = metadata_columns.split(',')

    return [files, groupnames, groupcolumns, datacolumnnames, metadata_columns]
