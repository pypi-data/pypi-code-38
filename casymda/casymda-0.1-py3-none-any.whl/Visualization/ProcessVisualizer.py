from tkinter import Canvas, Tk, Toplevel
import datetime
import time
import os
from PIL import Image, ImageTk
from casymda.CoreBlocks.CoreComponent import CoreComponentVisualizer, States


# this class enables the simple 2D animation of component contents and entity flows
# works with CoreComponents and CoreEntities
# basic components: canvas, text and icons (PhotoImages, created and moved on the canvas)
# TODO: mac os x compatibility (.png transparency issue)

class ProcessVisualizer(CoreComponentVisualizer):
    def __init__(self, flowSpeed=200, master=None, BGPhotoFile='sampleModels/bpmn/core-example.jpg', title="Core Example", defaultEntityIconPath=""):
        if master is None:
            self.gui = Tk()
        else:
            self.gui = Toplevel(master=master)

        self.BGphoto = ImageTk.PhotoImage(Image.open(BGPhotoFile))

        self.guiWidth = self.BGphoto.width()
        self.guiHeight = self.BGphoto.height()

        self.gui.geometry(str(self.guiWidth) + "x" + str(self.guiHeight))
        self.gui.title(title)

        self.canvas = Canvas(self.gui, width=self.guiWidth,
                             height=self.guiHeight, bg='black', )
        self.canvas.pack(side='left')

        self.img = self.canvas.create_image(
            0, 0, image=self.BGphoto, anchor='nw')
        timeText = "Time:  " + str(0)
        self.timeLabel = self.canvas.create_text(self.guiWidth - 5, self.guiHeight - 5, font="Helvetica 10", fill='black',
                                                 anchor='se', text=timeText)

        self.componentAnims = []
        self.entityAnims = []

        self.flowSpeed = flowSpeed  # speed of entity movement in pixels per second
        self.defaultEntityIconPath = defaultEntityIconPath

        self.state_icon_paths = self.get_state_icon_paths()

        self.gui.update_idletasks()

    def animateComponent(self, component, queuing=True, direction=-20):
        # creates new or updates existing animation
        componentAnim = self.find_or_create_component_anim(component)

        # update component's text
        if len(component.entities) > 5:  # don't provide too much details
            contentListString = "Amount:  " + str(len(component.entities))
        else:
            contentListString = "\n".join([" - ".join([entity.name, str(datetime.timedelta(
                seconds=int(entity.timeOfArrival)))]) for entity in component.entities])
        self.canvas.itemconfig(componentAnim.contentList,
                               text=contentListString)

        self.updateTimeLabel(component.env.now)

        # update entity animations as well if they should queue
        if queuing:
            x, y = component.xy
            q_offset_x = 0
            for entity in component.entities:
                self.animateFlowXY(x, y, x + q_offset_x, y,
                                   entity, skipFlow=True)
                q_offset_x += direction

    def animateFlow(self, fromComp, toComp, entity, skipFlow=False, ways=None):
        # animates entity movements between components

        self.updateTimeLabel(fromComp.env.now)

        if toComp is None:
            self.destroyEntityAnim(entity)  # sink
            return

        fx, fy = fromComp.xy
        tx, ty = toComp.xy

        # if waypoints exist, animate flow between waypoints first and update fx, fy
        if ways is not None and toComp.name in ways:
            for way in fromComp.ways[toComp.name]:
                self.animateFlowXY(fx, fy, *way, entity, skipFlow=skipFlow)
                fx, fy = way

        self.animateFlowXY(fx, fy, tx, ty, entity, skipFlow=skipFlow)

    def animateFlowXY(self, fx, fy, tx, ty, entity, skipFlow):
        # flow animation

        # find / create entity animation
        entityAnim = next(
            (x for x in self.entityAnims if x.entity is entity), None)  # existing
        if entityAnim is None:
            entityAnim = self.createEntityAnim(entity, (fx, fy))  # new
        entityIcon = entityAnim.icon

        # make sure starting position is as expected
        self.canvas.coords(entityIcon, fx, fy)
        self.moveIcon(fx, fy, tx, ty, entityIcon,
                      self.flowSpeed, skipFlow=skipFlow)

        entityAnim.xy = (tx, ty)  # update known position

    def moveIcon(self, fx, fy, tx, ty, icon, flowSpeed, skipFlow):
        # only animate flow if not skipped
        if skipFlow:
            self.canvas.move(icon, (tx - fx), (ty - fy))
            self.gui.update_idletasks()
            return

        d = ((tx - fx)**2 + (ty - fy)**2)**0.5
        if d == 0:
            return  # target already reached

        t = d / float(flowSpeed)  # wallclock time needed for distance
        fps = 30  # aninmations per second
        # x-distance / number of animations = distance per move
        perMoveX = (tx - fx) / (t * fps)
        perMoveY = (ty - fy) / (t * fps)  # y
        remainingX = tx - fx
        remainingY = ty - fy
        # animation loop
        while (abs(remainingX) + abs(remainingY)) > 0:
            # do not move further than necessary
            x_move = remainingX if abs(
                remainingX) < abs(perMoveX) else perMoveX
            y_move = remainingY if abs(
                remainingY) < abs(perMoveY) else perMoveY

            remainingX -= x_move
            remainingY -= y_move

            self.canvas.move(icon, x_move, y_move)
            self.gui.update_idletasks()
            time.sleep(1 / float(fps))  # sleep until next frame

    def updateTimeLabel(self, now):
        textString = "Time:  " + str(datetime.timedelta(seconds=int(now)))
        self.canvas.itemconfig(self.timeLabel, text=textString)
        self.gui.update_idletasks()

    def createEntityAnim(self, entity, xy):
        x, y = xy

        try:
            filePath = entity.processVisualizerAnimPath
        except AttributeError:
            filePath = self.defaultEntityIconPath

        # TODO: solve transparency issue -> mac: either not displayed or just a black square (when converting to RGB)
        photo = ImageTk.PhotoImage(Image.open(filePath).convert("RGBA"))

        icon = self.canvas.create_image(x, y, image=photo, anchor='c')
        self.gui.update_idletasks()

        entityAnim = EntityAnim(entity, icon, photo, xy)
        self.entityAnims.append(entityAnim)

        return entityAnim

    def destroyEntityAnim(self, entity):
        entityAnim = next(
            (x for x in self.entityAnims if x.entity is entity), None)  # existing
        if entityAnim is not None:
            self.entityAnims.remove(entityAnim)
            entityAnim = None
            self.gui.update_idletasks()

    def createComponentAnim(self, component):
        # currently only consists of updated list of entities
        if component.xyContentList is None:
            # default contents list's position to slightly below the center
            xC, yC = component.xy
            xC -= 20
            yC += 10
        else:
            xC, yC = component.xyContentList

        contentList = self.canvas.create_text(xC, yC, font="Helvetica 10", fill='black',
                                              anchor='nw', text="contents:\n-")

        componentAnim = ComponentAnim(component, contentList)
        self.componentAnims.append(componentAnim)
        return componentAnim

    def find_or_create_component_anim(self, component):
        # creates new or updates existing animation
        componentAnim = next(
            (x for x in self.componentAnims if x.component is component), None)  # existing
        if componentAnim is None:
            componentAnim = self.createComponentAnim(component)  # new
        return componentAnim

    def change_component_state(self, component, state, is_active):

        component_anim = self.find_or_create_component_anim(component)
        if is_active is True:
            state_icon = State_Icon(
                state.value, component.xy, self.state_icon_paths[state.value], self.canvas)
            component_anim.state_icons[state.value] = state_icon
        else:
            if component_anim.state_icons[state.value] is not None:
                self.canvas.delete(
                    component_anim.state_icons[state.value].icon)
                component_anim.state_icons[state.value] = None
        self.gui.update_idletasks()

    def get_state_icon_paths(self):
        path = os.path.dirname(os.path.realpath(__file__))
        state_icon_paths = {
            enum_state.value: path + "/state_icons/" + enum_state.value + ".png" for enum_state in States
        }
        return state_icon_paths


class State_Icon():

    OFFSETS = {
        States.busy.value: (38, -25),
        States.empty.value: (38, -25),
        States.blocked.value: (38, 0)
    }

    def __init__(self, state_value, xy, path_to_icon, canvas):
        self.state_value = state_value
        self.xy = map(sum, zip(xy, self.OFFSETS[state_value]))
        self.photo = ImageTk.PhotoImage(
            Image.open(path_to_icon).convert("RGBA"))
        self.icon = canvas.create_image(
            *self.xy, image=self.photo, anchor='c')


class EntityAnim():
    def __init__(self, entity, icon, photo, xy):
        self.entity = entity
        self.icon = icon
        self.photo = photo
        self.xy = xy


class ComponentAnim():
    def __init__(self, component, contentList, icon=None, text=None):
        self.component = component
        self.contentList = contentList
        self.icon = icon
        self.text = text
        self.state_icons = {state.value: None for state in States}
