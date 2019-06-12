import logging

log = logging.getLogger(__name__)


class Element(object):
    active = True
    hasFocus = False

    def __init__(self, app, *args, **kwargs):
        super(Element, self).__init__(*args, **kwargs)
        self.app = app

    def processEvent(self, event):
        '''Processes the specified event and returns the event if it should
        be passed on, or None if it has been caught.'''
        return event

    def tick(self, deltaT):
        '''Gives the element a chance to update itself. deltaT is the time
        in seconds since the last tick cycle.'''

    def draw(self, screen):
        '''Gives the element a chance to draw itself onto the screen.'''

    def gotFocus(self):
        pass

    def lostFocus(self):
        pass


class CompoundElement(Element):
    # List of elements in order that they are drawn on screen. That is,
    # the first element in the list is drawn at the bottom.

    def __init__(self, *args, **kwargs):
        super(CompoundElement, self).__init__(*args, **kwargs)
        self.elements = []
        self.active = True

    def processEvent(self, event):
        if not self.active:
            return event

        elements = list(self.elements)
        elements.reverse()
        for element in elements:
            event = element.processEvent(event)

            if event is None or not self.app._running:
                return None
        return event

    def tick(self, deltaT):
        if not self.active:
            return
        try:
            for element in self.elements:
                try:
                    element.tick(deltaT)
                except Exception as e:
                    log.exception('Error in %s.tick', self.__class__.__name__)
        except RuntimeError as e:
            if e.__str__() == 'maximum recursion depth exceeded':
                log.error('ERROR: Infinite loop of elements:')
                if hasattr(element, 'elements'):
                    log.error('%s contains %s' % (element, element.elements))
            raise

    def draw(self, screen):
        if not self.active:
            return
        for element in self.elements:
            try:
                element.draw(screen)
            except Exception as e:
                log.error('%s: %s', self, e, exc_info=True)

    def clearFocus(self):
        self.setFocus(None)

    def setFocus(self, element):
        if element is not None and element not in self.elements:
            return

        if element is not None and element.hasFocus:
            return

        for el in self.elements:
            if el.hasFocus:
                el.hasFocus = False
                el.lostFocus()
        if element is not None:
            element.hasFocus = True
            element.gotFocus()


class TabFriendlyCompoundElement(CompoundElement):
    def __init__(self, app, *args, **kwargs):
        super(TabFriendlyCompoundElement, self).__init__(app, *args, **kwargs)
        self.tabOrder = []

    def tabNext(self, sender):
        assert sender in self.tabOrder
        i = self.tabOrder.index(sender)
        i += 1
        i %= len(self.tabOrder)
        self.setFocus(self.tabOrder[i])


class SwitchingElement(Element):
    def __init__(self, app, elements=None, choice=None, *args, **kwargs):
        super(SwitchingElement, self).__init__(app, *args, **kwargs)
        if elements is None:
            self.elements = {}
        else:
            self.elements = elements

        self.setChoice(choice)

    def setChoice(self, choice):
        if isinstance(choice, Element):
            self.element = choice
        else:
            self.element = self.elements.get(choice, None)

    def processEvent(self, event):
        if not self.element:
            return event
        return self.element.processEvent(event)

    def tick(self, deltaT):
        if self.element:
            self.element.tick(deltaT)

    def draw(self, screen):
        if self.element:
            self.element.draw(screen)
