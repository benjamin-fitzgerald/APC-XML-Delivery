import xml.etree.ElementTree as ET
import arcpy
import os
import sys
import datetime
from collections import defaultdict
from random import randint
import time
import traceback
import pandas as pd
import requests, json


def GenerateXML(fileName):
    NS_XSI = "{http://www.w3.org/2001/XMLSchema-instance}"

    root = ET.Element('WorkSet')
    root.set(NS_XSI + "noNamespaceSchemaLocation", "WorkSet.xsd")

    ApplicationVersion = ET.Element("ApplicationVersion")
    root.append(ApplicationVersion)
    ApplicationVersion.text = '1'

    NumWorkItems = ET.Element("NumWorkItems")
    root.append(NumWorkItems)
    NumWorkItems.text = '0'

    Objects = ET.Element('Objects')
    root.append(Objects)

    # Get these .text  values from SDE
    PriorWorkSetFlag = ET.Element("PriorWorkSetFlag")
    root.append(PriorWorkSetFlag)
    PriorWorkSetFlag.text = '0'

    StateAbbrv = ET.Element("StateAbbrv")
    root.append(StateAbbrv)
    StateAbbrv.text = 'UT'

    UsageType = ET.Element("UsageType")
    root.append(UsageType)
    UsageType.text = 'PPLD'

    WorkAreaID = ET.Element("WorkAreaID")
    root.append(WorkAreaID)
    WorkAreaID.text = '0'

    WorkMap = ET.Element("WorkMap")
    root.append(WorkMap)
    WorkMap.text = '0'

    WorkMapSection = ET.Element("WorkMapSection")
    root.append(WorkMapSection)
    WorkMapSection.text = '0'

    WorkSetID = ET.Element("WorkSetID")
    root.append(WorkSetID)
    WorkSetID.text = '0'

    WorkSetCategory = ET.Element("WorkSetCategory")
    root.append(WorkSetCategory)
    WorkSetCategory.text = '0'

    WorkSource = ET.Element("WorkSource")
    root.append(WorkSource)
    WorkSource.text = 'FPI'

    XSDVersion = ET.Element("XSDVersion")
    root.append(XSDVersion)
    XSDVersion.text = '1'

    XMLDataVersion = ET.Element("XMLDataVersion")
    root.append(XMLDataVersion)
    XMLDataVersion.text = '1'



    tree = ET.ElementTree(root)
    tree.write(fileName)


# Driver Code
if __name__ == "__main__":
    database = arcpy.GetParameterAsText(0)
    WorksetIDnumber = arcpy.GetParameterAsText(1)
    Type = arcpy.GetParameterAsText(2)
    OutputFolder = arcpy.GetParameterAsText(3)
    FailedPoints = arcpy.GetParameterAsText(4)

    WorksetIds = []
    WorksetIDnumber = WorksetIDnumber.replace("  ", " ")
    WorksetIDnumber = WorksetIDnumber.replace(", ", ",")

    WorksetIds = WorksetIDnumber.split(",")

    for WorksetID in WorksetIds:
        FailedPointsList = []
        if FailedPoints:
            FailedPoints = FailedPoints.replace("  ", " ")
            FailedPoints = FailedPoints.replace(", ", ",")

            FailedPointsList = FailedPoints.split(",")

        worksequence = 1

        now = datetime.datetime.now()
        now_formatted = now.strftime('%Y%m%d%H%M%S')
        # tree.write(r'C:\Pacificorp\from_pacificorp\fpi_a_data_{0}_{1}.xml'.format('test','test'))
        name = os.path.join(OutputFolder, 'fpi_a_data_{0}_{1}.xml'.format(str(WorksetID), now_formatted))
        # xmlFull = os.path.join(OutputFolder, name)
        GenerateXML(name)
        tree = ET.parse(name)

        root = tree.getroot()
        if str(Type) == 'VA':
            Pole = os.path.join(database, 'IR_PAVCA_25.DBO.INSPECTIONPOLE_VA')
            PhotoTable = os.path.join(database, 'IR_PAVCA_25.DBO.InspectionPole_VAPhotoTracking')
        elif str(Type) == 'DTLSB':
            Pole = os.path.join(database, 'IR_PAVCA_25.DBO.INSPECTIONPOLE_DTLSB')
            PhotoTable = os.path.join(database, 'IR_PAVCA_25.DBO.InspectionPole_DTLSBPhotoTracking')
        else:
            arcpy.AddMessage('Type needs to be VA or DTLSB')
            sys.exit()

        ConditionTable = os.path.join(database, 'IR_PAVCA_25.DBO.ConditionTable')
        # TreatmentTable = os.path.join(database, 'IR_PAVCA_25.DBO.TreatmentTable')
        ConditionRemarks = os.path.join(database, 'IR_PAVCA_25.DBO.ConditionRemarks')

        ConditionPhotoTable = os.path.join(database, 'IR_PAVCA_25.DBO.ConditionTablePhotoTracking')
        # ElevationPole = os.path.join(database, 'IR_PAVCA_25.DBO.ElevationPole')
        persontable = os.path.join(database, 'IR_PAVCA_25.DBO.UserList')
        sourceConditionPhotoTable = os.path.join(database, 'IR_PAVCA_25.DBO.SourceConditionTablePhotoTracking')
        sourceCondition = os.path.join(database, 'IR_PAVCA_25.DBO.SourceConditionTable')

        facility_point_id = 'Facilty_Point_ID'
        Height = 'Height'
        Birthdate = 'Birthdate'
        Birthdate_Estimated = 'Birthdate_Estimated'
        Pole_Manufacturer = 'Pole_Manufacturer'
        Class = 'Class'
        Stubbing_Code = 'Stubbing_Code'
        Pole_Material = 'Material'
        Manufacturer_Treatment_Code = 'Manufacturer_Treatment_Code'
        PoleTop_Cond_Code = 'PoleTop_Condition'
        GrdLine_Cond_Code = 'GrdLine_Condition'
        Decay_Location = 'Decay_Location'
        Condition = 'Condition'
        Status_Remark = 'Status_Remark'
        Structure_Type = 'Structure_Type'
        pole_id = 'PoleID'
        Inspection_ID = 'Inspection_ID'
        inspection_set_id = 'inspection_set_id'
        Circuit_ID = 'Circuit_ID'
        Multiple_Circuit_ID = 'Multiple_Circuit_ID'
        ESRI_LATITUDE = 'ESRIGNSS_LATITUDE'
        ESRI_LONGITUDE = 'ESRIGNSS_LONGITUDE'
        Treatment = 'Treatment'

        facility_point_id_list = []
        worktaskID_list = []
        resultid_List = []
        for object in root.iter('Object'):
            for child in object.getchildren():
                if child.tag == 'WorkResults':
                    for workresult in child:
                        for taskname in workresult:
                            if taskname.tag == 'WorkTaskID':
                                worktaskID_list.append(int(taskname.text))
                            if taskname.tag == 'ResultID':
                                resultid_List.append(int(taskname.text))
            facility_point_id_list.append(object.find('ObjectID').text)
        #####################################################################################
        #####################################################################################
        ##########################################################################################################################################################################
        #####################################################################################
        ##########################################################################################################################################################################
        # NEED TO FIX, NEED TO FIND MAX IDS THEN ADD THIS PART
        worktaskId_counter = 1
        resultId_counter = 1

        condtion_globals = []
        source_condition_globals = []
        # treatment_globals = []
        photo_globals = []
        globalList = []
        counter = 1
        counter1 = 0

        removecounter = 0
        while removecounter != 10:
            for child in root:
                if child.tag == ('Objects'):
                    for child2 in child:
                        for child3 in child2:
                            if child3.tag == 'WorkResults':
                                for child4 in child3:
                                    for child5 in child4:
                                        # Leave this in or take this out based on what kyle wants
                                        if child5.tag == 'WorkTaskType':
                                            #     if child5.text == 'OUT_CONDITION':
                                            # child3.remove(child4)
                                            if child5.text == 'EQUIPMENT':
                                                child3.remove(child4)
                                        if child5.tag == 'WorkTaskName':
                                            if child5.text in ['TREATMENT_CODE', 'PRIOR_TREATMENT', 'TREATMENT_DATE',
                                                               'INFORMATION_CODE', 'TREATMENT_REMARKS',
                                                               'INFORMATION_IDN', 'INFORMATION_REMARKS', 'CSS_LATITUDE',
                                                               'CSS_LONGITUDE', 'PADMS_GPS_LATITUDE',
                                                               'PADMS_GPS_LONGITUDE']:
                                                child3.remove(child4)
            removecounter += 1

        persondict = {}
        with arcpy.da.SearchCursor(persontable, ['drg_auditor', 'pac_inspector']) as cursor:
            for row in cursor:
                persondict[row[0]] = row[1]
        if str(Type) == 'DTLSB':
            pole_fields = [facility_point_id, Height, Birthdate, Birthdate_Estimated, Class, Stubbing_Code,  # 5
                           Pole_Material, Manufacturer_Treatment_Code, PoleTop_Cond_Code, GrdLine_Cond_Code, Decay_Location,
                           # 10
                           Condition, #11
                           Structure_Type, pole_id, Inspection_ID, inspection_set_id, Circuit_ID,  # 16
                           Multiple_Circuit_ID, ESRI_LATITUDE, ESRI_LONGITUDE, facility_point_id, 'SHAPE', 'Audit_Date',
                           'GlobalID',
                           'WorkSetID',  # 24
                           'Symbology', 'ObjectID', 'Inspection_Type', 'Audit_User', 'Facility_Address', 'ObjectID',
                           'Indication_Remark',  # 31
                           'MapString', 'Section', 'Alt_PoleID', 'WorkAreaID', 'ObjectID', 'State']  # 37
        elif str(Type) == 'VA':
            pole_fields = [facility_point_id, Height, Birthdate, facility_point_id, Class, facility_point_id,  # 5
                           Pole_Material, facility_point_id, facility_point_id, facility_point_id, facility_point_id,
                           # 10
                           Condition,
                           Structure_Type, pole_id, Inspection_ID, inspection_set_id, facility_point_id,  # 16
                           facility_point_id, ESRI_LATITUDE, ESRI_LONGITUDE, facility_point_id, 'SHAPE', 'Audit_Date',
                           'GlobalID',
                           'WorkSetID',  # 24
                           'Symbology', 'ObjectID', 'Inspection_Type', 'Audit_User', 'Facility_Address', 'ObjectID',
                           'Indication_Remark',  # 31
                           'MapString', 'Section', 'Alt_PoleID', 'WorkAreaID', 'ObjectID', 'State']  # 37

        # ElevationFields = ['REL_GLOBALID', 'Z', 'WorkSetID']
        # elevation_dict = {}
        # with arcpy.da.SearchCursor(ElevationPole, ElevationFields) as cursor:
        #     for row in cursor:
        #         if row[2] == WorksetID and row[1] is not None:
        #             elevation_dict[row[0]] = int(row[1])

        ##outside XML Stuff
        PriorWorkSetFlagtext = 'N'
        StateAbbrvtext = ''
        UsageTypetext = ''
        WorkAreaIDtext = ''
        WorkMaptext = ''
        WorkMapSectiontext = ''
        WorkSetIDtext = ''
        WorkSetCategorytext = str(Type)
        WorkSourcetext = '1'

        with arcpy.da.SearchCursor(Pole, pole_fields) as cursor:
            for row in cursor:
                if FailedPointsList:
                    if str(row[36]) in FailedPointsList:
                        if row[24] == WorksetID or str(row[23]) == '{047631C3-695C-466F-BB6A-077CB0F95C32}':  # or row[30] in (47382, 47383, 48172) :
                            arcpy.AddMessage(row[36])
                            StateAbbrvtext = str(row[37])
                            UsageTypetext = ''
                            WorkAreaIDtext = str(row[35])
                            WorkMaptext = str(row[32])
                            WorkMapSectiontext = str(row[33])
                            WorkSetIDtext = str(row[24])
                            WorkSourcetext = ''

                            mapstring_section = str(row[32]) + str(row[33])
                            if row[25] == 2:
                                photo_globals.append(row[23])
                            if row[25] not in (1, 99,  4, 55):
                                # arcpy.AddMessage(row[23])
                                globalList.append(row[23])
                                counter1 += 1
                                photo_globals.append(row[23])
                                # arcpy.AddMessage('------------------------------------------------------------------------------------------------')
                                # arcpy.AddMessage(counter)

                                counter += 1
                                ObjectTags = []
                                # Adding
                                source_condition_globals.append(row[23])
                                if row[11] == 'Y':
                                    condtion_globals.append(row[23])
                                # if row[20] == 'Y':
                                #     treatment_globals.append(row[23])
                                for object in root.iter('Objects'):
                                    newObject = ET.SubElement(object, 'Object')
                                    element4 = ET.SubElement(newObject, 'AlternateObjectID')
                                    #######################################################################################################################
                                    altobjid = '0' + str(row[13])
                                    element4.text = str(row[13])
                                    objectIDElement = ET.SubElement(newObject, 'ObjectID')
                                    if row[0] is not None:
                                        objectIDElement.text = str(row[0])
                                    else:
                                        pass
                                    objectMemeberIDElement = ET.SubElement(newObject, 'ObjectMemberID')
                                    if row[15] is not None:
                                        objectMemeberIDElement.text = str(row[15])
                                    else:
                                        pass
                                    element5 = ET.SubElement(newObject, 'StructureType')

                                    if row[12] == 1:
                                        element5.text = 'OH'
                                    if row[12] == 2:
                                        element5.text = 'UG'
                                    objectMemeberPositionElement = ET.SubElement(newObject, 'ObjectMemberPosition')
                                    workaction_element = ET.SubElement(newObject, 'WorkAction')
                                    if row[25] == 77:

                                        workaction_element.text = 'REMOVED'

                                    elif row[25] == 3:

                                        workaction_element.text = 'ADDED'
                                    elif row[25] not in (77, 3) and row[34] is not None:

                                        workaction_element.text = 'RENAMED'
                                    elif row[25] not in (77, 3) and row[34] is None:

                                        workaction_element.text = 'UNCHANGED'
                                    if row[25] == 44 and row[31] == 13:

                                        workaction_element.text = 'STRUCT_TYP_CHG'
                                    element1 = ET.SubElement(newObject, 'WorkSequence')
                                    worksequence += 1
                                    element1.text = str(worksequence)
                                    # element2 = ET.SubElement(newObject, 'PriorWorkID')

                                    # objectMemeberPositionElement = ET.SubElement(newObject, 'ObjectMemberPosition')
                                    element3 = ET.SubElement(newObject, 'WorkID')
                                    element3.text = str(row[26])

                                    element6 = ET.SubElement(newObject, 'VendorTrackerID')
                                    element6.text = str(row[23])


                                    if row[27] is not None:

                                        d_element = ET.SubElement(newObject, 'WorkCategory')
                                        if Type == 'VA' and row[25] == 77:
                                            d_element.text = ('REMOVED_FP')
                                        if Type == 'VA' and row[25] != 77:
                                            d_element.text = ('SAFETY')
                                        else:
                                            if row[27] == 1:
                                                d_element.text = ('DETAIL')
                                            if row[27] in [2, 3, 4]:
                                                d_element.text = ('DTLSB')
                                            if row[27] == 5:
                                                d_element.text = ('REMOVED_FP')
                                            if row[27] == 6:
                                                d_element.text = ('NOINSPECT')
                                        if row[31] == 13:
                                            d_element.text = ('NOINSPECT')
                                    if row[28] is not None:
                                        f_element = ET.SubElement(newObject, 'Organization')
                                        e_element = ET.SubElement(f_element, 'ErpPerson')

                                        e_element.text = persondict[row[28]]

                                    PriorWorkIDElement = ET.SubElement(newObject, 'PriorWorkID')
                                    if row[14] is not None:
                                        PriorWorkIDElement.text = str(row[14])
                                    else:
                                        pass


                                    if row[22] is not None:
                                        oldtime = row[22]
                                        now_formatted = oldtime.strftime('%Y%m%d')
                                        time_element = ET.SubElement(newObject, 'WorkTimestamp')
                                        time_element.text = (str(now_formatted))
                                    if Type == 'VA':
                                        PhotoDocumentations = ET.SubElement(newObject, 'PhotoDocumentations')

                                    child = ET.SubElement(newObject, 'WorkResults')

                                    # arcpy.AddMessage(checklist)
                                    # Adding any work results
                                    if Type == 'DTLSB':
                                        if row[16] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = (str(row[16]))
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(22)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('CIRCUIT_ID')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('CIRCUIT_ATTRIBUTES')
                                    if Type == 'DTLSB':
                                        if row[17] is not None:
                                            # arcpy.AddMessage('MULTIPLE_CIRCUIT_INDICATOR')
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = (str(row[17]))
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(23)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('MULTIPLE_CIRCUIT_INDICATOR')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('CIRCUIT_ATTRIBUTES')
                                        elif row[17] is None:
                                            # arcpy.AddMessage('MULTIPLE_CIRCUIT_INDICATOR')
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = 'N'
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(23)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('MULTIPLE_CIRCUIT_INDICATOR')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('CIRCUIT_ATTRIBUTES')
                                    if Type == 'DTLSB':
                                        if row[9] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = (str(row[9]))
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(118)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('GROUND_LINE_CONDITION_CODE')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('POLE_INSPECTION')
                                    if Type == 'DTLSB':
                                        if row[8] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = (str(row[8]))
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(117)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('POLE_TOP_CONDITION_CODE')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('POLE_INSPECTION')
                                    if row[25] == 77 and row[31] is not None:
                                        # arcpy.AddMessage((row[31]))
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        # arcpy.AddMessage((row[31]))
                                        if row[31] == 6:
                                            element3.text = 'RMV: NIF'
                                            #arcpy.AddMessage(row[0])
                                        if row[31] == 7:
                                            element3.text = 'RMV: MP'
                                        if row[31] == 8:
                                            element3.text = 'RMV: SL'
                                        if row[31] == 9:
                                            element3.text = 'RMV: CO'
                                        if row[31] == 10:
                                            element3.text = 'RMV: UB'
                                        if row[31] == 11:
                                            element3.text = 'RMV: DATA DEL'
                                        if row[31] == 12:
                                            element3.text = 'RMV: OTH'
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(456)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('ACTION_INDICATOR_RMKS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('FLD_DATA_CORRECTION')
                                    if row[25] == 88 and row[31] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        if row[31] == 15:
                                            element3.text = 'LOCKED GATE'
                                        if row[31] == 17:
                                            element3.text = 'DANGEROUS ANIMAL'
                                        if row[31] == 17:
                                            element3.text = 'VEGETATION BLOCKING FACILITY'
                                        if row[31] == 18:
                                            element3.text = 'NEED TO CONTACT OWNER'
                                        if row[31] == 19:
                                            element3.text = 'ACCESS DENIED'
                                        if row[31] == 20:
                                            element3.text = 'NO GATE'
                                        if row[31] == 21:
                                            element3.text = 'NO ROAD OR IMPASSABLE: WASHED OUT/LANDSLIDE/TREES DOWN/NEED CULVERT'
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(456)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('ACTION_INDICATOR_RMKS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('FLD_DATA_CORRECTION')
                                    if row[25] != 3:
                                        if row[18] is not None:
                                            # arcpy.AddMessage('Adding GPS')
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            position_parent = element1.text
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = ('N')
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(25)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('GPS_MEAS_TAKEN')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('OBSERVED_POSITION')
                                        if row[18] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            parentelement = ET.SubElement(element, 'ParentResultID')
                                            parentelement.text = position_parent
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            lat_length = str(row[18])
                                            while len(lat_length) < 9:
                                                lat_length = lat_length + '0'
                                            element3.text = (lat_length)
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(26)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('LATITUDE')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('OBSERVED_POSITION')
                                        if row[19] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            parentelement = ET.SubElement(element, 'ParentResultID')
                                            parentelement.text = position_parent
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            long_length = str(row[19])
                                            while len(long_length) < 11:
                                                long_length = long_length + '0'
                                            element3.text = (long_length)
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(27)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('LONGITUDE')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('OBSERVED_POSITION')
                                        if row[19] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            parentelement = ET.SubElement(element, 'ParentResultID')
                                            parentelement.text = position_parent
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = '-1'
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = '29'
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('GPS_QUALITY_IND')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('OBSERVED_POSITION')
                                    # if row[25] == 3:
                                    #     if row[18] is not None:
                                    #         # arcpy.AddMessage('Adding GPS')
                                    #         element = ET.SubElement(child, 'WorkResult')
                                    #         element1 = ET.SubElement(element, 'ResultID')
                                    #         resultId_counter += 1
                                    #         element1.text = str((resultId_counter))
                                    #         position_parent = element1.text
                                    #         element2 = ET.SubElement(element, 'ResultValue')
                                    #         element3 = ET.SubElement(element2, 'Value')
                                    #         element3.text = ('Y')
                                    #         worktaskId_counter += 1
                                    #         element4 = ET.SubElement(element, 'WorkTaskID')
                                    #         element4.text = str(25)
                                    #         element5 = ET.SubElement(element, 'WorkTaskName')
                                    #         element5.text = ('GPS_MEAS_TAKEN')
                                    #         element6 = ET.SubElement(element, 'WorkTaskType')
                                    #         element6.text = ('OBSERVED_POSITION')
                                    #     if row[18] is not None:
                                    #         element = ET.SubElement(child, 'WorkResult')
                                    #         parentelement = ET.SubElement(element, 'ParentResultID')
                                    #         parentelement.text = position_parent
                                    #         element1 = ET.SubElement(element, 'ResultID')
                                    #         resultId_counter += 1
                                    #         element1.text = str((resultId_counter))
                                    #         element2 = ET.SubElement(element, 'ResultValue')
                                    #         element3 = ET.SubElement(element2, 'Value')
                                    #         lat_length = str(row[18])
                                    #         while len(lat_length) < 9:
                                    #             lat_length = lat_length + '0'
                                    #         element3.text = (lat_length)
                                    #         worktaskId_counter += 1
                                    #         element4 = ET.SubElement(element, 'WorkTaskID')
                                    #         element4.text = str(26)
                                    #         element5 = ET.SubElement(element, 'WorkTaskName')
                                    #         element5.text = ('LATITUDE')
                                    #         element6 = ET.SubElement(element, 'WorkTaskType')
                                    #         element6.text = ('OBSERVED_POSITION')
                                    #     if row[19] is not None:
                                    #         element = ET.SubElement(child, 'WorkResult')
                                    #         parentelement = ET.SubElement(element, 'ParentResultID')
                                    #         parentelement.text = position_parent
                                    #         element1 = ET.SubElement(element, 'ResultID')
                                    #         resultId_counter += 1
                                    #         element1.text = str((resultId_counter))
                                    #         element2 = ET.SubElement(element, 'ResultValue')
                                    #         element3 = ET.SubElement(element2, 'Value')
                                    #         long_length = str(row[19])
                                    #         while len(long_length) < 11:
                                    #             long_length = long_length + '0'
                                    #         element3.text = (long_length)
                                    #         worktaskId_counter += 1
                                    #         element4 = ET.SubElement(element, 'WorkTaskID')
                                    #         element4.text = str(27)
                                    #         element5 = ET.SubElement(element, 'WorkTaskName')
                                    #         element5.text = ('LONGITUDE')
                                    #         element6 = ET.SubElement(element, 'WorkTaskType')
                                    #         element6.text = ('OBSERVED_POSITION')
                                    #
                                    #     if row[19] is not None:
                                    #         element = ET.SubElement(child, 'WorkResult')
                                    #         parentelement = ET.SubElement(element, 'ParentResultID')
                                    #         parentelement.text = position_parent
                                    #         element1 = ET.SubElement(element, 'ResultID')
                                    #         resultId_counter += 1
                                    #         element1.text = str((resultId_counter))
                                    #         element2 = ET.SubElement(element, 'ResultValue')
                                    #         element3 = ET.SubElement(element2, 'Value')
                                    #         element3.text = '1'
                                    #         worktaskId_counter += 1
                                    #         element4 = ET.SubElement(element, 'WorkTaskID')
                                    #         element4.text = '29'
                                    #         element5 = ET.SubElement(element, 'WorkTaskName')
                                    #         element5.text = ('GPS_QUALITY_IND')
                                    #         element6 = ET.SubElement(element, 'WorkTaskType')
                                    #         element6.text = ('OBSERVED_POSITION')
                                    elif row[25] == 3:
                                        if row[18] is not None:
                                            # arcpy.AddMessage('Adding GPS')
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            position_parent = element1.text
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = ('Y')
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(25)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('GPS_MEAS_TAKEN')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('OBSERVED_POSITION')
                                        if row[18] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            parentelement = ET.SubElement(element, 'ParentResultID')
                                            parentelement.text = position_parent
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            lat_length = str(row[18])
                                            while len(lat_length) < 9:
                                                lat_length = lat_length + '0'
                                            element3.text = (lat_length)
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(26)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('LATITUDE')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('OBSERVED_POSITION')
                                        if row[19] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            parentelement = ET.SubElement(element, 'ParentResultID')
                                            parentelement.text = position_parent
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            long_length = str(row[19])
                                            while len(long_length) < 11:
                                                long_length = long_length + '0'
                                            element3.text = (long_length)
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(27)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('LONGITUDE')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('OBSERVED_POSITION')

                                        if row[19] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            parentelement = ET.SubElement(element, 'ParentResultID')
                                            parentelement.text = position_parent
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = '1'
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = '29'
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('GPS_QUALITY_IND')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('OBSERVED_POSITION')


                                        if row[19] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            parentelement = ET.SubElement(element, 'ParentResultID')
                                            parentelement.text = position_parent
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')

                                            URL = r"http://api.geonames.org/srtm1JSON?lat={0}&lng={1}&&username=marcmore".format(
                                                str(row[18]), str(row[19]))
                                            #arcpy.AddMessage(URL)
                                            # URL = r"http://api.geonames.org/srtm1JSON?lat=50.01&lng=10.2&&username=marcmore"
                                            response = requests.get(URL)
                                            data = response.json()
                                            z_meters = data['srtm1']
                                            z_feet = int(z_meters) # * 3.281
                                            element3.text = str(z_feet)
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = '32'
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('APPROX_ELEVATION')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('OBSERVED_POSITION')
                                        if row[19] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            parentelement = ET.SubElement(element, 'ParentResultID')
                                            parentelement.text = position_parent
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = str(randint(4, 6))
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = '30'
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('HDOP')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('OBSERVED_POSITION')
                                    if row[1] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[1]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(15)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('POLE_HEIGHT')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('PHYSICAL_ATTRIBUTES')
                                    if row[2] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[2]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(16)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('YEAR_INSTALLED')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('PHYSICAL_ATTRIBUTES')
                                    if Type == 'DTLSB':
                                        if row[3] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = (str(row[3]))
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(17)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('YEAR_INSTALLED_AGE_ESTIMATE')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('PHYSICAL_ATTRIBUTES')
                                    if row[6] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[6]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(20)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('POLE_COMPOSITION_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('PHYSICAL_ATTRIBUTES')
                                    if row[4] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[4]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(18)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('POLE_CLASS_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('PHYSICAL_ATTRIBUTES')
                                    if Type == 'DTLSB':
                                        if row[5] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = (str(row[5]))
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(19)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('POLE_STUBBING_CODE')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('PHYSICAL_ATTRIBUTES')
                                    if Type == 'DTLSB':
                                        if row[7] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = str((resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = (str(row[7]))
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(21)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('MANUFACTURER_TREATMENT_CODE')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('PHYSICAL_ATTRIBUTES')
                                    if Type == 'DTLSB':
                                        if row[10] is not None:
                                            element = ET.SubElement(child, 'WorkResult')
                                            element1 = ET.SubElement(element, 'ResultID')
                                            resultId_counter += 1
                                            element1.text = (str(resultId_counter))
                                            element2 = ET.SubElement(element, 'ResultValue')
                                            element3 = ET.SubElement(element2, 'Value')
                                            element3.text = (str(row[10]))
                                            worktaskId_counter += 1
                                            element4 = ET.SubElement(element, 'WorkTaskID')
                                            element4.text = str(119)
                                            element5 = ET.SubElement(element, 'WorkTaskName')
                                            element5.text = ('DECAY_LOCATION_CODE')
                                            element6 = ET.SubElement(element, 'WorkTaskType')
                                            element6.text = ('PHYSICAL_ATTRIBUTES')
                                    if row[29] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = (str(resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = row[29]
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(128)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('FACILITY_ADDRESS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('INFORMATION')
                                    # TreatmentCode
                                    if row[27] in [2, 3, 4]:
                                        # arcpy.AddMessage('ysy')
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')

                                        element1.text = str((resultId_counter))
                                        parentid = str(resultId_counter)
                                        resultId_counter += 1
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        if row[27] == 2:
                                            element3.text = 'SOUND'
                                        elif row[27] in [3, 4]:
                                            element3.text = 'SNDBORE'
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(299)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('TREATMENT_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('TREATMENT')
                                    # TreatmentWorkType
                                    if row[27] in [2, 3, 4]:
                                        element = ET.SubElement(child, 'WorkResult')
                                        # element7 = ET.SubElement(element, 'ParentResultID')
                                        # element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = 'I_BORE'
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(298)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('TRTMT_WORK_TYPE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('TREATMENT')
                                    # TREATMENT_DATE
                                    if row[27] in [2, 3, 4]:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        oldtime = row[22]
                                        now_formatted = oldtime.strftime('%Y%m%d')
                                        element3.text = str(now_formatted)
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(300)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('TREATMENT_DATE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('TREATMENT')


                else:
                    if row[24] == WorksetID:  # or row[30] in (47382, 47383, 48172) :
                        #.AddMessage(row[36])
                        StateAbbrvtext = str(row[37])
                        UsageTypetext = ''
                        WorkAreaIDtext = str(row[35])
                        WorkMaptext = str(row[32])
                        WorkMapSectiontext = str(row[33])
                        WorkSetIDtext = str(row[24])
                        WorkSourcetext = ''

                        mapstring_section = str(row[32]) + str(row[33])
                        if row[25] == 2:
                            photo_globals.append(row[23])
                        if row[25] not in (1, 99,  4, 55):
                            # arcpy.AddMessage(row[23])
                            globalList.append(row[23])
                            counter1 += 1
                            photo_globals.append(row[23])
                            # arcpy.AddMessage('------------------------------------------------------------------------------------------------')
                            # arcpy.AddMessage(counter)

                            counter += 1
                            ObjectTags = []
                            # Adding
                            source_condition_globals.append(row[23])
                            if row[11] == 'Y':
                                condtion_globals.append(row[23])
                            # if row[20] == 'Y':
                            #     treatment_globals.append(row[23])
                            for object in root.iter('Objects'):
                                newObject = ET.SubElement(object, 'Object')
                                element4 = ET.SubElement(newObject, 'AlternateObjectID')
                                #######################################################################################################################
                                altobjid = '0' + str(row[13])
                                element4.text = str(row[13])
                                objectIDElement = ET.SubElement(newObject, 'ObjectID')
                                if row[0] is not None:
                                    objectIDElement.text = str(row[0])
                                else:
                                    pass
                                objectMemeberIDElement = ET.SubElement(newObject, 'ObjectMemberID')
                                if row[15] is not None:
                                    objectMemeberIDElement.text = str(row[15])
                                else:
                                    pass
                                element5 = ET.SubElement(newObject, 'StructureType')

                                if row[12] == 1:
                                    element5.text = 'OH'
                                if row[12] == 2:
                                    element5.text = 'UG'
                                objectMemeberPositionElement = ET.SubElement(newObject, 'ObjectMemberPosition')
                                workaction_element = ET.SubElement(newObject, 'WorkAction')
                                if row[25] == 77:

                                    workaction_element.text = 'REMOVED'

                                elif row[25] == 3:

                                    workaction_element.text = 'ADDED'
                                elif row[25] not in (77, 3) and row[34] is not None:

                                    workaction_element.text = 'RENAMED'
                                elif row[25] not in (77, 3) and row[34] is None:

                                    workaction_element.text = 'UNCHANGED'
                                if row[25] == 44 and row[31] == 13:

                                    workaction_element.text = 'STRUCT_TYP_CHG'
                                element1 = ET.SubElement(newObject, 'WorkSequence')
                                worksequence += 1
                                element1.text = str(worksequence)
                                # element2 = ET.SubElement(newObject, 'PriorWorkID')

                                # objectMemeberPositionElement = ET.SubElement(newObject, 'ObjectMemberPosition')
                                element3 = ET.SubElement(newObject, 'WorkID')
                                element3.text = str(row[26])

                                element6 = ET.SubElement(newObject, 'VendorTrackerID')
                                element6.text = str(row[23])

                                if row[27] is not None:

                                    d_element = ET.SubElement(newObject, 'WorkCategory')
                                    if Type == 'VA' and row[25] == 77:
                                        d_element.text = ('REMOVED_FP')
                                    if Type == 'VA' and row[25] != 77:
                                        d_element.text = ('SAFETY')
                                    else:
                                        if row[27] == 1:
                                            d_element.text = ('DETAIL')
                                        if row[27] in [2, 3, 4]:
                                            d_element.text = ('DTLSB')
                                        if row[27] == 5:
                                            d_element.text = ('REMOVED_FP')
                                        if row[27] == 6:
                                            d_element.text = ('NOINSPECT')
                                    if row[31] == 13:
                                            d_element.text = ('NOINSPECT')
                                if row[28] is not None:
                                    f_element = ET.SubElement(newObject, 'Organization')
                                    e_element = ET.SubElement(f_element, 'ErpPerson')

                                    e_element.text = persondict[row[28]]

                                PriorWorkIDElement = ET.SubElement(newObject, 'PriorWorkID')
                                if row[14] is not None:
                                    PriorWorkIDElement.text = str(row[14])
                                else:
                                    pass

                                if row[22] is not None:
                                    oldtime = row[22]
                                    now_formatted = oldtime.strftime('%Y%m%d')
                                    time_element = ET.SubElement(newObject, 'WorkTimestamp')
                                    time_element.text = (str(now_formatted))
                                if Type == 'VA':
                                    PhotoDocumentations = ET.SubElement(newObject, 'PhotoDocumentations')

                                child = ET.SubElement(newObject, 'WorkResults')

                                # arcpy.AddMessage(checklist)
                                # Adding any work results
                                if Type == 'DTLSB':
                                    if row[16] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[16]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(22)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CIRCUIT_ID')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('CIRCUIT_ATTRIBUTES')
                                if Type == 'DTLSB':
                                    if row[17] is not None:
                                        # arcpy.AddMessage('MULTIPLE_CIRCUIT_INDICATOR')
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[17]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(23)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('MULTIPLE_CIRCUIT_INDICATOR')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('CIRCUIT_ATTRIBUTES')
                                    elif row[17] is None:
                                        # arcpy.AddMessage('MULTIPLE_CIRCUIT_INDICATOR')
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = 'N'
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(23)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('MULTIPLE_CIRCUIT_INDICATOR')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('CIRCUIT_ATTRIBUTES')
                                if Type == 'DTLSB':
                                    if row[9] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[9]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(118)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('GROUND_LINE_CONDITION_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('POLE_INSPECTION')
                                if Type == 'DTLSB':
                                    if row[8] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[8]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(117)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('POLE_TOP_CONDITION_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('POLE_INSPECTION')
                                if row[25] == 77 and row[31] is not None:
                                    # arcpy.AddMessage((row[31]))
                                    element = ET.SubElement(child, 'WorkResult')
                                    element1 = ET.SubElement(element, 'ResultID')
                                    resultId_counter += 1
                                    element1.text = str((resultId_counter))
                                    element2 = ET.SubElement(element, 'ResultValue')
                                    element3 = ET.SubElement(element2, 'Value')
                                    # arcpy.AddMessage((row[31]))
                                    if row[31] == 6:
                                        element3.text = 'RMV: NIF'
                                        # arcpy.AddMessage(row[0])
                                    if row[31] == 7:
                                        element3.text = 'RMV: MP'
                                    if row[31] == 8:
                                        element3.text = 'RMV: SL'
                                    if row[31] == 9:
                                        element3.text = 'RMV: CO'
                                    if row[31] == 10:
                                        element3.text = 'RMV: UB'
                                    if row[31] == 11:
                                        element3.text = 'RMV: DATA DEL'
                                    if row[31] == 12:
                                        element3.text = 'RMV: OTH'
                                    worktaskId_counter += 1
                                    element4 = ET.SubElement(element, 'WorkTaskID')
                                    element4.text = str(456)
                                    element5 = ET.SubElement(element, 'WorkTaskName')
                                    element5.text = ('ACTION_INDICATOR_RMKS')
                                    element6 = ET.SubElement(element, 'WorkTaskType')
                                    element6.text = ('FLD_DATA_CORRECTION')
                                if row[25] == 88 and row[31] is not None:
                                    element = ET.SubElement(child, 'WorkResult')
                                    element1 = ET.SubElement(element, 'ResultID')
                                    resultId_counter += 1
                                    element1.text = str((resultId_counter))
                                    element2 = ET.SubElement(element, 'ResultValue')
                                    element3 = ET.SubElement(element2, 'Value')
                                    if row[31] == 15:
                                        element3.text = 'LOCKED GATE'
                                    if row[31] == 17:
                                        element3.text = 'DANGEROUS ANIMAL'
                                    if row[31] == 17:
                                        element3.text = 'VEGETATION BLOCKING FACILITY'
                                    if row[31] == 18:
                                        element3.text = 'NEED TO CONTACT OWNER'
                                    if row[31] == 19:
                                        element3.text = 'ACCESS DENIED'
                                    if row[31] == 20:
                                        element3.text = 'NO GATE'
                                    if row[31] == 21:
                                        element3.text = 'NO ROAD OR IMPASSABLE: WASHED OUT/LANDSLIDE/TREES DOWN/NEED CULVERT'
                                    worktaskId_counter += 1
                                    element4 = ET.SubElement(element, 'WorkTaskID')
                                    element4.text = str(456)
                                    element5 = ET.SubElement(element, 'WorkTaskName')
                                    element5.text = ('ACTION_INDICATOR_RMKS')
                                    element6 = ET.SubElement(element, 'WorkTaskType')
                                    element6.text = ('FLD_DATA_CORRECTION')
                                if row[25] != 3:
                                    if row[18] is not None:
                                        # arcpy.AddMessage('Adding GPS')
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        position_parent = element1.text
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = ('N')
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(25)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('GPS_MEAS_TAKEN')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OBSERVED_POSITION')
                                    if row[18] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        parentelement = ET.SubElement(element, 'ParentResultID')
                                        parentelement.text = position_parent
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        lat_length = str(row[18])
                                        while len(lat_length) < 9:
                                            lat_length = lat_length + '0'
                                        element3.text = (lat_length)
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(26)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('LATITUDE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OBSERVED_POSITION')
                                    if row[19] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        parentelement = ET.SubElement(element, 'ParentResultID')
                                        parentelement.text = position_parent
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        long_length = str(row[19])
                                        while len(long_length) < 11:
                                            long_length = long_length + '0'
                                        element3.text = (long_length)
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(27)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('LONGITUDE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OBSERVED_POSITION')
                                    if row[19] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        parentelement = ET.SubElement(element, 'ParentResultID')
                                        parentelement.text = position_parent
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = '-1'
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = '29'
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('GPS_QUALITY_IND')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OBSERVED_POSITION')
                                # if row[25] == 3:
                                #     if row[18] is not None:
                                #         # arcpy.AddMessage('Adding GPS')
                                #         element = ET.SubElement(child, 'WorkResult')
                                #         element1 = ET.SubElement(element, 'ResultID')
                                #         resultId_counter += 1
                                #         element1.text = str((resultId_counter))
                                #         position_parent = element1.text
                                #         element2 = ET.SubElement(element, 'ResultValue')
                                #         element3 = ET.SubElement(element2, 'Value')
                                #         element3.text = ('Y')
                                #         worktaskId_counter += 1
                                #         element4 = ET.SubElement(element, 'WorkTaskID')
                                #         element4.text = str(25)
                                #         element5 = ET.SubElement(element, 'WorkTaskName')
                                #         element5.text = ('GPS_MEAS_TAKEN')
                                #         element6 = ET.SubElement(element, 'WorkTaskType')
                                #         element6.text = ('OBSERVED_POSITION')
                                #     if row[18] is not None:
                                #         element = ET.SubElement(child, 'WorkResult')
                                #         parentelement = ET.SubElement(element, 'ParentResultID')
                                #         parentelement.text = position_parent
                                #         element1 = ET.SubElement(element, 'ResultID')
                                #         resultId_counter += 1
                                #         element1.text = str((resultId_counter))
                                #         element2 = ET.SubElement(element, 'ResultValue')
                                #         element3 = ET.SubElement(element2, 'Value')
                                #         lat_length = str(row[18])
                                #         while len(lat_length) < 9:
                                #             lat_length = lat_length + '0'
                                #         element3.text = (lat_length)
                                #         worktaskId_counter += 1
                                #         element4 = ET.SubElement(element, 'WorkTaskID')
                                #         element4.text = str(26)
                                #         element5 = ET.SubElement(element, 'WorkTaskName')
                                #         element5.text = ('LATITUDE')
                                #         element6 = ET.SubElement(element, 'WorkTaskType')
                                #         element6.text = ('OBSERVED_POSITION')
                                #     if row[19] is not None:
                                #         element = ET.SubElement(child, 'WorkResult')
                                #         parentelement = ET.SubElement(element, 'ParentResultID')
                                #         parentelement.text = position_parent
                                #         element1 = ET.SubElement(element, 'ResultID')
                                #         resultId_counter += 1
                                #         element1.text = str((resultId_counter))
                                #         element2 = ET.SubElement(element, 'ResultValue')
                                #         element3 = ET.SubElement(element2, 'Value')
                                #         long_length = str(row[19])
                                #         while len(long_length) < 11:
                                #             long_length = long_length + '0'
                                #         element3.text = (long_length)
                                #         worktaskId_counter += 1
                                #         element4 = ET.SubElement(element, 'WorkTaskID')
                                #         element4.text = str(27)
                                #         element5 = ET.SubElement(element, 'WorkTaskName')
                                #         element5.text = ('LONGITUDE')
                                #         element6 = ET.SubElement(element, 'WorkTaskType')
                                #         element6.text = ('OBSERVED_POSITION')
                                #
                                #     if row[19] is not None:
                                #         element = ET.SubElement(child, 'WorkResult')
                                #         parentelement = ET.SubElement(element, 'ParentResultID')
                                #         parentelement.text = position_parent
                                #         element1 = ET.SubElement(element, 'ResultID')
                                #         resultId_counter += 1
                                #         element1.text = str((resultId_counter))
                                #         element2 = ET.SubElement(element, 'ResultValue')
                                #         element3 = ET.SubElement(element2, 'Value')
                                #         element3.text = '1'
                                #         worktaskId_counter += 1
                                #         element4 = ET.SubElement(element, 'WorkTaskID')
                                #         element4.text = '29'
                                #         element5 = ET.SubElement(element, 'WorkTaskName')
                                #         element5.text = ('GPS_QUALITY_IND')
                                #         element6 = ET.SubElement(element, 'WorkTaskType')
                                #         element6.text = ('OBSERVED_POSITION')
                                elif row[25] == 3:
                                    if row[18] is not None:
                                        # arcpy.AddMessage('Adding GPS')
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        position_parent = element1.text
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = ('Y')
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(25)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('GPS_MEAS_TAKEN')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OBSERVED_POSITION')
                                    if row[18] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        parentelement = ET.SubElement(element, 'ParentResultID')
                                        parentelement.text = position_parent
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        lat_length = str(row[18])
                                        while len(lat_length) < 9:
                                            lat_length = lat_length + '0'
                                        element3.text = (lat_length)
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(26)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('LATITUDE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OBSERVED_POSITION')
                                    if row[19] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        parentelement = ET.SubElement(element, 'ParentResultID')
                                        parentelement.text = position_parent
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        long_length = str(row[19])
                                        while len(long_length) < 11:
                                            long_length = long_length + '0'
                                        element3.text = (long_length)
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(27)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('LONGITUDE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OBSERVED_POSITION')

                                    if row[19] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        parentelement = ET.SubElement(element, 'ParentResultID')
                                        parentelement.text = position_parent
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = '1'
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = '29'
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('GPS_QUALITY_IND')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OBSERVED_POSITION')

                                    if row[19] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        parentelement = ET.SubElement(element, 'ParentResultID')
                                        parentelement.text = position_parent
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')

                                        URL = r"http://api.geonames.org/srtm1JSON?lat={0}&lng={1}&&username=marcmore".format(
                                            str(row[18]), str(row[19]))
                                        #URL = r"http://api.geonames.org/srtm1JSON?lat=50.01&lng=10.2&&username=marcmore"
                                        response = requests.get(URL)
                                        data = response.json()
                                        z_meters = data['srtm1']
                                        z_feet = int(z_meters) # * 3.281
                                        element3.text = str(z_feet)
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = '32'
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('APPROX_ELEVATION')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OBSERVED_POSITION')
                                    if row[19] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        parentelement = ET.SubElement(element, 'ParentResultID')
                                        parentelement.text = position_parent
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = str(randint(4, 6))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = '30'
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('HDOP')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OBSERVED_POSITION')
                                if row[1] is not None:
                                    element = ET.SubElement(child, 'WorkResult')
                                    element1 = ET.SubElement(element, 'ResultID')
                                    resultId_counter += 1
                                    element1.text = str((resultId_counter))
                                    element2 = ET.SubElement(element, 'ResultValue')
                                    element3 = ET.SubElement(element2, 'Value')
                                    element3.text = (str(row[1]))
                                    worktaskId_counter += 1
                                    element4 = ET.SubElement(element, 'WorkTaskID')
                                    element4.text = str(15)
                                    element5 = ET.SubElement(element, 'WorkTaskName')
                                    element5.text = ('POLE_HEIGHT')
                                    element6 = ET.SubElement(element, 'WorkTaskType')
                                    element6.text = ('PHYSICAL_ATTRIBUTES')
                                if row[2] is not None:
                                    element = ET.SubElement(child, 'WorkResult')
                                    element1 = ET.SubElement(element, 'ResultID')
                                    resultId_counter += 1
                                    element1.text = str((resultId_counter))
                                    element2 = ET.SubElement(element, 'ResultValue')
                                    element3 = ET.SubElement(element2, 'Value')
                                    element3.text = (str(row[2]))
                                    worktaskId_counter += 1
                                    element4 = ET.SubElement(element, 'WorkTaskID')
                                    element4.text = str(16)
                                    element5 = ET.SubElement(element, 'WorkTaskName')
                                    element5.text = ('YEAR_INSTALLED')
                                    element6 = ET.SubElement(element, 'WorkTaskType')
                                    element6.text = ('PHYSICAL_ATTRIBUTES')
                                if Type == 'DTLSB':
                                    if row[3] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[3]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(17)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('YEAR_INSTALLED_AGE_ESTIMATE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('PHYSICAL_ATTRIBUTES')
                                if row[6] is not None:
                                    element = ET.SubElement(child, 'WorkResult')
                                    element1 = ET.SubElement(element, 'ResultID')
                                    resultId_counter += 1
                                    element1.text = str((resultId_counter))
                                    element2 = ET.SubElement(element, 'ResultValue')
                                    element3 = ET.SubElement(element2, 'Value')
                                    element3.text = (str(row[6]))
                                    worktaskId_counter += 1
                                    element4 = ET.SubElement(element, 'WorkTaskID')
                                    element4.text = str(20)
                                    element5 = ET.SubElement(element, 'WorkTaskName')
                                    element5.text = ('POLE_COMPOSITION_CODE')
                                    element6 = ET.SubElement(element, 'WorkTaskType')
                                    element6.text = ('PHYSICAL_ATTRIBUTES')
                                if row[4] is not None:
                                    element = ET.SubElement(child, 'WorkResult')
                                    element1 = ET.SubElement(element, 'ResultID')
                                    resultId_counter += 1
                                    element1.text = str((resultId_counter))
                                    element2 = ET.SubElement(element, 'ResultValue')
                                    element3 = ET.SubElement(element2, 'Value')
                                    element3.text = (str(row[4]))
                                    worktaskId_counter += 1
                                    element4 = ET.SubElement(element, 'WorkTaskID')
                                    element4.text = str(18)
                                    element5 = ET.SubElement(element, 'WorkTaskName')
                                    element5.text = ('POLE_CLASS_CODE')
                                    element6 = ET.SubElement(element, 'WorkTaskType')
                                    element6.text = ('PHYSICAL_ATTRIBUTES')
                                if Type == 'DTLSB':
                                    if row[5] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[5]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(19)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('POLE_STUBBING_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('PHYSICAL_ATTRIBUTES')
                                if Type == 'DTLSB':
                                    if row[7] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[7]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(21)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('MANUFACTURER_TREATMENT_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('PHYSICAL_ATTRIBUTES')
                                if Type == 'DTLSB':
                                    if row[10] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = (str(resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (str(row[10]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(119)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('DECAY_LOCATION_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('PHYSICAL_ATTRIBUTES')
                                if row[29] is not None:
                                    element = ET.SubElement(child, 'WorkResult')
                                    element1 = ET.SubElement(element, 'ResultID')
                                    resultId_counter += 1
                                    element1.text = (str(resultId_counter))
                                    element2 = ET.SubElement(element, 'ResultValue')
                                    element3 = ET.SubElement(element2, 'Value')
                                    element3.text = row[29]
                                    worktaskId_counter += 1
                                    element4 = ET.SubElement(element, 'WorkTaskID')
                                    element4.text = str(128)
                                    element5 = ET.SubElement(element, 'WorkTaskName')
                                    element5.text = ('FACILITY_ADDRESS')
                                    element6 = ET.SubElement(element, 'WorkTaskType')
                                    element6.text = ('INFORMATION')
                                # TreatmentCode
                                if row[27] in [2, 3, 4]:
                                    # arcpy.AddMessage('ysy')
                                    element = ET.SubElement(child, 'WorkResult')
                                    element1 = ET.SubElement(element, 'ResultID')

                                    element1.text = str((resultId_counter))
                                    parentid = str(resultId_counter)
                                    resultId_counter += 1
                                    element2 = ET.SubElement(element, 'ResultValue')
                                    element3 = ET.SubElement(element2, 'Value')
                                    if row[27] == 2:
                                        element3.text = 'SOUND'
                                    elif row[27] in [3, 4]:
                                        element3.text = 'SNDBORE'
                                    worktaskId_counter += 1
                                    element4 = ET.SubElement(element, 'WorkTaskID')
                                    element4.text = str(299)
                                    element5 = ET.SubElement(element, 'WorkTaskName')
                                    element5.text = ('TREATMENT_CODE')
                                    element6 = ET.SubElement(element, 'WorkTaskType')
                                    element6.text = ('TREATMENT')
                                # TreatmentWorkType
                                if row[27] in [2, 3, 4]:
                                    element = ET.SubElement(child, 'WorkResult')
                                    # element7 = ET.SubElement(element, 'ParentResultID')
                                    # element7.text = parentid
                                    element1 = ET.SubElement(element, 'ResultID')
                                    resultId_counter += 1
                                    element1.text = str((resultId_counter))
                                    element2 = ET.SubElement(element, 'ResultValue')
                                    element3 = ET.SubElement(element2, 'Value')
                                    element3.text = 'I_BORE'
                                    worktaskId_counter += 1
                                    element4 = ET.SubElement(element, 'WorkTaskID')
                                    element4.text = str(298)
                                    element5 = ET.SubElement(element, 'WorkTaskName')
                                    element5.text = ('TRTMT_WORK_TYPE')
                                    element6 = ET.SubElement(element, 'WorkTaskType')
                                    element6.text = ('TREATMENT')
                                # TREATMENT_DATE
                                if row[27] in [2, 3, 4]:
                                    element = ET.SubElement(child, 'WorkResult')
                                    element7 = ET.SubElement(element, 'ParentResultID')
                                    element7.text = parentid
                                    element1 = ET.SubElement(element, 'ResultID')
                                    resultId_counter += 1
                                    element1.text = str((resultId_counter))
                                    element2 = ET.SubElement(element, 'ResultValue')
                                    element3 = ET.SubElement(element2, 'Value')
                                    oldtime = row[22]
                                    now_formatted = oldtime.strftime('%Y%m%d')
                                    element3.text = str(now_formatted)
                                    worktaskId_counter += 1
                                    element4 = ET.SubElement(element, 'WorkTaskID')
                                    element4.text = str(300)
                                    element5 = ET.SubElement(element, 'WorkTaskName')
                                    element5.text = ('TREATMENT_DATE')
                                    element6 = ET.SubElement(element, 'WorkTaskType')
                                    element6.text = ('TREATMENT')

        counter2 = 0
        notused = []
        for object in root.iter('Object'):
            ischild = 'no'
            for child in object:
                if child.tag == 'VendorTrackerID':
                    # arcpy.AddMessage(child.text)
                    ischild = 'yes'
                    counter2 += 1
            if ischild == 'no':
                for child in object:
                    if child.tag == 'ObjectID':
                        notused.append(child.text)
        # arcpy.AddMessage(len(notused))
        objectlength = 0
        testcounter = 0
        while len(notused) > 0 or testcounter == 5:
            for child in root:
                if child.tag == ('Objects'):
                    for child2 in child:
                        objectlength += 1
                        for child3 in child2:
                            if child3.tag == 'ObjectID':
                                if child3.text in notused:
                                    notused.remove(child3.text)
                                    child.remove(child2)

            testcounter += 1

        condition_code_dict = {}
        numbers = ('1', '2', '3', '4', '5', '6', '7', '8', '9')
        with arcpy.da.SearchCursor(ConditionRemarks, ['Condition_Code', 'Condition_Description']) as cursor:
            for row in cursor:
                condition_code_dict[row[0]] = row[1]
        # Populating the source condition with the new condition status

        randomcount = 0
        codelist = defaultdict(list)
        nodups = []
        prioritylist = []
        # with arcpy.da.SearchCursor(sourceCondition, sourceConditionFields) as cursor:
        #     for row in cursor:
        #
        #
        #         if row[4] in globalList and row[0] is not None:
        #
        #             for object in root.iter('Object'):
        #                 if row[4] == object.find('VendorTrackerID').text:
        #                     if Type == 'VA':
        #                         d_element = object.find('WorkCategory')
        #                         if d_element.text != 'NOINSPECT':
        #                             d_element.text = 'SAFETYEX'
        #                     for child in object.getchildren():
        #                         if child.tag == 'WorkResults':
        #
        #                             for child1 in child:  # child1 tag is work result
        #
        #                                 for child2 in child1:
        #
        #                                     # print child2.text
        #                                     # if child2.text == 'CONDITION_PRIORITY_CODE':
        #                                     #     child1.find('Value').text = row[1]
        #                                     # print child2.text
        #                                     parentresultid = ''
        #                                     for child3 in child2:
        #                                         # if child3.text in ['A', 'B', 'C', 'D'] and child1.find('ResultID').text not in prioritylist:
        #                                         #     child3.text = row[1]
        #                                         #     prioritylist.append(child1.find('ResultID').text)
        #
        #                                         if row[0] == child3.text:
        #                                             #nodups.append(row[4])
        #                                             #arcpy.AddMessage(codelist)
        #                                             parentresultid = child1.find('ResultID').text
        #                                             if parentresultid not in nodups:
        #
        #                                                 #arcpy.AddMessage(parentresultid)
        #                                                 # CONDITION_STATUS
        #                                                 if row[3] is not None:
        #                                                     randomcount += 1
        #                                                     element = ET.SubElement(child, 'WorkResult')
        #                                                     element7 = ET.SubElement(element, 'ParentResultID')
        #                                                     element7.text = parentresultid
        #                                                     element1 = ET.SubElement(element, 'ResultID')
        #                                                     resultId_counter += 1
        #                                                     element1.text = str((resultId_counter))
        #                                                     element2 = ET.SubElement(element, 'ResultValue')
        #                                                     element3 = ET.SubElement(element2, 'Value')
        #                                                     if row[3] == 'CORRECTED':
        #                                                         element3.text = 'CORRECTED'
        #                                                     if row[3] == 'REMOVED':
        #                                                         element3.text = 'REMOVED'
        #                                                     if row[3] == 'PRIORITYCHG':
        #                                                         element3.text = 'PRIORITYCHG'
        #                                                         prioritylist.append(parentresultid)
        #                                                     if row[3] == 'NOCHANGE':
        #                                                         element3.text = 'NOCHANGE'
        #
        #
        #                                                     worktaskId_counter += 1
        #                                                     element4 = ET.SubElement(element, 'WorkTaskID')
        #                                                     element4.text = str(125)
        #                                                     element5 = ET.SubElement(element, 'WorkTaskName')
        #                                                     element5.text = ('CONDITION_STATUS')
        #                                                     element6 = ET.SubElement(element, 'WorkTaskType')
        #                                                     element6.text = ('OUT_CONDITION')
        #                                                     # STATUS_REMARK
        #                                                     if row[3] is not None:
        #                                                         randomcount += 1
        #                                                         element = ET.SubElement(child, 'WorkResult')
        #                                                         element7 = ET.SubElement(element, 'ParentResultID')
        #                                                         element7.text = parentresultid
        #                                                         element1 = ET.SubElement(element, 'ResultID')
        #                                                         resultId_counter += 1
        #                                                         element1.text = str((resultId_counter))
        #                                                         element2 = ET.SubElement(element, 'ResultValue')
        #                                                         element3 = ET.SubElement(element2, 'Value')
        #                                                         if row[3] == 'CORRECTED':
        #                                                             element3.text = 'fixed'
        #                                                         if row[3] == 'REMOVED':
        #                                                             element3.text = 'fixed'
        #                                                         if row[3] == 'PRIORITYCHG':
        #                                                             if row[1] == 'A':
        #                                                                 element3.text = 'B2A'
        #                                                             if row[1] == 'B':
        #                                                                 element3.text = 'C2B'
        #
        #                                                         if row[3] == 'NOCHANGE':
        #                                                             element3.text = 'NOCHANGE'
        #
        #                                                         worktaskId_counter += 1
        #                                                         element4 = ET.SubElement(element, 'WorkTaskID')
        #                                                         element4.text = str(126)
        #                                                         element5 = ET.SubElement(element, 'WorkTaskName')
        #                                                         element5.text = ('STATUS_REMARK')
        #                                                         element6 = ET.SubElement(element, 'WorkTaskType')
        #                                                         element6.text = ('OUT_CONDITION')
        #                                                     nodups.append(parentresultid)
        #                                                 # if row[4] not in test.keys():
        #                                                 #     codelist[str(row[4])].append(str(row[0]))
        #                                                 # else:
        #                                                 #     if str(row[0]) in codelist[str(row[4])]:
        #                                                 #         codelist[str(row[4])].append(str(row[0]))
        #             #
        #             for object in root.iter('Object'):
        #                 if row[4] == object.find('VendorTrackerID').text:
        #                     for child in object.getchildren():
        #                         if child.tag == 'WorkResults':
        #
        #                             for child1 in child:  # child1 tag is work result
        #
        #                                 for child2 in child1:
        #
        #                                     # print child2.text
        #                                     # if child2.text == 'CONDITION_PRIORITY_CODE':
        #                                     #     child1.find('Value').text = row[1]
        #                                     # print child2.text
        #
        #                                     for child3 in child2:
        #                                         if  child1.find('WorkTaskName').text == 'CONDITION_PRIORITY_CODE' and child1.find('ParentResultID').text in prioritylist:
        #                                             child3.text = row[1]
        #                                             #child3.text = 'A'
        #                                             #arcpy.AddMessage(child3.text)
        #                                             #prioritylist.append(child1.find('ResultID').text)
        # #arcpy.AddMessage(prioritylist)
        #
        # #arcpy.AddMessage('SourceStatus count')
        # #arcpy.AddMessage(randomcount)
        #
        #
        #

        now = datetime.datetime.now()
        now_formatted = now.strftime('%Y%m%d%H%M%S')

        # this is for the condtions with priority A that need a Photo
        ccondtionphotodict = {}
        with arcpy.da.SearchCursor(ConditionPhotoTable, ['Photo_Name', 'REL_GLOBALID']) as cursor:
            for row in cursor:
                if '_1' in row[0]:
                    ccondtionphotodict[row[1]] = row[0]

        # arcpy.AddMessage('Finished writing Pole records XML')
        PhotoFields = ['Photo_Name', 'REL_GLOBALID']  # 9
        phototest = []
        # arcpy.AddMessage('Start writing Photos to XML')
        dupphotolist = []
        # this search cursor is to make sure no duplicate photos are included in the xml
        with arcpy.da.SearchCursor(PhotoTable, PhotoFields) as cursor:
            for row in cursor:
                dupphotolist.append(row[0])
        set1 = set(dupphotolist)
        # arcpy.AddMessage(photo_globals)
        phototrackinglist = []
        # reading the phototracking table and populating results in xml
        with arcpy.da.SearchCursor(PhotoTable, PhotoFields) as cursor:
            for row in cursor:
                if row[1] in photo_globals and row[0] is not None:
                    # arcpy.AddMessage(1)
                    phototest.append(row[1])
                    phototrackinglist = []
                    for object in root.iter('Object'):
                        if row[1] == object.find('VendorTrackerID').text:
                            # arcpy.AddMessage(2)
                            for child in object.getchildren():
                                phototrackinglist.append(child.tag)
                                # arcpy.AddMessage(3)
                            if 'PhotoDocumentations' not in phototrackinglist:
                                # arcpy.AddMessage(photo_globals)
                                # arcpy.AddMessage('Adding a Photo')
                                set1.remove(row[0])
                                element = ET.SubElement(object, 'PhotoDocumentations')
                                element1 = ET.SubElement(element, 'PhotoDocumentation')
                                element2 = ET.SubElement(element1, 'PhotoFileName')
                                element2.text = str((row[0]))
                                element3 = ET.SubElement(element1, 'PhotoDescription')
                                if '_1' in row[0] or '_3' in row[0]:
                                    element3.text = 'Overview'
                                else:
                                    element3.text = 'Attachments and Apparatus'
                                element4 = ET.SubElement(element1, 'PhotoType')
                                if '_1' in row[0] or '_3' in row[0]:
                                    element4.text = 'Overview'
                                else:
                                    element4.text = 'Close-Up'

                            elif 'PhotoDocumentations' in phototrackinglist and row[0] in set1:
                                # arcpy.AddMessage('Adding a Second Photo')
                                set1.remove(row[0])
                                for child in object.getchildren():
                                    if child.tag == 'PhotoDocumentations':
                                        element5 = ET.SubElement(child, 'PhotoDocumentation')
                                        element6 = ET.SubElement(element5, 'PhotoFileName')
                                        element6.text = str((row[0]))
                                        element7 = ET.SubElement(element5, 'PhotoDescription')
                                        if '_1' in row[0] or '_3' in row[0]:
                                            element7.text = 'Overview'
                                        else:
                                            element7.text = 'Attachments and Apparatus'
                                        element8 = ET.SubElement(element5, 'PhotoType')
                                        if '_1' in row[0] or '_3' in row[0]:
                                            element8.text = 'Overview'
                                        else:
                                            element8.text = 'Close-Up'

        # arcpy.AddMessage('Start writing Condition records to XML')
        ConditionFields = ['Type', 'Condition_Code', 'Condition_Priority', 'Condition_Remarks', 'Condition_Status',
                           # 4
                           'Status_Remark', 'REL_GLOBALID', 'GlobalID', 'created_user', 'created_date']  # 9

        sourceConditionFields = ['Condition_Code', 'Condition_Code', 'Condition_Priority', 'Condition_Remarks',
                                 'Condition_Status',
                                 # 4
                                 'Status_Remark', 'REL_GLOBALID', 'GlobalID', 'created_user', 'Source_Date_String', 'Source_ID',
                                 'Source_Priority']  # 11

        photodescription = {}
        extra_descriptions = ['SVCPOA', 'SVCGUARD', 'SVCPOAGU', 'SVCPOACU', 'SVCYARD', 'SVCCUSTW', 'SVCEST',
                              'SVCDRIVE',
                              'SVCROAD', 'SVCCOMMD', 'SVCROOF', 'SVCDECK', 'SVCNEUT', 'SVCPOOL', 'SVCWIND',
                              'SVCRUBCM',
                              'SVCRUBLG', 'GO95SVC', 'SVCDEFLC', 'CLEAR']

        sourceConditionPhotodict = {}
        sourceconglobals = []
        with arcpy.da.SearchCursor(sourceConditionPhotoTable, ['Photo_Name', 'REL_GLOBALID']) as cursor:
            for row in cursor:
                if '_1' in row[0]:
                    sourceconglobals.append(row[1])
                    sourceConditionPhotodict[row[1]] = row[0]

        # sourcepole_globals = []
        # with  arcpy.da.SearchCursor(sourcePole, ['facility_point_id', 'GlobalID']) as cursor:
        #     for row in cursor:
        #         sourcepole_globals.append(row[0])
        #
        # if Type == 'VA':
        #     for object in root.iter('Object'):
        #         try:
        #             photoexist = object.find('PhotoDocumentations').text
        #             print (photoexist)
        #         except:
        #             elemen = ET.SubElement(object, 'PhotoDocumentations')
        # #arcpy.AddMessage('Starting source contitions photos')
        # sourcephotodescription = {}
        # with arcpy.da.SearchCursor(sourceCondition, sourceConditionFields)as cursor:
        #     for row in cursor:
        #         if row[8] in sourcepole_globals and row[3] != 'ABM' and row[5] in sourceconglobals:
        #             #arcpy.AddMessage(row[8])
        #             if ((row[1] in ('A', 'B') and row[0] != 'GRDBROKE') or row[0] in extra_descriptions) and row[
        #                 0] in condition_code_dict.keys():
        #                 # dictionary with Condition global id as key and condition remark as value
        #                 try:
        #
        #
        #                     sourcephotodescription[row[5]] = (condition_code_dict[row[0]])
        #                 except:
        #                     continue
        #             for object in root.iter('Object'):
        #                 # if row[6] is None:
        #                 #     arcpy.AddMessage(row[7])
        #                 if row[4] == object.find('VendorTrackerID').text:
        #                     for child in object.getchildren():
        #
        #                         if child.tag == 'PhotoDocumentations':
        #                             for key, value in sourceConditionPhotodict.iteritems():
        #                                 if key == row[5] and key in sourcephotodescription.keys():
        #                                     # arcpy.AddMessage('added photo')
        #                                     element = ET.SubElement(child, 'PhotoDocumentation')
        #                                     element1 = ET.SubElement(element, 'PhotoFileName')
        #                                     element1.text = value
        #                                     element2 = ET.SubElement(element, 'PhotoDescription')
        #                                     element2.text = sourcephotodescription[key]
        #                                     element3 = ET.SubElement(element, 'PhotoType')
        #                                     element3.text = 'Conditions'

        # Adding all the conditions from the condition table to xml
        with arcpy.da.SearchCursor(ConditionTable, ConditionFields) as cursor:
            for row in cursor:
                if row[6] in condtion_globals and row[4] != 'ABM':
                    if (row[2] in ('A', 'B') and row[1] != 'GRDBROKE') or row[1] in extra_descriptions:
                        photodescription[row[7]] = (condition_code_dict[row[1]])
                    condition_photos = []
                    for object in root.iter('Object'):
                        # if Type == 'VA':
                        #     for child in object.getchildren():
                        #         condition_photos.append(child.tag)
                        # if row[6] is None:
                        #     arcpy.AddMessage(row[7])
                        if row[6] == object.find('VendorTrackerID').text:
                            if Type == 'VA':
                                d_element = object.find('WorkCategory')
                                if d_element.text != 'NOINSPECT':
                                    d_element.text = 'SAFETYEX'
                            for child in object.getchildren():
                                if child.tag == 'WorkResults':
                                    # Adding any all condition codes in the table with the asscoiated work result
                                    # CONDITON CODE
                                    if row[1] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        parentid = str(resultId_counter)
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        if (row[1]  != 'STUBO2' and row[1] != 'STUBU2' and row[1] != 'GO95STUB') and  any(ext in (row[1]) for ext in numbers):
                                            print row[1]
                                            code = row[1][:-1]
                                            element3.text = code
                                        else:
                                            # dictionary with Condition global id as key and condition remark as value

                                            element3.text = (row[1])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(120)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')

                                    # CONDITION_DATE
                                    if row[9] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        oldtime = row[9]
                                        now_formatted = oldtime.strftime('%Y%m%d')
                                        element3.text = str((now_formatted))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(122)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_DATE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')
                                    # #CONDITION_IDN
                                    # element = ET.SubElement(child, 'WorkResult')
                                    # element7 = ET.SubElement(element, 'ParentResultID')
                                    # element7.text = parentid
                                    # element1 = ET.SubElement(element, 'ResultID')
                                    # resultId_counter += 1
                                    # element1.text = (resultId_counter)
                                    # element2 = ET.SubElement(element, 'ResultValue')
                                    # element3 = ET.SubElement(element2, 'Value')
                                    # element3.text = (row[9])
                                    # worktaskId_counter += 1
                                    # element4 = ET.SubElement(element, 'WorkTaskID')
                                    # element4.text = (worktaskId_counter)
                                    # element5 = ET.SubElement(element, 'WorkTaskName')
                                    # element5.text = ('CONDITION_IDN')
                                    # element6 = ET.SubElement(element, 'WorkTaskType')
                                    # element6.text = ('OUT_CONDITION')

                                    # CONDITION_Remarks
                                    if row[1] == 'CUTOUTAR' and row[2] == 'D':
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = 'Porcelain Cutout'
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(123)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_REMARKS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')
                                    elif row[3] is not None :
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        if str(row[1]) in ('COOTHER', 'COFIBER', 'COTVEYE', 'COTELCO') and row[5] is not None:
                                            element3.text = str(row[5])
                                        else:
                                            element3.text = (condition_code_dict[row[1]])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(123)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_REMARKS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')

                                        # CONDITION_REMARKS
                                    elif row[3] is None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')

                                        if str(row[1]) in ('COOTHER', 'COFIBER', 'COTVEYE', 'COTELCO') and row[5] is not None:
                                            element3.text = str(row[5])
                                        else:
                                            element3.text = (condition_code_dict[row[1]])

                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(123)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_REMARKS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')

                                    # CONDITION_STATUS
                                    if row[4] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (row[4])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(125)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_STATUS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')
                                    # STATUS_REMARK
                                    if row[5] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (row[5])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(126)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('STATUS_REMARK')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')
                                    # CONDITION_PRIORITY_CODE
                                    if row[2] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (row[2])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(121)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_PRIORITY_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')

                                        # # adding photo for priority A
                                        # if row[2] == 'A' and row[7] in ccondtionphotodict.keys():
                                        #     # condition_code_dict[row[1]]
                                        #     # arcpy.AddMessage("ConditionPhoto")
                                        #     element8 = ET.SubElement(element, 'PhotoFileName')
                                        #     element8.text = ccondtionphotodict[row[7]]
                                # if Type == 'VA':
                                #     if 'PhotoDocumentations' not in condition_photos:
                                #         photo_element = ET.SubElement(object, 'PhotoDocumentations')
                                #         for key, value in ccondtionphotodict.iteritems():
                                #             if key == row[7] and key in photodescription.keys():
                                #                 # arcpy.AddMessage('added photo')
                                #                 element = ET.SubElement(child, 'PhotoDocumentation')
                                #                 element1 = ET.SubElement(element, 'PhotoFileName')
                                #                 element1.text = value
                                #                 element2 = ET.SubElement(photo_element, 'PhotoDescription')
                                #                 element2.text = photodescription[key]
                                #                 element3 = ET.SubElement(element, 'PhotoType')
                                #                 element3.text = 'Conditions'



                                if child.tag == 'PhotoDocumentations':
                                    for key, value in ccondtionphotodict.iteritems():
                                        if key == row[7] and key in photodescription.keys():
                                            # arcpy.AddMessage('added photo')
                                            element = ET.SubElement(child, 'PhotoDocumentation')
                                            element1 = ET.SubElement(element, 'PhotoFileName')
                                            element1.text = value
                                            element2 = ET.SubElement(element, 'PhotoDescription')
                                            element2.text = photodescription[key]
                                            element3 = ET.SubElement(element, 'PhotoType')
                                            element3.text = 'Conditions'
        with arcpy.da.SearchCursor(sourceCondition, sourceConditionFields) as cursor:
            for row in cursor:
                if row[6] in source_condition_globals and row[4] != 'ABM':

                    if row[2] in ('A', 'B') and row[1] != 'GRDBROKE' and row[1] != 'XFRMUGRU':

                        photodescription[row[7]] = (condition_code_dict[row[1]])
                    for object in root.iter('Object'):
                        # if row[6] is None:
                        #     arcpy.AddMessage(row[7])
                        if row[6] == object.find('VendorTrackerID').text:
                            if Type == 'VA':
                                d_element = object.find('WorkCategory')
                                if d_element.text != 'NOINSPECT':
                                    d_element.text = 'SAFETYEX'
                            for child in object.getchildren():
                                if child.tag == 'WorkResults':
                                    # Adding any all condition codes in the table with the asscoiated work result
                                    # CONDITON CODE
                                    if row[1] is not None and row[1] != '':
                                        element = ET.SubElement(child, 'WorkResult')
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        parentid = str(resultId_counter)
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        if (row[1]  != 'STUBO2' and row[1] != 'STUBU2' and row[1] != 'GO95STUB') and any(ext in (row[1]) for ext in numbers):
                                            print row[1]
                                            code = row[1][:-1]
                                            element3.text = code
                                        else:
                                            # dictionary with Condition global id as key and condition remark as value

                                            element3.text = (row[1])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(120)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')

                                    # CONDITION_DATE
                                    if row[9] is not None and row[9] != '':
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        #oldtime = row[9]
                                        #now_formatted = oldtime.strftime('%Y%m%d')
                                        element3.text = str((row[9]))
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(122)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_DATE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')
                                    # #CONDITION_IDN
                                    if row[10] is not None:

                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str(resultId_counter)
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = str(row[10])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(124)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_IDN')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')

                                    # CONDITION_Remarks
                                    if row[1] == 'CUTOUTAR' and row[2] == 'D':

                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = 'Porcelain Cutout'
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(123)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_REMARKS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')
                                    elif row[3] is not None:

                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        if str(row[1]) in ('COOTHER', 'COFIBER', 'COTVEYE', 'COTELCO') and row[5] is not None:
                                            element3.text = str(row[5])
                                        else:
                                            element3.text = (condition_code_dict[row[1]])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(123)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_REMARKS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')

                                        # CONDITION_REMARKS
                                    elif row[3] is None:

                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')

                                        if str(row[1]) in ('COOTHER', 'COFIBER', 'COTVEYE', 'COTELCO') and row[5] is not None:
                                            element3.text = str(row[5])
                                        else:
                                            element3.text = (condition_code_dict[row[1]])

                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(123)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_REMARKS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')

                                    # CONDITION_STATUS
                                    if row[4] is not None and row[4] != '':
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = str(row[4])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(125)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_STATUS')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')
                                    # STATUS_REMARK
                                    if row[4] is not None:
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        if row[4] == 'PRIORITYCHG':
                                            change = str(row[11]) + '2' + str(row[2])
                                            element3.text = change
                                        else:
                                            element3.text = str(row[4])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(126)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('STATUS_REMARK')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')
                                    # CONDITION_PRIORITY_CODE
                                    if row[2] is not None and row[2] != '':
                                        element = ET.SubElement(child, 'WorkResult')
                                        element7 = ET.SubElement(element, 'ParentResultID')
                                        element7.text = parentid
                                        element1 = ET.SubElement(element, 'ResultID')
                                        resultId_counter += 1
                                        element1.text = str((resultId_counter))
                                        element2 = ET.SubElement(element, 'ResultValue')
                                        element3 = ET.SubElement(element2, 'Value')
                                        element3.text = (row[2])
                                        worktaskId_counter += 1
                                        element4 = ET.SubElement(element, 'WorkTaskID')
                                        element4.text = str(121)
                                        element5 = ET.SubElement(element, 'WorkTaskName')
                                        element5.text = ('CONDITION_PRIORITY_CODE')
                                        element6 = ET.SubElement(element, 'WorkTaskType')
                                        element6.text = ('OUT_CONDITION')

                                        # adding photo for priority A
                                        # if row[2] == 'A' and row[7] in sourceConditionPhotodict.keys():
                                        #     # condition_code_dict[row[1]]
                                        #     # arcpy.AddMessage("ConditionPhoto")
                                        #     element8 = ET.SubElement(element, 'PhotoFileName')
                                        #     element8.text = sourceConditionPhotodict[row[7]]
                                if child.tag == 'PhotoDocumentations':
                                    for key, value in sourceConditionPhotodict.iteritems():
                                        if key == row[7] and key in photodescription.keys():
                                            # arcpy.AddMessage('added photo')
                                            element = ET.SubElement(child, 'PhotoDocumentation')
                                            element1 = ET.SubElement(element, 'PhotoFileName')
                                            element1.text = value
                                            element2 = ET.SubElement(element, 'PhotoDescription')
                                            element2.text = photodescription[key]
                                            element3 = ET.SubElement(element, 'PhotoType')
                                            element3.text = 'Conditions'

        for object in root.iter('WorkTaskID'):
            if object.text == '292':
                object.text = ('123')

        # arcpy.AddMessage('Remove Conditions')
        # Getting rid of Removed Conditions
        removecounter2 = 0
        fp_removed = 0
        # arcpy.AddMessage(removecounter2)
        while removecounter2 != 10:

            for child in root:
                if child.tag == ('Objects'):
                    for child2 in child:
                         for child3 in child2:

                            # print child2.find('WorkCategory').text
                            if child3.tag == 'WorkResults':
                                for child4 in child3:
                                    for child5 in child4:
                                        # Leave this in or take this out based on what kyle wants
                                        if child5.tag == 'WorkTaskType':
                                            if child5.text == 'OUT_CONDITION' and (child2.find(
                                                    'WorkCategory').text == 'REMOVED_FP' or child2.find(
                                                    'WorkCategory').text == 'NOINSPECT'):
                                                # print child5.text
                                                # print child2.find('WorkCategory').text
                                                child3.remove(child4)
            removecounter2 +=1

        # arcpy.AddMessage('Remove VA')
        # Remove Extraneous for VA
        if Type == 'VA':
            removecounter3 = 0
            fp_removed = 0
            while removecounter3 != 10:

                for child in root:
                    if child.tag == ('Objects'):
                        for child2 in child:
                            for child3 in child2:

                                # print child2.find('WorkCategory').text
                                if child3.tag == 'WorkResults':
                                    for child4 in child3:
                                        for child5 in child4:
                                            # Leave this in or take this out based on what kyle wants
                                            if child5.tag == 'WorkTaskName':
                                                if child5.text in ['DECAY_LOCATION_CODE', 'POLE_HEIGHT',
                                                                   'POLE_TOP_CONDITION_CODE',
                                                                   #'GPS_QUALITY_IND', 'LONGITUDE', 'LATITUDE',
                                                                   #'GPS_MEAS_TAKEN',
                                                                   'MULTIPLE_CIRCUIT_INDICATOR', 'CIRCUIT_ID',
                                                                   'MANUFACTURER_TREATMENT_CODE',
                                                                   'POLE_COMPOSITION_CODE', 'POLE_STUBBING_CODE',
                                                                   'POLE_CLASS_CODE',
                                                                   'YEAR_INSTALLED', 'GROUND_LINE_CONDITION_CODE',
                                                                   'FACILITY_ADDRESS']:
                                                    child3.remove(child4)
                removecounter3 += 1

        # failed_counter = 0
        # while failed_counter < 10:
        #     if FailedPointsList:
        #         for child in root:
        #             if child.tag == ('Objects'):
        #                 for child2 in child:
        #                     for child3 in child2:
        #                         if child3.tag == 'AlternateObjectID':
        #                             if child3.text not in FailedPointsList:
        #                                 child.remove(child2)
        #     failed_counter +=1

        # arcpy.AddMessage(fp_removed)

        # counts the totoal poles and changes NumWorkItems to that number

        totalpoles = 0
        for object in root.iter('Object'):
            if object.tag == 'Object':
                totalpoles += 1
        #
        for object in root.iter('NumWorkItems'):
            object.text = str(totalpoles)
            # arcpy.AddMessage('NumWorkItems')
            # arcpy.AddMessage(object.text)
        arcpy.AddMessage('Total Poles = {}'.format(totalpoles))
        for object in root.iter('PriorWorkSetFlag'):
            object.text = 'N'
        for object in root.iter('WorkAreaID'):
            object.text = WorkAreaIDtext
        for object in root.iter('WorkMap'):
            object.text = WorkMaptext
        for object in root.iter('WorkMapSection'):
            object.text = WorkMapSectiontext
        for object in root.iter('WorkSetID'):
            object.text = WorkSetIDtext

        for object in root.iter('StateAbbrv'):
            object.text = StateAbbrvtext

        for object in root.iter('WorkSetCategory'):
            object.text = str(Type)

        # now = datetime.datetime.now()
        # now_formatted = now.strftime('%Y%m%d%H%M%S')
        # #tree.write(r'C:\Pacificorp\from_pacificorp\fpi_a_data_{0}_{1}.xml'.format('test','test'))
        # name = os.path.join(path, 'fpi_a_data_{0}_{1}.xml'.format(str(WorksetID), now_formatted))
        # arcpy.AddMessage(WorksetID)
        # tree.write(r'C:\Pacificorp\from_pacificorp\fpi_a_data_{0}_{1}.xml'.format(str(WorksetID), now_formatted))
        tree.write(name)
        arcpy.AddMessage('{} have been created'.format(name))
        arcpy.AddMessage('------------------------------------------------------------------------------------------------')

        # data = ExcelDelivery.dataextraction(database, mapstring_section)
        # ExcelDelivery.create_excel(data, xmlfolder,mapstring_section)
