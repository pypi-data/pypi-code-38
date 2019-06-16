
import math
import scipy.spatial.distance
import matplotlib.pyplot as plot
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from sklearn.cluster import KMeans
import argparse

from echidna_obj.parse_simple_ import ObjSimple


class ObjTube(ObjSimple):
    def get_count(self):
        """ Identify the amount of clusters based on material property informations.
        @return cluster_count The amount of objects i.e. clusters
        """
        objectfile = self.get_file()
        lines = [line.rstrip('\n') for line in objectfile]
        count = 0
        for line in lines:
            if line.startswith('usemtl'):
                count += 1
        cluster_count = count * 2
        return cluster_count

    def get_centers(self):
        """ Identify the center point coordinates of each top and bottom surface of cylinder primitive based on vertices,
        describing the cylinder mesh.
        @return centers A list of vertices
        """
        vertices = self.get_vertices()
        centers = []
        for i in vertices:
            k_means = KMeans(n_clusters=2).fit(i)
            center = k_means.cluster_centers_
            centers.append(center)
        return centers

    def generate_edges(self):
        """ Generate edges in between the calculated center point coordinates based on indices.
        @return edges A set (pair) of edges defined by two points per edge
        """
        centers = self.get_centers()
        centers_new = [value for sublist in centers for value in sublist]
        edges = []
        for idx, val in enumerate(centers_new):
            if idx % 2 == 0:
                center_vertex1 = idx
                if idx + 1 < len(centers_new):
                    center_vertex2 = idx + 1
                    pair = (center_vertex1, center_vertex2)
                    edges.append(pair)
        return edges

    def calc_edgelength(self):
        """ Calculate edge lengths based on generated edges of centers.
        @return edge_length A list of edge lengths
        """
        centers = self.get_centers()
        centers_new = [value for sublist in centers for value in sublist]
        edges = [(centers_new[i], centers_new[i + 1] if i + 1 < len(centers_new) else None) for i in
                 range(0, len(centers_new), 2)]
        edge_length = []
        for points in edges:
            p1 = points[0]
            p2 = points[1]
            distance = scipy.spatial.distance.euclidean(p1, p2)
            edge_length.append(distance)
        return edge_length

    def calc_bplength(self):
        """ Divide and calculate the base pair count of each edge based on the division factor or 3.4 Angstrom for B-DNA.
        @return bp_list A list of integer number representing the base pair count per edge
        """
        edge_length = self.calc_edgelength()
        div = 0.34
        bp_list = []
        for item in edge_length:
            bp = math.floor(item / div)
            bp_list.append(bp)
        return bp_list
    
    def get_startvertices(self):
        """ Identify the start vertices based on center point coordinates.
        @return starts A list of the start vertices
        """
        centers = self.get_centers()
        centers_new = [value for sublist in centers for value in sublist]
        edges = [(centers_new[i], centers_new[i + 1] if i + 1 < len(centers_new) else None) for i in
                 range(0, len(centers_new), 2)]
        x_coord = 0
        y_coord = 1
        z_coord = 2
        starts = []
        ends = []
        for points in edges:
            startpoint = points[0]
            endpoint = points[1]
            x1, y1, z1 = startpoint[x_coord], startpoint[y_coord], startpoint[z_coord]
            x2, y2, z2 = endpoint[x_coord], endpoint[y_coord], endpoint[z_coord]
            if z1 < z2:
                starts.append(startpoint)
                ends.append(endpoint)
            elif z2 < z1:
                starts.append(endpoint)
                ends.append(startpoint)
        return starts

    def get_endvertices(self):
        """ Identify the end vertices based on center point coordinates.
        @return ends A list of the end vertices
        """
        centers = self.get_centers()
        centers_new = [value for sublist in centers for value in sublist]
        edges = [(centers_new[i], centers_new[i + 1] if i + 1 < len(centers_new) else None) for i in
                 range(0, len(centers_new), 2)]
        x_coord = 0
        y_coord = 1
        z_coord = 2
        starts = []
        ends = []
        for points in edges:
            startpoint = points[0]
            endpoint = points[1]
            x1, y1, z1 = startpoint[x_coord], startpoint[y_coord], startpoint[z_coord]
            x2, y2, z2 = endpoint[x_coord], endpoint[y_coord], endpoint[z_coord]
            if z1 < z2:
                starts.append(startpoint)
                ends.append(endpoint)
            elif z2 < z1:
                starts.append(endpoint)
                ends.append(startpoint)
        return ends

    def get_direction(self):
        """ Calculate the direction of edges.
        @return dir_vector_norm A list of normalized directions as 3-component vectors
        """
        x_coord = 0
        y_coord = 1
        z_coord = 2
        starts = self.get_startvertices()
        ends = self.get_endvertices()

        dir_vector_norm = []
        for s, e in zip(starts, ends):
            x, y, z = (e[x_coord]-s[x_coord]), (e[y_coord]-s[y_coord]), (e[z_coord]-s[z_coord])
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
        centers = self.get_centers()
        centers_new = [value for sublist in centers for value in sublist]
        directions = self.get_direction()
        starts = self.get_startvertices()
        ends = self.get_endvertices()
        edge_lengths = self.calc_edgelength()

        x_list = [i[0] for i in vertices_new]
        y_list = [i[1] for i in vertices_new]
        z_list = [i[2] for i in vertices_new]
        fig = plot.figure()
        ax = Axes3D(fig)
        ax.set_xlim(min(x_list) - 5, max(x_list) + 5)
        ax.set_ylim(min(y_list) - 5, max(y_list) + 5)
        ax.set_zlim(min(z_list) - 5, max(z_list) + 5)

        x_list_center = [j[0] for j in centers_new]
        y_list_center = [j[1] for j in centers_new]
        z_list_center = [j[2] for j in centers_new]

        center_edges = self.generate_edges()
        segments = []
        for e in center_edges:
            x1, y1, z1 = x_list_center[e[0]], y_list_center[e[0]], z_list_center[e[0]]
            x2, y2, z2 = x_list_center[e[1]], y_list_center[e[1]], z_list_center[e[1]]
            seg = ((x1, y1, z1), (x2, y2, z2))
            segments.append(seg)
        ax.add_collection3d(Line3DCollection(segments, lw=1, linestyle='-', color='k'))

        for direct, start, length in zip(directions, starts, edge_lengths):
            ax.quiver(start[0], start[1], start[2], direct[0], direct[1], direct[2],
                      length=length, linewidths=0.5, color='gray', normalize=True)

        x_coord = 0
        y_coord = 1
        z_coord = 2
        for s in starts:
            ax.scatter(s[x_coord], s[y_coord], s[z_coord], c='green', marker='o')
        for e in ends:
            ax.scatter(e[x_coord], e[y_coord], e[z_coord], c='red', marker='o')

        plot.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_name', metavar='file',
                        help='Input directory for an object file.')
    args = parser.parse_args()
    ObjTube(args.file_name).vis()