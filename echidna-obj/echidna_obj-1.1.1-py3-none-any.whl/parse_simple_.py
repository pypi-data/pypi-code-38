
import os
import re


class ObjSimple:
    def __init__(self, file_name=None):
        self.file = file_name
        if file_name is None:
            self.file = input("Please enter the path to your .obj file: ")
        elif not os.path.isfile(self.file):
            raise FileExistsError('Did not find the file at the chosen path, {}, please try again.'.format(str(self.file)))

    def get_file(self):
        """ Read object file.
        @return the Object file
        """
        obj_file = self.file
        with open(obj_file, 'r') as f:
            obj = f.readlines()
        return obj

    def get_vertices(self):
        """ Identify the values of vertices of an .obj file.
        @return vertices A list of vertices
        """
        objectfile = self.get_file()
        lines = [line.rstrip('\n') for line in objectfile]
        vertices = []
        for i in range(0, len(lines)):
            obj_v = []
            pattern = 'usemtl'
            file_line = lines[i]
            if re.search(pattern, file_line):
                if i + 1 < len(lines):
                    new_lines = lines[i + 1:]
                    for line in new_lines:
                        new_split = line.split()
                        if new_split[0] == 'v':
                            v = new_split[1:]
                            vertex = [float(x) for x in v]
                            if vertex not in obj_v:
                                obj_v.append(vertex)
                        elif new_split[0] != 'v':
                            break
                vertices.append(obj_v)
        return vertices

    def get_faces(self):
        """ Identify the faces of the file.
        @return vertices A list of faces
        """
        obj_file = self.get_file()
        face_list = []
        for line in obj_file:
            split = line.split()
            if len(split) == 0:
                continue
            elif split[0] == 'f':
                face = []
                for value in split[1:]:
                    face_vertex = value.split('/')
                    face.append(int(face_vertex[0]) - 1)
                face_list.append(face)
        return face_list


