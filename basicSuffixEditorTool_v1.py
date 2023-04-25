# basicSuffixEditorTool
# Version: 1.0.0
# Author: @jennastilling

import maya.cmds as cmds
import functools

# Purpose:      creates the UI window that appears on screen
# Parameters:   pWindowTitle    title of frame that appears
#               pApplyCallback  function name that applies the suffix to the object names (will be tied to a button generated in this method)
# Returns:      n/a
def createUI(pWindowTitle, pApplyCallback):
    windowID = "myWindowID"
    
    # if another window with the same id as above is open, close it
    if cmds.window(windowID, exists = True):
        cmds.deleteUI(windowID)
        
    # creates the frame that hold the ui information on screen
    cmds.window(windowID, title=pWindowTitle, sizeable = False, resizeToFitChildren = True)
    
    # sets the column layout of panel
    cmds.rowColumnLayout(numberOfColumns = 3, columnWidth = [(1,75), (2,60), (3, 60)], columnOffset = [(1, "right", 3)])

    # suffix section of panel
    cmds.text(label = "Suffix")
    
    pSuffixField = cmds.textField(text = "")
    
    # adds space
    cmds.separator (h=10, style = "none")
    cmds.separator (h=10, style = "none")

    # button to execute the method
    cmds.button(label = "Apply", command = functools.partial(pApplyCallback, pSuffixField, windowID))
    
    # Purpose:      cancels the suffix method without executing and closes the screen
    # Parameters:   n/a
    # Returns:      n/a
    def cancelCallback(*pArgs):
        if cmds.window(windowID, exists = True):
            cmds.deleteUI(windowID)
    
    # button to cancel and close window
    cmds.button(label = "Cancel", command = cancelCallback)
    
    # display frame and panel
    cmds.showWindow()
 
def applyCallback(pSuffixField, windowID, *pArgs):
    suffix = cmds.textField(pSuffixField, query = True, text = True)
    
    # grabs a list of objects selected
    objectList = cmds.listRelatives(allDescendents = True)
    
    # loops through list and adds the suffix to the object's name
    for objectName in objectList:
        newName = objectName + suffix
        cmds.select(objectName)
        cmds.rename(newName)

    # grabs the first parent selected and adds the suffix to the object's name
    objectName = cmds.listRelatives(parent = True)
    newName = objectName[0] + suffix
    cmds.select(objectName[0])
    cmds.rename(newName)
    
    # closes window
    if cmds.window(windowID, exists = True):
        cmds.deleteUI(windowID)
    
# start - creates window 
createUI("Suffix Editor", applyCallback)