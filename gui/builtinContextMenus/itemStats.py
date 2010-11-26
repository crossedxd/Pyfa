from gui.contextMenu import ContextMenu
from gui.itemStats import ItemStatsDialog
import gui.mainFrame
import service
import wx

class ItemStats(ContextMenu):
    def __init__(self):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

    def display(self, context, selection):
        return context in ("item", "ship", "module", "ammo", "skill",
                           "itemSearch", "drone", "implant", "booster",
                           "projectedModule", "projectedDrone", "projectedAmmo")

    def getText(self, context, selection):
        return "%s stats" % (context.capitalize() if context not in self.REPLACES else self.REPLACES[context])

    REPLACES = {"itemSearch": "Item",
                "projectedModule": "Module",
                "projectedDrone": "Drone",
                "projectedAmmo": "Ammo"}

    def activate(self, context, selection, i):
        if context == "ship":
            fitID = self.mainFrame.getActiveFit()
            cFit = service.Fit.getInstance()
            stuff = cFit.getFit(fitID).ship
        else:
            stuff = selection[0]

        if context == "module" and stuff.isEmpty:
            return

        mstate = wx.GetMouseState()
        reuse = False

        if mstate.ControlDown() or mstate.CmdDown():
            reuse = True

        if self.mainFrame.GetActiveStatsWindow() == None and reuse:
            dlg=ItemStatsDialog(stuff, context.capitalize() if context not in self.REPLACES else self.REPLACES[context])

        elif reuse:
            lastWnd = self.mainFrame.GetActiveStatsWindow()
            pos = lastWnd.GetPosition()
            dlg=ItemStatsDialog(stuff, context.capitalize() if context not in self.REPLACES else self.REPLACES[context], pos)
            lastWnd.closeEvent(None)

        else:
            dlg=ItemStatsDialog(stuff, context.capitalize() if context not in self.REPLACES else self.REPLACES[context])

ItemStats.register()
