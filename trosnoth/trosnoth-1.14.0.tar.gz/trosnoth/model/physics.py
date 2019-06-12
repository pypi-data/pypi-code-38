# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2012 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import logging
from math import atan2

from trosnoth.model.modes import PhysicsConstants
from trosnoth.utils.math import isNear, RotatedAxes

log = logging.getLogger(__name__)


class Collision(object):
    def __init__(self, startPos, delta, contactPoint, surfaceAngle, ledge=False):
        self.start = startPos
        self.end = (startPos[0] + delta[0], startPos[1] + delta[1])
        self.contactPoint = contactPoint
        self.angle = surfaceAngle
        self.travelDistance = (delta[0] ** 2 + delta[1] ** 2) ** 0.5
        self.ledge = ledge


class CollisionShape(object):
    '''
    Abstract base class for shapes to be used for collision testing against
    obstacles and ledges in the game world.
    '''

    def getMotionBounds(self, start, vector):
        '''
        :param start: the initial position of a unit of this shape
        :param vector: the (deltaX, deltaY) that the unit is moving
        :return: x0, y0, x1, y1 that bounds the unit's motion
        '''
        raise NotImplementedError(
            '{}.getRect()'.format(self.__class__.__name__))

    def checkConcavePolygonCollision(self, start, vector, polygon):
        '''
        Checks whether the a unit of this shape travelling along the given
        vector would collide with the given fixed closed polygon.

        :param start: the start position of the unit
        :param vector: the (deltaX, deltaY) that the unit is moving
        :param polygon: the polygon to test against
        :return: a Collision object, or None for no collision
        '''
        raise NotImplementedError('{}.checkConcavePolygonCollision()'.format(
            self.__class__.__name__))

    def checkLedgeCollision(self, start, vector, polygon):
        '''
        Checks whether the a unit of this shape travelling along the given
        vector would collide with the given one-way open polygon.

        :param start: the start position of the unit
        :param vector: the (deltaX, deltaY) that the unit is moving
        :param polygon: the open polygon to test against
        :return: a Collision object, or None for no collision
        '''
        raise NotImplementedError('{}.checkConcavePolygonCollision()'.format(
            self.__class__.__name__))


class CollisionEllipse(CollisionShape):
    def __init__(self, xRadius, yRadius):
        self.rx = xRadius
        self.ry = yRadius

    def getMotionBounds(self, start, vector):
        x, y = start
        dx, dy = vector

        x0 = x - self.rx + min(0, dx)
        x1 = x + self.rx + max(0, dx)
        y0 = y - self.ry + min(0, dy)
        y1 = y + self.ry + max(0, dy)
        return x0, y0, x1, y1

    def checkConcavePolygonCollision(self, start, vector, polygon):
        '''
        Checks whether the a unit of this shape travelling along the given
        vector would collide with the given fixed polygon.

        :param start: the start position of the unit
        :param vector: the (deltaX, deltaY) that the unit is moving
        :param polygon: the polygon to test against
        :return: a Collision object, or None for no collision
        '''

        # Check if entire polygon is outside of the motion path of this unit
        points = list(polygon.getPoints())
        for axis in self.getMotionBoundaries(start, vector):
            for point in points:
                if self.pointLiesInside(point, axis):
                    break
            else:
                # All points lie outside this boundary, so no collision occurs
                return None

        # Check an infinite line along each polygon edge to see how far the
        # unit could move before hitting that axis.
        vectorDist = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
        edgeDist, edgeContact, edgeAngle = self.getEdgeCollision(
            start, vector, polygon)
        if edgeDist is None:
            # Entire motion path is separated by an edge axis,
            # so no collision occurs.
            return None

        if edgeDist < 0:
            # Start position lies partially or fully inside the polygon. Try
            # starting with a magical nudge.
            r = min(0.5, 0.1 / vectorDist)
            nudgeX = vector[0] * r
            nudgeY = vector[1] * r
            start2 = (start[0] + nudgeX, start[1] + nudgeY)
            vector2 = (vector[0] - nudgeX, vector[1] - nudgeY)

            edgeDist2, edgeContact2, edgeAngle2 = self.getEdgeCollision(
                start2, vector2, polygon)
            if edgeDist2 is None:
                # Entire motion path is separated by an edge axis,
                # so no collision occurs.
                return None
            if edgeDist2 >= 0:
                # No longer inside the polygon, so go with this calculation
                edgeDist = edgeDist2 + r * vectorDist
                edgeContact = edgeContact2
                edgeAngle = edgeAngle2
            else:
                # Still inside the polygon. Try nudging the other way.
                start2 = (start[0] - nudgeX, start[1] - nudgeY)

                edgeDist2, edgeContact2, edgeAngle2 = self.getEdgeCollision(
                    start2, vector2, polygon)
                if edgeDist2 is None:
                    return None

                if edgeDist2 >= 0:
                    edgeDist = edgeDist2 - r * vectorDist
                    edgeContact = edgeContact2
                    edgeAngle = edgeAngle2

        vertexDist, vertex, vertexAngle = self.getVertexCollision(
            start, vector, points)

        if vertexDist is None:
            # Tangent to ellipse does not separate shapes,
            # so edge collision occurs before vertex collision.
            finalDist = edgeDist
            if edgeContact is None:
                contactPoint = start
            else:
                contactPoint = edgeContact
            if edgeAngle is None:
                # Already inside polygon. Use normal to direction of travel.
                surfaceAngle = atan2(-vector[0], vector[1])
            else:
                surfaceAngle = edgeAngle
        elif vertexDist >= vectorDist:
            # Vertex collision would occur past end of intended motion path
            return None
        elif vertexDist < 0:
            # Unit has already passed the polygon
            return None
        else:
            # Vertex collision occurs before edge collision
            finalDist = vertexDist
            contactPoint = vertex
            surfaceAngle = vertexAngle

        if isNear(finalDist, 0):
            actualVector = (0.0, 0.0)
        else:
            f = finalDist / vectorDist
            actualVector = (vector[0] * f, vector[1] * f)

        return Collision(start, actualVector, contactPoint, surfaceAngle)

    def checkLedgeCollision(self, start, vector, polygon):
        '''
        Checks whether the a unit of this shape travelling along the given
        vector would collide with the given one-way open polygon.

        :param start: the start position of the unit
        :param vector: the (deltaX, deltaY) that the unit is moving
        :param polygon: the open polygon to test against
        :return: a Collision object, or None for no collision
        '''
        vectorDist = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
        for x1, y1, x2, y2 in polygon.getEdges():
            dist, contactPoint = self.getMaxMotionToAxis(
                start, vector, x1, y1, x2, y2)

            if dist is None or dist >= vectorDist or dist < 0:
                # Does not collide with this infinite axis
                continue

            cx, cy = contactPoint
            if (
                    x1 <= cx <= x2 or x2 <= cx <= x1
                    or isNear(cx, x1) or isNear(cx, x2)):
                if (
                        y1 <= cy <= y2 or y2 <= cy <= y2
                        or isNear(cy, y1) or isNear(cy, y2)):
                    if isNear(dist, 0):
                        actualVector = (0.0, 0.0)
                    else:
                        f = dist / vectorDist
                        actualVector = (vector[0] * f, vector[1] * f)
                    surfaceAngle = atan2(y2 - y1, x2 - x1)
                    return Collision(
                        start, actualVector, contactPoint, surfaceAngle, ledge=True)

        points = list(polygon.getPoints())
        dist, vertex, surfaceAngle = self.getVertexCollision(
            start, vector, points, closed=False)

        if dist is None or dist >= vectorDist or dist <= 0:
            # Does not collide with any of the vertices
            return None

        if isNear(dist, 0):
            actualVector = (0.0, 0.0)
        else:
            f = dist / vectorDist
            actualVector = (vector[0] * f, vector[1] * f)
        return Collision(start, actualVector, vertex, surfaceAngle, ledge=True)

    def getMotionBoundaries(self, start, vector):
        '''
        :param start: the start position of a unit of this shape
        :param vector: the (deltaX, deltaY) the unit is moving
        :return: iterable of axes representing the edges of this motion path.
        '''
        x0, y0 = self.getSurfacePointFromTangent(start, vector)
        yield (x0, y0), RotatedAxes(vector=vector)

        reverseVector = (-vector[0], -vector[1])
        x1, y1 = self.getSurfacePointFromTangent(start, reverseVector)
        yield (x1, y1), RotatedAxes(vector=reverseVector)

    def getSurfacePointFromTangent(self, origin, tangent):
        '''
        :param origin: the centre of the ellipse
        :param tangent: a vector representing the direction of the tangent
        :return: the point where a tangent of that slope would touch the
            ellipse.
        '''
        # Scale into a coordinate system where the ellipse is circular
        tx, ty = tangent
        tx /= self.rx
        ty /= self.ry

        length = (tx ** 2 + ty ** 2) ** 0.5
        x = self.rx * ty / length
        y = -self.ry * tx / length

        x0, y0 = origin
        return x0 + x, y0 + y

    def pointLiesInside(self, point, axis):
        # NOTE: boundary is counted as outside
        origin, rotatedAxes = axis
        s, t = rotatedAxes.rotatedFromGlobal(point, origin=origin)
        return t > 0 and not isNear(t, 0, epsilon=0.01)

    def getEdgeCollision(self, start, vector, polygon):
        '''
        :param start: the start position of a unit of this shape
        :param vector: the unit's attempted displacement vector
        :param polygon: a LeafNode representing the closed polygon to test
        :return: (dist, contactPoint, angle) for the greatest distance the
            unit can travel and still have a separating axis, or (None,
            None, None) if the entire displacement vector still is separated
            by an axis along one of the polygon edges.
        '''
        vectorDist = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
        edgeDist = 0
        edgeContact = edgeAngle = None
        for x1, y1, x2, y2 in polygon.getEdges():
            dist, contactPoint = self.getMaxMotionToAxis(
                start, vector, x1, y1, x2, y2)
            if dist is None or dist >= vectorDist:
                # Entire motion path is separated by this axis,
                # so no collision occurs.
                return None, None, None

            # Find the furthest it can move and still be separated by an axis
            if dist > edgeDist or edgeAngle is None:
                edgeDist = dist
                edgeContact = contactPoint
                edgeAngle = atan2(y2 - y1, x2 - x1)

        return edgeDist, edgeContact, edgeAngle

    def getMaxMotionToAxis(self, start, vector, x1, y1, x2, y2):
        '''
        :param start: the start position of a unit of this shape
        :param vector: the (deltaX, deltaY) that the unit is trying to move
        :param x1, y1: defines the first point of the axis to test
        :param x2, y2: defines the second point of the axis to test
        :return: (dist, contactPoint) where:
            dist: is the maximum distance the unit could travel in this
                direction and still lie entirely outside the axis defined by
                the given points.
            contactPoint: is the point of collision with the axis.

            If the unit is already inside the axis, returns (-0.05, None),
            so that collisions touching the surface are distinguishable from
            those where the unit is already inside the axis.
            If even an infinite motion would leave the unit outside the
            axis, returns (None,  None).

        Note that the parameter vector is only used to to determine the
        direction of motion, but its magnitude is ignored, so this method
        may return a distance greater than the length of vector.
        '''

        # Find the point on the ellipse which would collide
        nx, ny = (x2 - x1), (y2 - y1)
        x0, y0 = self.getSurfacePointFromTangent(start, (-nx, -ny))

        crossProduct1 = nx * (y1 - y0) - ny * (x1 - x0)
        ellipseTouchesAxis = isNear(crossProduct1, 0)
        if crossProduct1 < 0 and not ellipseTouchesAxis:
            # Point on ellipse is already inside the axis
            return (-0.05, None)

        mx, my = vector
        divisor = my * nx - mx * ny
        if divisor <= 0 or isNear(divisor, 0):
            # Moving away from or parallel to this axis
            return (None, None)

        x = ((y1 - y0) * mx * nx + x0 * my * nx - x1 * mx * ny) / divisor
        y = -((x1 - x0) * my * ny + y0 * mx * ny - y1 * my * nx) / divisor
        dist = ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5

        return dist, (x, y)

    def getVertexCollision(self, start, vector, points, closed=True):
        '''
        Calculates the greatest distance this shaped unit would move
        along the given path before colliding with a vertex of the given
        polygon.

        :param start: the starting point of the unit
        :param vector: the direction of motion
        :param points: the points of the polygon
        :param closed: True for a closed polygon, False for open
        :return: (dist, vertex, tangentAngle), where
            dist: the distance moved, or None if none of the vertices have a
                separating axis that aligns with the tangent of the ellipse
                (that is, none of the vertices can be hit without first hitting
                an edge).
            vertex: the point of collision
            tangentAngle: the angle of the tangent at the point of collision

        Note that dist may be negative, in cases where the ellipse has passed
        the polygon already.
        '''
        sx, sy = start

        # Transform into a coordinate system where the ellipse is a circle
        magnitude = (
            (vector[0] / self.rx) ** 2 + (vector[1] / self.ry) ** 2) ** 0.5
        mx = vector[0] / magnitude / self.rx
        my = vector[1] / magnitude / self.ry

        if closed:
            iterator = self.iterClosedPolygonPoints(points)
        else:
            iterator = self.iterOpenPolygonPoints(points)

        for lastPoint, point, nextPoint in iterator:
            x1 = (point[0] - sx) / self.rx
            y1 = (point[1] - sy) / self.ry

            # Project this vertex onto the circle
            radicand = 1 - (mx * y1 - my * x1) ** 2
            if radicand > 0 and not isNear(radicand, 0):
                # Entire circle will not miss this vertex
                k = mx * x1 + my * y1 - radicand ** 0.5
                if isNear(k, 0):
                    # Make sure that it's definitely not negative
                    k = 0.0
                elif k < 0:
                    # Unit is either inside or past this polygon
                    k2 = mx * x1 + my * y1 + radicand ** 0.5
                    if isNear(k2, 0):
                        # Make sure that it's definitely negative, for the
                        # sake of later tests that check if the collision is
                        # before or after the polygon.
                        k2 = -0.000001
                    if k2 > 0:
                        # Unit is inside this polygon
                        return None, None, None

                    # Unit is past this polygon, so use the other side of
                    # the circle for subsequent calculations.
                    k = k2

                # Find collision point on circle
                cx = x1 - k * mx
                cy = y1 - k * my

                # Check the slope of the tangent is within allowed bounds
                tx = -cy * self.rx
                ty = cx * self.ry
                prevSegmentProduct = tx * (point[1] - lastPoint[1]) \
                                     - ty * (point[0] - lastPoint[0])
                inPrevSegment = prevSegmentProduct > 0 and not isNear(
                    prevSegmentProduct, 0)
                nextSegmentProduct = (nextPoint[0] - point[0]) * ty \
                                     - (nextPoint[1] - point[1]) * tx
                inNextSegment = nextSegmentProduct > 0 and not isNear(
                    nextSegmentProduct, 0)
                if inPrevSegment and inNextSegment:
                    # Because both objects are convex, only one collision is
                    # possible, so no need to check other vertices.
                    dist = k * ((mx * self.rx) ** 2 + (my * self.ry) ** 2) ** 0.5
                    return dist, point, atan2(-ty, -tx)

        return None, None, None

    def iterClosedPolygonPoints(self, points):
        lastPoint, point = points[-2:]
        for nextPoint in points:
            yield lastPoint, point, nextPoint
            lastPoint, point = point, nextPoint

    def iterOpenPolygonPoints(self, points):
        # End point: make a false previous point 90 degrees to the next
        p0, p1 = points[:2]
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        yield (p0[0] - dy, p0[1] + dx), p0, p1

        for i in range(1, len(points) - 1):
            yield points[i - 1], points[i], points[i + 1]

        # End point: make a false next point 90 degrees to the previous
        p1, p2 = points[-2:]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        yield p1, p2, (p2[0] - dy, p2[1] + dx)


def CollisionCircle(radius):
    result = CollisionEllipse(radius, radius)
    result.debug = True
    return result


class WorldPhysics(PhysicsConstants):
    def __init__(self, world):
        PhysicsConstants.__init__(self)
        self.world = world

    def getCollision(self, unit, vector, *, ignoreLedges=False):
        '''
        Returns a Colision object that results from moving the given unit by
        the given vector.
        '''
        if isNear(vector[0], 0) and isNear(vector[1], 0):
            return None

        collisions = []
        for polygon in self.getCandidatePolygons(unit, vector):
            if ignoreLedges and polygon.isLedge():
                continue
            collision = self.checkCollision(unit, vector, polygon)
            if collision:
                collisions.append(collision)
        if not collisions:
            return None
        return min(collisions, key=lambda c: c.travelDistance)

    def getCandidatePolygons(self, unit, vector):
        x0, y0, x1, y1 = unit.collisionShape.getMotionBounds(unit.pos, vector)
        return self.world.layout.getCandidatePolygons(x0, y0, x1, y1)

    def checkCollision(self, unit, vector, polygon):
        '''
        :return: a Collision instance, or None
        '''
        shape = unit.collisionShape
        start = unit.pos
        if polygon.isLedge():
            return shape.checkLedgeCollision(start, vector, polygon)
        return shape.checkConcavePolygonCollision(start, vector, polygon)

    def getMotion(self, unit, vector, *, ignoreLedges=False):
        '''
        Returns (endPos, collision) for the given proposed motion of the
        given unit.
        '''
        collision = self.getCollision(
            unit, vector, ignoreLedges=ignoreLedges)
        if collision:
            return collision.end, collision
        return (unit.pos[0] + vector[0], unit.pos[1] + vector[1]), None
