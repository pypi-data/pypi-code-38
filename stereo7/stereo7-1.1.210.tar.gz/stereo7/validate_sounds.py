import xml.etree.ElementTree as ET
import os
import fileutils

logs = []


def validate():
    root = ET.parse(fileutils.root_dir + '/Resources/ini/sounds.xml').getroot()
    for sound in root:
        file = sound.attrib['value']
        file = file.replace('##music_dir##', '/Resources/audio/music/')
        file = file.replace('##sound_dir##', '/Resources/audio/sound/')
        file = file.replace('##music_ext##', '.mp3')
        file = file.replace('##sound_ext##', '.mp3')
        file = fileutils.root_dir + file
        abspath = os.path.abspath(file)
        abspath = abspath.replace('\\', '/')
        file = file.replace('\\', '/')
        if not os.path.isfile(file) or file != abspath:
            logs.append('Not founded: ' + file + ' name: ' + sound.attrib['name'])
