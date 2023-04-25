# basicSuffixEditorTool
# Version: 2.0.0
# Author: @jennastilling

# TODO
# Fix filtering system

import maya.cmds as cmds
from functools import partial

class TypeSelected:
    # constructor
    def __init__(self, type):
         self.type = type
      
    # mutator
    def setType(self, type):
        self.type = type
      
    # accessor
    def getType(self):
        return self.type

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
    cmds.window(windowID, title=pWindowTitle, sizeable = False, resizeToFitChildren = True, widthHeight=(400, 300))
    
    # sets ui layout
    cmds.rowLayout(numberOfColumns=2)
    cmds.columnLayout(adjustableColumn=True, columnAlign="left", rowSpacing=5)

    # suffix section of panel
    cmds.text(label = "Suffix")
    
    suffixField = cmds.textField(text = "_")

    cmds.separator (h=10, style = "none")

    # search by heirarchy or selected objects
    radioGroup = cmds.radioCollection()
    cmds.text(label = "Selection Type: ")  
    cmds.radioButton(label= "By heirarchy", sl = True, align = "left")
    cmds.radioButton(label='By selection', align = "right")

    cmds.separator (h=10, style = "none")

    # filter out a specific type
    typeSelected = TypeSelected("joint")

    # Purpose:      changes selected type to what user selects from drop menu
    # Parameters:   selected drop menu item
    # Returns:      n/a
    def setSelectedType(item):
            if item == "Joints":
                 typeSelected.setType("joint")
            elif item == "Controllers":
                 typeSelected.setType("transform")
            else:
                 typeSelected.setType("none")

    menuGroup = cmds.optionMenu(label='Specific Type', changeCommand=setSelectedType)
    cmds.menuItem(label='None')
    cmds.menuItem(label='Joints')
    cmds.menuItem(label='Controllers')
    cmds.menuItem(label='Groups')
    cmds.menuItem(label='Locators')
    cmds.menuItem(label='Constraints')
    cmds.menuItem(label = "I/K Handles")

    cmds.separator (h=10, style = "none")
    # button to execute the method
    cmds.button(label = "Apply", command = partial(pApplyCallback, suffixField, windowID, radioGroup, menuGroup))
    
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
 
# Purpose:      gets the name of the selected radio button
# Parameters:   radioGroup      radio button collection to query
# Returns:      selectedValue   selected radio button
def getRadioSelection(radioGroup):
    radioCollection = cmds.radioCollection(radioGroup, q = True, sl = True)
    selectedValue = cmds.radioButton(radioCollection, q = True, label = True)
    return selectedValue

# Purpose:      gets the name of the selected drop menu item
# Parameters:   radioGroup      drop menu to query
# Returns:      selectedValue   selected menu item
def getDropMenuSelection(dropMenu):
    selectedValue = cmds.optionMenu(dropMenu, q = True, value = True)
    if selectedValue == "Joints":
            typeSelected = "joint"
    elif selectedValue == "Controllers":
            typeSelected = "nurbsCurve"
    elif selectedValue == "Groups":
            typeSelected = "transform"
    elif selectedValue == "Locators":
            typeSelected = "locator"
    elif selectedValue == "Constraints":
            typeSelected = "constraint"
    elif selectedValue == "I/K Handles":
            typeSelected = "ikHandle"
    else:
            typeSelected = "None"
    return typeSelected

# Purpose:      appends a suffix onto given items
# Parameters:   suffix      suffix to append
#               objectList  list of objects to append suffix to
# Returns:      n/a
def renameObjects(suffix, objectList):
    for objectName in objectList:
        newName = objectName + suffix
        cmds.select(objectName)
        cmds.rename(newName)

# Purpose:      appends a suffix onto given items
# Parameters:   suffix      suffix to append
#               objectList  list of objects to append suffix to
# Returns:      n/a
def getFilteredObjects(masterList, objectList, typeSelected):
     filteredObjects = []
     A = ["locator", "nurbsCurve"]

     for i in objectList:
          print(i)
     for o in objectList:
        print(o)
        loc = masterList.index(o)
        print(masterList[loc])

        if typeSelected in A:
             loc = loc + 3
        else:
             loc = loc + 1

        objectType = masterList[loc]

        if objectType == typeSelected:
             filteredObjects.append(o)

     return filteredObjects

# Purpose:      cancels the suffix method without executing and closes the screen
# Parameters:   pSuffixField        text field containing desired suffix
#               windowID            id of current window open
#               heirarchySelection  if user wants to select by heirarchy
#               selectedSelection   if user wants to mass select or select specific objects
#               typeSelected        type of objects to filter out if user desires
# Returns:      n/a
def applyCallback(suffixField, windowID, radioGroup, menuGroup, *pArgs):
    typeSelected = getDropMenuSelection(menuGroup)
    selectedRadio = getRadioSelection(radioGroup)
    suffix = cmds.textField(suffixField, query = True, text = True)
    masterList = cmds.ls(st = True)
    for i in masterList:
         print(i)
    filteredList = []
    contraints = ["parentConstraint", "pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "poleVectorConstraint"]
    
    #if user wants to select by heirarchy
    if selectedRadio == "By heirarchy":
        # grabs a list of objects selected
        if typeSelected != "None":
            objectList = cmds.listRelatives(allDescendents = True)
            filteredList = getFilteredObjects(masterList, objectList, typeSelected)
        else:
             filteredList = cmds.listRelatives(allDescendents = True)

        if len(filteredList) > 0:
            # loops through list and adds the suffix to the object's name
            renameObjects(suffix, filteredList)

        # grabs the first parent selected and adds the suffix to the object's name
        objectName = cmds.listRelatives(parent = True)
        newName = objectName[0] + suffix
        cmds.select(objectName[0])
        cmds.rename(newName)
        
    #if user wants to select by selection
    else: 
        if typeSelected != "None":
            if typeSelected == "constraint":
                 objectList = []
                 for k in contraints:
                    objectList.append(cmds.ls(orderedSelection = True, type = k))
                    print(f"Type: {k}")
                    if objectList:
                        filteredList.append(getFilteredObjects(masterList, objectList, k))
            else:
                objectList = cmds.ls(orderedSelection = True, type = typeSelected)
                filteredList = getFilteredObjects(masterList, objectList, typeSelected)
        else:
             filteredList = cmds.ls(orderedSelection = True)
        
        if len(filteredList) > 0:
            # loops through list and adds the suffix to the object's name
            renameObjects(suffix, filteredList)
    
    # closes window
    if cmds.window(windowID, exists = True):
        cmds.deleteUI(windowID)
    
# start - creates window 
createUI("Suffix Editor", applyCallback)