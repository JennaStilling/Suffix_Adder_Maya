# basicSuffixEditorTool
# Version: 2.1.0
# Author: @jennastilling

# TODO
# Add drop down menu functionality for:
#   constraints -- <x>Contraint

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
    cmds.window(windowID, title=pWindowTitle, sizeable = False, resizeToFitChildren = True, widthHeight=(200, 300))
    
    # sets ui layout
    cmds.rowLayout(numberOfColumns=2)
    cmds.columnLayout(adjustableColumn=True, columnAlign="left", rowSpacing=5)

    # suffix section of panel
    cmds.text(label = "Suffix")
    
    suffixField = cmds.textField(text = "_")

    cmds.separator (h=10, style = "none")

    # radio buttons to search by heirarchy or selected objects
    radioGroup = cmds.radioCollection()
    cmds.text(label = "Selection Type: ")  
    cmds.radioButton(label= "By heirarchy", sl = True, align = "left") # default radio button object
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

    # creating the drop down menu
    menuGroup = cmds.optionMenu(label='Specific Type', changeCommand=setSelectedType)
    cmds.menuItem(label='None')
    cmds.menuItem(label='Joints')
    cmds.menuItem(label='Controllers')
    cmds.menuItem(label='Groups')
    cmds.menuItem(label='Locators')
    # cmds.menuItem(label='Constraints')
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
    selectedValue = cmds.optionMenu(dropMenu, q = True, value = True) # grabs selected option information and queries the name
    if selectedValue == "Joints":
            typeSelected = "joint"
    elif selectedValue == "Controllers":
            typeSelected = "nurbsCurve"
    elif selectedValue == "Groups":
            typeSelected = "transform"
    elif selectedValue == "Locators":
            typeSelected = "locator"
    # elif selectedValue == "Constraints":
    #         typeSelected = "constraint"
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
        newName = parseOutHierarchySymbol(objectName) + suffix
        cmds.select(objectName)
        cmds.rename(newName)

# Purpose:      creates a filtered list of objects in the selection or heirarchy based on if they match the type the user selected - determines 
#               location in master list of objects in scene containting detailed node information by calculating a location offset determined by previous testing
# Parameters:   typeSelected    object type user selected
#               objectList      list of objects user selected
#               masterList      list of all objects in the scene with detailed node information following the name - used to determine offset
# Returns:      list of objects in selection / heirarchy based on condition above
def getFilteredObjects(masterList, objectList, typeSelected):
    filteredObjects = [] # list of objects that match the selected type
    A = ["locator", "nurbsCurve"] # object types that have a different offset than the others (+1 vs. +3)
    # print(f"Searching for {typeSelected}")

    # for i in masterList:
    #     print(i)
    # print()
    # print(f"Length of filtered list: {len(objectList)}")
    # print(f"Length of master list: {len(masterList)}")

    # loops through objects user selected and were previously filtered by basic type (i.e. transform) - will check for specific types (i.e. nurbsCurve) and append them if they match parameter
    for o in objectList:
        # print(f"Searching for: {o}")
        loc = masterList.index(o) # index in master list of object name
        # print(f"Location: {loc}")

        # calculating offset of specific object type in master list
        if "Shape" not in o: # for some reason, nurbsCurves brought in two separate nodes despite filtering by object name, so determining if the shape node is currently being tested - if so, ignore it
            if typeSelected in A: # index should be offset by 3
                if loc + 3 >= len(masterList): # on the rare case a group object is the end of the list, it only has a transform node after it, so the offset is only 1 instead of 3
                     loc = loc+1
                else:
                    loc = loc + 3
            else:
                loc = loc + 1

            objectType = masterList[loc] # grabs the specific type of the checked object 

            # print(f"Object type found: {objectType}, for object {o}")
            if objectType == typeSelected: # if the two types match, append the object name to the filtered list
                    filteredObjects.append(o)

    return filteredObjects

# Purpose:      determines if the parent object of a heirarchy is of the same type as the user selected
# Parameters:   typeSelected    object type user selected
#               objectList      list of objects user selected
#               primaryObject   parent object of heirarchy
# Returns:      true or false depending on condition above
def determineIfPrimaryIsOfType(masterList, primaryObject, typeSelected):
    isOfType = False # boolean to keep track of if the object if of the type the user selected
    A = ["locator", "nurbsCurve"] # object types that have a different offset than the others (+1 vs. +3)

    # print(f"Primary object: {primaryObject}")
    # for i in masterList:
    #     print(i)

    loc = masterList.index(primaryObject[0]) # index in master list of parent object

    # calculating offset of specific object type in master list
    if typeSelected in A: # index should be offset by 3
        if loc + 3 >= len(masterList): # on the rare case a group object is the end of the list, it only has a transform node after it, so the offset is only 1 instead of 3
            loc = loc+1
        else:
            loc = loc + 3
    else:
        loc = loc + 1

    objectType = masterList[loc] # grabs the specific type of the checked object 

    if objectType == typeSelected: # if the two types match, then parent object should have suffix added
         isOfType = True

    return isOfType

# Purpose:      determines if the parent object of a heirarchy is of the same type as the user selected
# Parameters:   typeSelected    object type user selected
#               objectList      list of objects user selected
#               primaryObject   parent object of heirarchy
# Returns:      true or false depending on condition above
def parseOutHierarchySymbol(filteredList):
    newName = ""
    print(filteredList)

# find (character, [optional index])
    if '|' in filteredList:
        loc = filteredList.find('|')
        print(f"| found at position {loc}")
        if loc != -1:
            filteredList = filteredList[loc+1:]
        while loc != -1:
            loc = filteredList.find('|')
            if loc != -1:
                filteredList = filteredList[loc+1:]
    newName = filteredList

    return newName

# Purpose:      determines if the parent object of a heirarchy is of the same type as the user selected
# Parameters:   typeSelected    object type user selected
#               objectList      list of objects user selected
#               primaryObject   parent object of heirarchy
# Returns:      true or false depending on condition above
def removeBeginningLine(filteredList):
    newList = []
    for i in filteredList:
          #i = i[1:]
          print(i)
          newList.append(i)
    return newList

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
    filteredList = []
    # contraints = ["parentConstraint", "pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "poleVectorConstraint"]
    
    #if user wants to select by heirarchy
    if selectedRadio == "By heirarchy":
        # grabs a list of objects selected
        if typeSelected != "None":
            objectList = cmds.listRelatives(allDescendents = True, path = True)
            objectList = removeBeginningLine(objectList)
            filteredList = getFilteredObjects(masterList, objectList, typeSelected)
        else:
            filteredList = cmds.listRelatives(allDescendents = True, path = True)
            filteredList = removeBeginningLine(filteredList)

        if len(filteredList) > 0:
            # loops through list and adds the suffix to the object's name
            renameObjects(suffix, filteredList)

        # grabs the first parent selected and adds the suffix to the object's name
        objectName = cmds.listRelatives(parent = True)
        if (determineIfPrimaryIsOfType(masterList, objectName, typeSelected)):
            #objectName = cmds.listRelatives(parent = True)
            newName = objectName[0] + suffix
            cmds.select(objectName[0])
            cmds.rename(newName)
        
    #if user wants to select by selection
    else: 
        if typeSelected != "None":
            # if typeSelected == "constraint":
            #      objectList = []
            #      for k in contraints:
            #         objectList.append(cmds.ls(orderedSelection = True, type = k))
            #         print(f"Type: {k}")
            #         if objectList:
            #             filteredList.append(getFilteredObjects(masterList, objectList, k))
            # else:
            print(typeSelected)
            if typeSelected == "nurbsCurve" or typeSelected == "locator":
                 objectList = cmds.ls(orderedSelection = True, type = "transform")
            else:
                objectList = cmds.ls(orderedSelection = True, type = typeSelected)
            filteredList = getFilteredObjects(masterList, objectList, typeSelected)
        else:
             filteredList = cmds.ls(orderedSelection = True)
        
        if len(filteredList) > 0:
            # loops through list and adds the suffix to the object's name
            renameObjects(suffix, filteredList)
    
    # closes window
    # if cmds.window(windowID, exists = True):
    #     cmds.deleteUI(windowID)
    
# start - creates window 
createUI("Suffix Editor", applyCallback)