
import math
import os
import scipy.spatial.distance
import matplotlib.pyplot as plot
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import argparse

from echidna_obj.parse_simple_ import ObjSimple


class ObjWire(ObjSimple):
    def generate_edges(self):
        """ Generate edges in between the calculated centerpoint coordinates.
        @return edges A set (pair) of edges defined by two points per edge
        """
        face_list = self.get_faces()
        edges = []
        for face in face_list:
            for i in range(0, len(face)):
                vertex_1 = face[i]
                vertex_2 = face[0]
                if i + 1 < len(face):
                    vertex_2 = face[i + 1]
                pair = (vertex_1, vertex_2)
                edges.append(pair)
        edge_direction_1 = [(vertex_1, vertex_2) for (vertex_1, vertex_2) in edges if vertex_1 > vertex_2]
        # edge_direction_2 = [(vertex_1, vertex_2) for (vertex_1, vertex_2) in edges if vertex_2 > vertex_1]
        # edges_all_directions = (edge_direction_1 + edge_direction_2)
        return edge_direction_1

    def get_segments(self):
        vertices = self.get_vertices()
        vertices_new = [value for sublist in vertices for value in sublist]

        edges = self.generate_edges()
        x_coord = 0
        y_coord = 1
        z_coord = 2
        segments = []
        for edge in edges:
            x1, y1, z1 = vertices_new[edge[0]][x_coord], vertices_new[edge[0]][y_coord], vertices_new[edge[0]][z_coord]
            x2, y2, z2 = vertices_new[edge[1]][x_coord], vertices_new[edge[1]][y_coord], vertices_new[edge[1]][z_coord]
            segment = (x1, y1, z1), (x2, y2, z2)
            if segment not in segments:
                segments.append(segment)
        return segments

    def calc_edgelength(self):
        """ Calculate edge lengths based on generated edges of centers.
        @return edge_length A list of edge lengths
        """
        segments = self.get_segments()
        edge_length = []
        for points in segments:
            point_1 = points[0]
            point_2 = points[1]
            distance = scipy.spatial.distance.euclidean(point_1, point_2)
            edge_length.append(distance)
        return edge_length

    def get_startvertices(self):
        """ Identify the start vertices based on center point coordinates.
        @return starts A list of the start vertices
        """
        vertices = self.get_vertices()
        vertices_new = [value for sublist in vertices for value in sublist]

        edges = [(vertices_new[i], vertices_new[i + 1] if i + 1 < len(vertices_new) else None) for i in
                 range(0, len(vertices_new))]
        starts = []
        ends = []
        for points in edges:
            point1 = points[0]
            point2 = points[1]
            starts.append(point1)
            ends.append(point2)
        return starts

    def get_direction(self):
        """ Calculate the direction of edges.
        @return dir_vector_norm A list of normalized directions as 3-component vectors
        """
        segments = self.get_segments()
        x_coord = 0
        y_coord = 1
        z_coord = 2
        dir_vector_norm = []
        for s in segments:
            startpoint = s[0]
            endpoint = s[1]
            x, y, z = (endpoint[x_coord]-startpoint[x_coord]), (endpoint[y_coord]-startpoint[y_coord]), (endpoint[z_coord]-startpoint[z_coord])
            vector_length = (x ** 2 + y ** 2 + z ** 2) ** 0.5
            x_norm = x / vector_length
            y_norm = y / vector_length
            z_norm = z / vector_length
            direct = [x_norm, y_norm, z_norm]
            dir_vector_norm.append(direct)
        return dir_vector_norm

    def vis(self):
        """ Abstract 3D respresentation of the obj file.
        @return 3D plot of parsed object file
        """
        vertices = self.get_vertices()
        vertices_new = [value for sublist in vertices for value in sublist]
        starts = self.get_startvertices()
        directions = self.get_direction()
        edge_lengths = self.calc_edgelength()

        x_list = [i[0] for i in vertices_new]
        y_list = [i[1] for i in vertices_new]
        z_list = [i[2] for i in vertices_new]
        fig = plot.figure()
        ax = Axes3D(fig)
        ax.set_xlim(min(x_list) - 5, max(x_list) + 5)
        ax.set_ylim(min(y_list) - 5, max(y_list) + 5)
        ax.set_zlim(min(z_list) - 5, max(z_list) + 5)

        x_coord = 0
        y_coord = 1
        z_coord = 2
        for i in range(len(starts)):
            ax.scatter(starts[i][x_coord], starts[i][y_coord], starts[i][z_coord],
                       c='green', marker='o')

        segments = self.get_segments()
        ax.add_collection3d(Line3DCollection(segments, lw=1.0, linestyle='-', color='k'))

        for direct, start, length in zip(directions, starts, edge_lengths):
            ax.quiver(start[0], start[1], start[2], direct[0], direct[1], direct[2],
                      length=length, linewidths=0.5, color='gray', normalize=True)

        plot.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_name', metavar='file',
                        help='Input a directory for an object file.')
    args = parser.parse_args()
    ObjWire(args.file_name).vis()
