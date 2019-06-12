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

from math import pi
import pygame


class ImageCollection(object):
    def __init__(self, *images):
        for image in images:
            if not isinstance(image, pygame.Surface):
                raise TypeError('%r is not a pygame.Surface' % (image,))
        self.images = images

    def getImage(self):
        raise NotImplementedError('getImage not implemented')


class SingleImage(ImageCollection):
    def __init__(self, image):
        super(SingleImage, self).__init__(image)

    def getImage(self):
        return self.images[0]


class AngledImageCollection(ImageCollection):
    def __init__(self, angleFn, *images):
        super(AngledImageCollection, self).__init__(*images)
        self.angleFn = angleFn

    def getImage(self):
        angle = (self.angleFn() + pi) % (2 * pi) - pi
        numImages = len(self.images)
        point = abs(int(angle * numImages / pi))
        if point == len(self.images):
            point -= 1
        image = self.images[point]
        return image


class Animation(ImageCollection):
    def __init__(self, speed, timeFunction, *images):
        super(Animation, self).__init__(*images)
        self.speed = speed
        self.timeFunction = timeFunction
        self.startNow()

    def getImage(self):
        elapsed = self.timeFunction() - self.start
        cycles = int(elapsed / self.speed)
        imgIndex = cycles % len(self.images)
        if elapsed > self.speed * len(self.images):
            self.start -= self.speed * len(self.images)
        return self.images[imgIndex]

    def startNow(self):
        self.start = self.timeFunction()

    def isComplete(self):
        elapsed = self.timeFunction() - self.start
        cycles = int(elapsed / self.speed)
        return cycles >= len(self.images)


class AnimationWithStart(Animation):
    '''Animation loop that starts with a set sequence (that doesn't loop),
    then goes into the main loop'''
    # NOTE: This class is untested. Remove this comment once you are certain
    #       it works correctly

    def __init__(self, speed, numInitial, timeFunction, *images):
        self.initial = True
        super(AnimationWithStart, self).__init__(
            speed, timeFunction, *images[numInitial - 1:])
        self.initialAnimation = Animation(speed, *images[:numInitial])

    def startNow(self):
        super(AnimationWithStart, self).startNow()
        self.initial = True

    def getImage(self):
        elapsed = self.timeFunction() - self.start
        cycles = int(elapsed / self.speed)
        imgIndex = cycles % len(self.images)
        if elapsed > self.speed * len(self.images):
            self.start -= self.speed * len(self.images)
            self.initial = False
        if self.initial:
            return self.initialAnimation.getImage()
        else:
            return self.images[imgIndex]
