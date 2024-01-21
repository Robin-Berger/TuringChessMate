from colors import *

""""
 EvtObj handles standard events.
    Buttons
    Drag/drop objects
    ...

"""
class EvtObj:
    def __init__(self, has_select=False, has_dragging=False):
        #all features are turned off by default, but adding them is just adding parameters
        self.has_select = has_select
        self.has_dragging = has_dragging

        # Keep track of mouse activity, object dragging, button mechanics
        self.isWithin = False
        self.isPressed = False
        self.isDragged = False

        # Default colors for highlighting objects
        self.cPressed = (0, 255, 255)
        self.cNormal = (255, 255, 0)
        self.cDragged = LTGREY

        #TODO: implement modifiers (_left/_right may be ditched later)
        self.mod_shift = False
        self.mod_shift_left = False
        self.mod_shift_right = False
        self.mod_ctrl = False
        self.mod_ctrl_left = False
        self.mod_ctrl_right = False
        self.mod_alt = False

    # checks if click was within object. Needs override
    def isMouseWithin(self, mouse_x, mouse_y):
        return False

    def MOUSEWHEEL(self, _wheel):
        pass
    def MOUSEBUTTONDOWN(self, mouse_x, mouse_y):
        pass
    def MOUSEBUTTONUP(self, mouse_x, mouse_y):
        pass
    def MOUSEMOTION(self, mouse_x, mouse_y):
        pass

    def action_hovering(self):
        pass
    def action_dragging(self):
        pass
    def action_dropped(self):
        pass
    def action_clicked(self):
        pass
