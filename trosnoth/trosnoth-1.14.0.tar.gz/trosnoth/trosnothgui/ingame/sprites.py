

import datetime
import logging
from enum import Enum
import math
from math import pi
import random
import time

import pygame
import pygame.gfxdraw

from trosnoth.const import (
    MAP_TO_SCREEN_SCALE, COLLECTABLE_COIN_LIFETIME, TICK_PERIOD,
    DEFAULT_COIN_VALUE, HEAD_LOCATIONS, HEAD_BOT, HEAD_CUEBALL,
)
from trosnoth.gui.framework.basics import Animation
from trosnoth.model.player import Player
from trosnoth.trosnothgui.common import setAlpha
from trosnoth.trosnothgui.ingame.nametag import (
    NameTag, CoinTally, HealthBar, CountDown,
)
from trosnoth.trosnothgui.ingame.utils import mapPosToScreen
from trosnoth.utils.math import fadeValues, isNear

log = logging.getLogger(__name__)


class UnitSprite(pygame.sprite.Sprite):
    def __init__(self, app, worldGUI, unit):
        super(UnitSprite, self).__init__()
        self.app = app
        self.worldGUI = worldGUI
        self.unit = unit

    @property
    def pos(self):
        return self.unit.tweenPos(self.worldGUI.tweenFraction)


class ShotSprite(object):
    TICK_TRAIL = 1.3

    def __init__(self, app, worldGUI, shot):
        self.app = app
        self.worldGUI = worldGUI
        self.shot = shot
        self.colour = app.theme.colours.shot(shot.team)
        ticks = worldGUI.universe.monotonicTicks - 1
        self.drawPoints = [(ticks, shot.tweenPos(0))]

        shot.onRebound.addListener(self.gotRebound)
        shot.onExpire.addListener(self.gotExpire)

    def noLongerInUniverse(self):
        if self.shot:
            self.shot.onRebound.removeListener(self.gotRebound)
            self.shot.onExpire.removeListener(self.gotExpire)
            self.shot = None

    def gotRebound(self, pos):
        self._addDrawPoint(pos)

    def gotExpire(self):
        self._addDrawPoint(self.shot.pos)

    def _addDrawPoint(self, pos):
        self.drawPoints.append((self.worldGUI.universe.monotonicTicks, pos))

    @property
    def pos(self):
        if self.shot:
            return self.shot.tweenPos(self.worldGUI.tweenFraction)
        return None

    def shouldRemove(self):
        if self.shot is not None:
            return False
        if len(self.drawPoints) >= 2:
            return False
        return True

    def draw(self, screen, focus, area):
        wg = self.worldGUI
        worldTicks = wg.universe.monotonicTicks

        addedFinalPoint = False
        if self.shot and self.drawPoints:
            tick, _ = self.drawPoints[-1]
            if tick < worldTicks:
                addedFinalPoint = True
                self._addDrawPoint(self.shot.pos)

        ticksNow = worldTicks - 1 + wg.tweenFraction
        tickCutoff = ticksNow - self.TICK_TRAIL
        self._discardDrawPointsBefore(tickCutoff)
        self._drawPointsUntil(ticksNow, screen, focus, area)

        if addedFinalPoint:
            del self.drawPoints[-1]

    def _discardDrawPointsBefore(self, tickCutoff):
        lastTick = lastPos = None
        while True:
            if not self.drawPoints:
                return
            thisTick, thisPos = self.drawPoints[0]
            if thisTick >= tickCutoff:
                break
            self.drawPoints.pop(0)
            lastTick, lastPos = thisTick, thisPos

        if lastTick is not None:
            fraction = (tickCutoff - lastTick) / (thisTick - lastTick)
            insertPoint = (
                fadeValues(lastPos[0], thisPos[0], fraction),
                fadeValues(lastPos[1], thisPos[1], fraction),
            )
            self.drawPoints.insert(0, (tickCutoff, insertPoint))

    def _drawPointsUntil(self, ticksNow, screen, focus, area):
        if not self.drawPoints:
            return

        ticks0, pos = self.drawPoints[0]
        screenPos0 = mapPosToScreen(pos, focus, area)
        points = [screenPos0]
        for ticks1, pos in self.drawPoints[1:]:
            screenPos1 = mapPosToScreen(pos, focus, area)
            if ticks1 > ticksNow:
                fraction = (ticksNow - ticks0) / (ticks1 - ticks0)
                points.append((
                    fadeValues(screenPos0[0], screenPos1[0], fraction),
                    fadeValues(screenPos0[1], screenPos1[1], fraction),
                ))
                break

            points.append(screenPos1)
            screenPos0 = screenPos1
            ticks0 = ticks1

        if len(points) > 1:
            self.drawLines(screen, area, self.colour, points, thickness=6)

    def drawLines(self, screen, area, colour, points, thickness):
        rect = pygame.Rect(points[0], (0, 0))
        for point in points[1:]:
            rect.union_ip(point, (0, 0))

        if not rect.colliderect(area):
            return

        if not self.app.displaySettings.antialiasedShots:
            pygame.draw.lines(screen, colour, False, points, thickness)
            return

        halfThick = thickness / 2
        outline = []
        x0, y0 = points[0]
        angle = 0
        pt0 = pt5 = None
        for (x1, y1) in points[1:]:
            if (x0, y0) != (x1, y1):
                angle = math.atan2(y1 - y0, x1 - x0)
            sinTheta = math.sin(angle)
            cosTheta = math.cos(angle)

            pt1 = (x0 + halfThick * sinTheta, y0 - halfThick * cosTheta)
            pt2 = (x1 + halfThick * sinTheta, y1 - halfThick * cosTheta)
            pt3 = (x1 - halfThick * sinTheta, y1 + halfThick * cosTheta)
            pt4 = (x0 - halfThick * sinTheta, y0 + halfThick * cosTheta)

            outline.append(pt1)
            outline.append(pt2)
            outline.insert(0, pt4)
            outline.insert(0, pt3)

            pygame.gfxdraw.filled_polygon(screen, [pt1, pt2, pt3, pt4], colour)
            if pt0 and pt5:
                pygame.gfxdraw.filled_polygon(screen, [pt0, pt1, pt4, pt5], colour)
                pygame.gfxdraw.filled_polygon(screen, [pt0, pt1, pt5, pt4], colour)

            x0, y0 = x1, y1
            pt0 = pt1
            pt5 = pt4

        pygame.gfxdraw.aapolygon(screen, outline, colour)


class SingleAnimationSprite(pygame.sprite.Sprite):
    def __init__(self, worldGUI, pos):
        super(SingleAnimationSprite, self).__init__()
        self.app = worldGUI.app
        self.worldGUI = worldGUI
        self.pos = pos
        self.animation = self.getAnimation()
        self.image = self.animation.getImage()
        self.rect = self.image.get_rect()

    def getAnimation(self):
        raise NotImplementedError('getAnimation')

    def update(self):
        self.image = self.animation.getImage()

    def isDead(self):
        return self.animation.isComplete()


class ExplosionSprite(SingleAnimationSprite):
    def getAnimation(self):
        return self.app.theme.sprites.explosion(self.worldGUI.getTime)


class ShoxwaveExplosionSprite(SingleAnimationSprite):
    def getAnimation(self):
        return self.app.theme.sprites.shoxwaveExplosion(self.worldGUI.getTime)


class TrosballExplosionSprite(SingleAnimationSprite):
    def getAnimation(self):
        return self.app.theme.sprites.trosballExplosion(self.worldGUI.getTime)


class GrenadeSprite(UnitSprite):
    def __init__(self, app, worldGUI, grenade):
        super(GrenadeSprite, self).__init__(app, worldGUI, grenade)
        self.grenade = grenade
        self.image = app.theme.sprites.teamGrenade(grenade.player.team)
        self.rect = self.image.get_rect()


class CollectableCoinSprite(UnitSprite):
    def __init__(self, app, worldGUI, coin):
        super(CollectableCoinSprite, self).__init__(app, worldGUI, coin)
        self.coin = coin
        if coin.value >= 2 * DEFAULT_COIN_VALUE:
            self.animation = app.theme.sprites.bigCoinAnimation(
                worldGUI.getTime)
        else:
            self.animation = app.theme.sprites.coinAnimation(worldGUI.getTime)
        self.image = self.animation.getImage()
        self.alphaImage = self.image.copy()
        self.rect = self.image.get_rect()
        self.timer = worldGUI.getTime

    def update(self):
        self.image = self.animation.getImage()
        tick = self.worldGUI.universe.getMonotonicTick()
        fadeTick = self.coin.creationTick + (
                COLLECTABLE_COIN_LIFETIME - 2) // TICK_PERIOD
        if tick >= fadeTick:
            alpha = random.randint(32, 192)
            self.image = self.image.copy()
            setAlpha(self.image, alpha, alphaSurface=self.alphaImage)


class TrosballSprite(pygame.sprite.Sprite):
    def __init__(self, app, worldGUI, world):
        super(TrosballSprite, self).__init__()
        self.app = app
        self.worldGUI = worldGUI
        self.world = world
        self.localState = worldGUI.gameViewer.interface.localState
        self.animation = app.theme.sprites.trosballAnimation(worldGUI.getTime)
        self.warningAnimation = app.theme.sprites.trosballWarningAnimation(
            worldGUI.getTime)
        # Need a starting one:
        self.image = self.animation.getImage()
        self.rect = self.image.get_rect()

    def update(self):
        self.image = self.animation.getImage()
        manager = self.world.trosballManager
        if manager.trosballPlayer is not None:
            trosballExplodeTick = manager.playerGotTrosballTick + (
                self.world.physics.trosballExplodeTime // TICK_PERIOD)
            warningTick = trosballExplodeTick - 2 // TICK_PERIOD
            if self.world.getMonotonicTick() > warningTick:
                self.image = self.warningAnimation.getImage()
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    @property
    def pos(self):
        manager = self.world.trosballManager
        if self.localState.localTrosball:
            x, y = self.localState.localTrosball.tweenPos(
                self.worldGUI.tweenFraction)
        elif manager.trosballUnit:
            x, y = manager.trosballUnit.tweenPos(self.worldGUI.tweenFraction)
        else:
            p = manager.trosballPlayer
            if p.id == self.worldGUI.localPlayerId:
                p = self.worldGUI.localPlayerSprite
            x, y = p.tweenPos(self.worldGUI.tweenFraction)
            x += 5 if p.isFacingRight() else -5
        return (x, y)


class PlayerSprite(UnitSprite):
    # These parameters are used to create a canvas for the player sprite object
    canvasSize = (
        int(33 * MAP_TO_SCREEN_SCALE + 0.5),
        int(40 * MAP_TO_SCREEN_SCALE + 0.5))
    liveOffset = 3
    ghostOffset = 0

    def __init__(self, app, worldGUI, player, timer=None):
        super(PlayerSprite, self).__init__(app, worldGUI, player)
        if timer is None:
            timer = self.worldGUI.getTime
        self.timer = timer
        self.drawer = PlayerDrawer(app, timer)
        self._animationStart = None
        self.spriteTeam = player.team
        self.player = player
        self.nametag = NameTag(app, player.nick)
        self.countdown = CountDown(app, self.player)
        self._oldName = player.nick
        self._miniMapNameTag = None
        self.coinTally = CoinTally(app, 0)
        self.healthBar = HealthBar(
            app,
            badColour=self.app.theme.colours.badHealth,
            fairColour=self.app.theme.colours.fairHealth,
            goodColour=self.app.theme.colours.goodHealth)
        self.shieldBar = HealthBar(
            app,
            badColour=self.app.theme.colours.badShield,
            fairColour=self.app.theme.colours.fairShield,
            goodColour=self.app.theme.colours.goodShield)

        sprites = app.theme.sprites
        self.sprites = sprites

        self.ghostAnimation = sprites.ghostAnimation(
            worldGUI.getTime, self.player.team)

        self.shieldAnimation = Animation(0.15, timer, *sprites.shieldImages)

        flags = pygame.SRCALPHA
        self.alphaImage = pygame.Surface(self.canvasSize, flags)

        self.image = pygame.Surface(self.canvasSize, flags)
        self.rect = self.image.get_rect()

        # This probably shouldn't be done here.
        _t = datetime.date.today()
        self.is_christmas = _t.day in (24, 25, 26) and _t.month == 12

    @property
    def hookPos(self):
        oldPos, pos = self.player.getGrapplingHookPos()
        fraction = self.worldGUI.tweenFraction
        return (
            fadeValues(oldPos[0], pos[0], fraction),
            fadeValues(oldPos[1], pos[1], fraction),
        )

    def getAngleFacing(self):
        return self.player.angleFacing

    @property
    def angleFacing(self):
        return self.player.angleFacing

    def __getattr__(self, attr):
        '''
        Proxy attributes through to the underlying player class.
        '''
        return getattr(self.player, attr)

    def update(self):
        if self.player.nick != self._oldName:
            self._oldName = self.player.nick
            self.nametag = NameTag(self.app, self.player.nick)
            self._miniMapNameTag = None

        self.setImage()

    def _isSlow(self):
        # Consider horizontal movement of player.
        xMotion = self.player.getXKeyMotion()
        if xMotion < 0:
            return self.player.isFacingRight()
        if xMotion > 0:
            return not self.player.isFacingRight()
        return False

    def setImage(self):
        self.image.fill((127, 127, 127, 0))
        self.image.set_colorkey((127, 127, 127))

        if self.player.dead:
            self.setGhostImage()
        elif not self.player_is_hidden():
            self.drawer.update_from_player(
                self.player, show_phaseshift=self._canSeePhaseShift())
            self.drawer.render_living_player(self.image)

        if self.player.resyncing:
            self.greyOutImage()

    def player_is_hidden(self):
        if not self.player.invisible:
            return False
        if self.worldGUI.gameViewer.replay:
            return False
        target = self.getShownPlayer()
        if target and self.player.isFriendsWith(target):
            return False

        # Player is invisible and we're not on their team
        return True

    def greyOutImage(self):
        grey_colour = (100, 100, 100)
        grey = pygame.Surface(self.image.get_size())
        grey.fill(grey_colour)
        self.image.blit(grey, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        self.image.blit(grey, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def setGhostImage(self):
        blitImages = self.ghostAnimation
        offset = self.ghostOffset

        # Put the pieces together:
        for element in self.ghostAnimation:
            self.image.blit(element.getImage(), (offset, 0))
        if not self.player.isFacingRight():
            self.image = pygame.transform.flip(self.image, True, False)

        respawnRatio = 1 - (
            self.player.timeTillRespawn /
            self.player.world.physics.playerRespawnTotal)
        rect = self.image.get_rect()
        rect.height -= 2
        pt = (int(0.5 + rect.width * respawnRatio), rect.height)
        colours = self.app.theme.colours
        if respawnRatio >= 1:
            pygame.draw.line(
                self.image, colours.ghostBarFull, rect.bottomleft,
                rect.bottomright, 3)
        else:
            pygame.draw.line(
                self.image, colours.ghostBarEmpty, pt,
                rect.bottomright, 3)
            pygame.draw.line(
                self.image, colours.ghostBarFull, pt,
                rect.bottomleft, 1)

        self.setImageAlpha(128)

    def updateLivePlayerImageAlpha(self):
        if self.player.phaseshift and self._canSeePhaseShift():
            # Flicker the sprite between different levels of transparency
            self.setImageAlpha(random.randint(30, 150))
        elif self.player.isInvulnerable():
            self.setImageAlpha(random.randint(30, 150))
        elif self.player.invisible:
            replay = self.worldGUI.gameViewer.replay
            target = self.getShownPlayer()
            if replay or target and self.player.isFriendsWith(target):
                self.setImageAlpha(80)
            else:
                self.setImageAlpha(0)
        else:
            self.setImageAlpha(255)

    def setImageAlpha(self, alpha):
        setAlpha(self.image, alpha, alphaSurface=self.alphaImage)

    def getShownPlayer(self):
        return self.worldGUI.gameViewer.viewManager.target

    def _canSeePhaseShift(self):
        if self.worldGUI.gameViewer.replay:
            return True
        target = self.getShownPlayer()
        if not isinstance(target, Player):
            return False
        return self.player.isFriendsWith(target)

    def renderMiniMapNameTag(self):
        if self._miniMapNameTag:
            return self._miniMapNameTag

        nick = self.player.nick
        if len(nick) <= 3:
            shortName = nick
        else:
            for middleLetter in nick[1:-1]:
                if middleLetter.isupper():
                    break
            shortName = nick[0] + middleLetter + nick[-1]

        font = self.app.screenManager.fonts.miniMapLabelFont
        colours = self.app.theme.colours
        if self.player.dead:
            colour = colours.miniMapGhostColour(self.player.team)
        else:
            colour = colours.miniMapPlayerColour(self.player.team)
        HIGHLIGHT = (192, 192, 192)
        shadow = font.render(self.app, shortName, False, HIGHLIGHT)
        highlight = font.render(self.app, shortName, False, colour)
        x, y = highlight.get_size()
        xOff, yOff = 1, 1
        result = pygame.Surface((x + xOff, y + yOff)).convert()
        result.fill((0, 0, 1))
        result.set_colorkey((0, 0, 1))
        result.blit(shadow, (xOff, yOff))
        result.blit(highlight, (0, 0))
        self._miniMapNameTag = result
        return result


class PlayerAction(Enum):
    STANDING = 0
    WALKING = 1
    RUNNING = 2
    JUMPING = 3
    FALLING = 4
    GRABBING = 5
    GHOST = 6


class PlayerDrawer:
    live_offset = 3
    ghost_offset = 0

    def __init__(
            self, app, timer=time.time,
            action=PlayerAction.STANDING, gun_angle=1.57, bomber_time=None,
            emote=None, grabbed_surface_angle=None,
            grappling_hook_attached=False,
            has_shield=False, has_shoxwave=False, has_machine_gun=False,
            has_ricochet=False, has_ninja=False, has_disruption=False,
            has_elephant=False, flickering=False, translucent=False,
            head=HEAD_CUEBALL, team_colour=(255, 255, 255), resyncing=False,
    ):
        self.app = app
        self.theme = app.theme
        self._alpha_image = None

        self.timer = timer
        self.action = action
        self.gun_angle = gun_angle
        self.bomber_time = bomber_time
        self.emote = emote
        self.grabbed_surface_angle = grabbed_surface_angle
        self.grappling_hook_attached = grappling_hook_attached
        self.has_shield = has_shield
        self.has_shoxwave = has_shoxwave
        self.has_machine_gun = has_machine_gun
        self.has_ricochet = has_ricochet
        self.has_ninja = has_ninja
        self.has_disruption = has_disruption
        self.has_elephant = has_elephant
        self.flickering = flickering
        self.translucent = translucent
        self.head = head
        self.team_colour = team_colour
        self.resyncing = resyncing

        self._animation_start = None
        today = datetime.date.today()
        self._christmas = today.day in (24, 25, 26) and today.month == 12

    @classmethod
    def from_player(cls, app, player, timer=time.time, show_phaseshift=True):
        result = cls(app, timer=timer)
        result.update_from_player(player, show_phaseshift)
        return result

    def update_from_player(self, player, show_phaseshift=True):
        # Consider horizontal movement of player.

        self.gun_angle = player.angleFacing
        self.bomber_time = (
            player.bomber.timeRemaining if player.bomber else None)
        self.emote = player.emote
        self.grabbed_surface_angle = player.grabbedSurfaceAngle
        self.grappling_hook_attached = player.grapplingHook.isAttached()

        if player.dead:
            self.action = PlayerAction.GHOST
        elif player.grabbedSurfaceAngle is not None:
            self.action = PlayerAction.GRABBING
        elif player.getGroundCollision():
            if isNear(player.xVel, 0):
                self.action = PlayerAction.STANDING
            else:
                x_motion = player.getXKeyMotion()
                if x_motion < 0:
                    walking = player.isFacingRight()
                elif x_motion > 0:
                    walking = not player.isFacingRight()
                else:
                    walking = False
                if walking:
                    self.action = PlayerAction.WALKING
                else:
                    self.action = PlayerAction.RUNNING
        elif player.yVel > 0:
            self.action = PlayerAction.FALLING
        else:
            self.action = PlayerAction.JUMPING

        self.has_shield = player.hasVisibleShield()
        self.has_shoxwave = bool(player.shoxwave)
        self.has_machine_gun = bool(player.machineGunner)
        self.has_ricochet = bool(player.hasRicochet)
        self.has_ninja = bool(player.ninja)
        self.has_disruption = bool(player.disruptive)
        self.has_elephant = player.hasElephant()
        self.flickering = (
            (player.phaseshift and show_phaseshift) or player.isInvulnerable())
        self.translucent = player.invisible

        if player.bot:
            self.head = HEAD_BOT
        else:
            self.head = player.head

        if player.team is None:
            self.team_colour = (255, 255, 255)
        else:
            self.team_colour = player.team.colour

        self.resyncing = player.resyncing

    @property
    def facing_right(self):
        return self.gun_angle > 0

    @property
    def has_bomber(self):
        return self.bomber_time is not None

    @property
    def dead(self):
        return self.action == PlayerAction.GHOST

    def render(self, surface):
        surface.fill((127, 127, 127, 0))
        surface.set_colorkey((127, 127, 127))

        if self.dead:
            # TODO: move logic for rendering ghost to this class
            pass
        else:
            self.render_living_player(surface)

        if self.resyncing:
            self.grey_out_image(surface)

    def grey_out_image(self, surface):
        grey_colour = (100, 100, 100)
        grey = pygame.Surface(surface.get_size())
        grey.fill(grey_colour)
        surface.blit(grey, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        surface.blit(grey, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def render_living_player(self, surface):
        show_weapon = True
        regular_arms = True
        animation = False
        head_option = 0
        flipHead = not self.facing_right
        if self.has_bomber:
            self.render_bomber(surface)
            show_weapon = False
            animation = True
        elif self.emote:
            self.render_emote(surface)
            show_weapon = False
            animation = True
        elif self.action == PlayerAction.GRABBING:
            head_option, flipHead = self.render_wall_grabber(surface)
            regular_arms = False
        elif self.grappling_hook_attached:
            self.render_falling(surface)
        elif self.action == PlayerAction.STANDING:
            self.render_stander(surface)
        elif self.action == PlayerAction.WALKING:
            self.render_walker(surface)
            animation = True
        elif self.action == PlayerAction.RUNNING:
            self.render_runner(surface)
            animation = True
        elif self.action == PlayerAction.FALLING:
            self.render_falling(surface)
        else:
            self.render_jumping(surface)

        if not animation:
            self._animation_start = None

        self.render_head(surface, head_option, flipHead)
        if show_weapon:
            self.render_weapon(surface, regular_arms)
        if self.has_shield:
            self.render_shield(surface)

        self.update_live_player_image_alpha(surface)

    def render_bomber(self, surface):
        if self.bomber_time < 0.8:
            self.paste_sprite_sheet_animation(
                surface, 0.08, ((11, 0), (12, 0)), autoflip=True)
        else:
            self.paste_sprite_sheet_animation(
                surface, 0.1, ((9, 0), (9, 0), (10, 0)), autoflip=True)

    def render_emote(self, surface):
        i, j = self.get_weapon_sprite_indices()
        if i is not None:
            dx = -5 if self.facing_right else 5
            self.paste_sprite_sheet(
                surface, i + 14, j, autoflip=True, offset=(dx, -10))
        self.paste_sprite_sheet_animation(
            surface,
            self.emote.frameRate,
            self.emote.spriteIndices,
            autoflip=True)

    def render_wall_grabber(self, surface):
        wall_angle = self.grabbed_surface_angle
        # wall_index: 0 = vertical wall, 7 = horizontal roof
        wall_index = int(
            max(0, min(1, abs(wall_angle * 2 / pi) - 1)) * 7 + 0.5)
        flip = wall_angle > 0 and wall_index != 7

        # gun_angle: 0 = pointing upwards, clockwise to 2*pi = pointing upwards
        gun_angle = self.gun_angle % (2 * pi)
        gun_index = int(gun_angle * 16 / pi + 0.5)
        if self.has_shoxwave:
            if self.facing_right:
                gun_index = 7
            else:
                gun_index = 26
        elif gun_index > 16:
            gun_index += 1

        if 16 <= gun_index <= 17:
            if self.facing_right:
                gun_index = 16
            else:
                gun_index = 17
        # gun_index: 0 = pointing upwards, clockwise to 33 = pointing
        # upwards, with 0 to 16 facing right and 17 to 33 facing left.
        face_right = gun_index <= 16

        # When actually pasting from the spritesheet, the x-index needs to
        # take into account whether the image will then be flipped.
        if flip:
            gun_index = 33 - gun_index
        self.paste_sprite_sheet(surface, gun_index, 1 + wall_index, flip=flip)

        # Calculate which head angle to use
        if 3 <= wall_index <= 6:
            # Angled head
            flip_head = flip
            if face_right ^ flip:
                head_option = 1
            else:
                head_option = 2
        else:
            # Normal head
            head_option = 0
            flip_head = not face_right

        return head_option, flip_head

    def render_stander(self, surface):
        self.paste_sprite_sheet(surface, 0, 0, autoflip=True)

    def render_runner(self, surface):
        self.paste_sprite_sheet_animation(
            surface, 0.1, ((1, 0), (2, 0), (3, 0), (4, 0)), autoflip=True)

    def render_walker(self, surface):
        self.paste_sprite_sheet_animation(
            surface, 0.1, ((5, 0), (6, 0), (7, 0), (8, 0)), autoflip=True)

    def render_falling(self, surface):
        self.paste_sprite_sheet(surface, 3, 0, autoflip=True)

    def render_jumping(self, surface):
        self.paste_sprite_sheet(surface, 3, 0, autoflip=True)

    def get_weapon_sprite_indices(self):
        if self.has_shoxwave:
            return None, None
        if self.has_machine_gun:
            return 0, 10
        if self.has_ricochet:
            return 17, 10
        return 17, 9

    def render_weapon(self, surface, draw_arms):
        if self.has_shoxwave:
            if draw_arms:
                self.paste_sprite_sheet(surface, 7, 9, autoflip=True)
            self.paste_sprite_sheet(surface, 13, 0, autoflip=True)
            return

        x0, y0 = self.get_weapon_sprite_indices()
        angle = (self.gun_angle + pi) % (2 * pi) - pi
        index = int(abs(angle * 16 / pi) + 0.5)

        if draw_arms:
            self.paste_sprite_sheet(surface, index, 9, autoflip=True)
        self.paste_sprite_sheet(surface, x0 + index, y0, autoflip=True)

    def render_head(self, surface, head_option, flip_head):
        santa = self._christmas
        self.paste_head(surface, head_option, flip=flip_head)

        if self.has_ninja:
            santa = False
            self.paste_sprite_sheet(
                surface, 31 + head_option, 0, flip=flip_head)

        if self.has_disruption:
            santa = False
            self.paste_sprite_sheet_animation(surface, 0.2, (
                (16 + head_option, 0), (19 + head_option, 0),
                (22 + head_option, 0)), flip=flip_head)

        if self.has_elephant:
            santa = False
            self.paste_sprite_sheet(
                surface, 28 + head_option, 0, flip=flip_head)

        if santa:
            self.paste_sprite_sheet(
                surface, 25 + head_option, 0, flip=flip_head)

    def render_shield(self, surface):
        self.paste_animation(surface, self.theme.sprites.shieldImages, 0.15)

    def paste_sprite_sheet(
            self, surface, x_index, y_index, *, flip=False, autoflip=False,
            offset=None):
        if autoflip:
            flip = not self.facing_right

        sheet = self.theme.sprites.playerSpriteSheet(flip)
        CELL_WIDTH = 28 * MAP_TO_SCREEN_SCALE
        CELL_HEIGHT = 40 * MAP_TO_SCREEN_SCALE
        if flip:
            x_index = sheet.get_width() // CELL_WIDTH - 1 - x_index

        x = x_index * CELL_WIDTH
        y = y_index * CELL_HEIGHT
        x_dest = (surface.get_width() - CELL_WIDTH) // 2
        y_dest = (surface.get_height() - CELL_HEIGHT) // 2
        if offset:
            x_dest += offset[0]
            y_dest += offset[1]
        area = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)
        surface.blit(sheet, (x_dest, y_dest), area)

    def paste_head(self, surface, head_option, *, flip=False, autoflip=False):
        dx, y_index = HEAD_LOCATIONS[self.head]
        x_index = head_option + dx

        if autoflip:
            flip = not self.facing_right

        sheet = self.theme.sprites.playerHeadSheet(self.team_colour, flip)
        CELL_WIDTH = 28 * MAP_TO_SCREEN_SCALE
        CELL_HEIGHT = 40 * MAP_TO_SCREEN_SCALE
        if flip:
            x_index = sheet.get_width() // CELL_WIDTH - 1 - x_index

        x = x_index * CELL_WIDTH
        y = y_index * CELL_HEIGHT
        x_dest = (surface.get_width() - CELL_WIDTH) // 2
        y_dest = (surface.get_height() - CELL_HEIGHT) // 2
        area = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)
        surface.blit(sheet, (x_dest, y_dest), area)

    def get_animation_elapsed_time(self):
        if self._animation_start is None:
            self._animation_start = self.timer()
            return 0
        return self.timer() - self._animation_start

    def paste_sprite_sheet_animation(
            self, surface, framerate, frame_indices,
            *, autoflip=False, flip=False):
        elapsed = self.get_animation_elapsed_time()

        timeIndex = int(elapsed // framerate) % len(frame_indices)
        x_index, y_index = frame_indices[timeIndex]
        self.paste_sprite_sheet(
            surface, x_index, y_index, autoflip=autoflip, flip=flip)

    def paste_animation(self, surface, images, framerate):
        elapsed = self.get_animation_elapsed_time()

        image = images[int(elapsed // framerate) % len(images)]
        x_dest = (surface.get_width() - image.get_width()) // 2
        y_dest = (surface.get_height() - image.get_height()) // 2
        surface.blit(image, (x_dest, y_dest))

    def update_live_player_image_alpha(self, surface):
        if self.flickering:
            self.set_image_alpha(surface, random.randint(30, 150))
        elif self.translucent:
            self.set_image_alpha(surface, 80)
        else:
            self.set_image_alpha(surface, 255)

    def set_image_alpha(self, surface, alpha):
        if self._alpha_image is None \
                or self._alpha_image.get_size() != surface.get_size():
            self._alpha_image = pygame.Surface(
                surface.get_size(), pygame.SRCALPHA)
        setAlpha(surface, alpha, alphaSurface=self._alpha_image)
