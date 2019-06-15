
from win32api import GetSystemMetrics
from comtypes.client import CreateObject
from comtypes.gen import STKObjects
from comtypes import COMError

from toolbox import TLE_Manager, Toolbox

__author__ = "W. Conor McFerren"
__maintainer__ = "W. Conor McFerren"
__email__ = "cnmcferren@gmail.com"


class AreaTarget:
   
    def __init__(self, scenario, name=None, coordList = None, parsedLine=None):
        """

        Creates an AreaTarget object that holdsthe reference for area targets
        to be added to the scenario.

        Parameters:
            scenario (STKObjects.IAgScenario): Scenario for the area target
            to be placed in.
            parsedLine (list): Line parsed from the Target List.
            name (str): Name of the satellite
            coordList (list): List of coordinate points in the following form:
            [(lat0,lon0),(lat1,lon1),...(latN,lonN)].

        """
        self.__guardian = scenario
        
        self.root = self.__guardian.GetGuardian().root
        if not parsedLine == None:
        
            self.root.BeginUpdate()
        
            self.ID = parsedLine[1]
            startLat = parsedLine[8]
            startLon = parsedLine[9]
            endLat = parsedLine[10]
            endLon = parsedLine[11]

            points = [(startLat,startLon),
                      (startLat,endLon),
                      (endLat,endLon),
                      (endLat,startLon)]
            
            self.center =Toolbox.ComputeCenterTarget(points)

            self.__areaTarget = self.root.CurrentScenario.Children.New(STKObjects.eAreaTarget,self.ID)
            self.__areaTarget = self.__areaTarget.QueryInterface(STKObjects.IAgAreaTarget)
            self.__areaTarget.AreaType = STKObjects.ePattern
            self.__patterns = self.__areaTarget.AreaTypeData
            self.__patterns = self.__patterns.QueryInterface(STKObjects.IAgAreaTypePatternCollection)
        
            self.__patterns.Add(points[0][0],points[0][1])
            self.__patterns.Add(points[1][0],points[1][1])
            self.__patterns.Add(points[2][0],points[2][1])
            self.__patterns.Add(points[3][0],points[3][1])
            self.__areaTarget.AutoCentroid = True
        
            self.root.EndUpdate()
            
        elif not name == None and not coordList == None:
            
            for i in range(len(coordList)):
                coordList[i] = coordList[i].split(',')
                coordList[i][0] = float(coordList[i][0])
                coordList[i][1] = float(coordList[i][1])
                
            self.root.BeginUpdate()
            
            self.ID = name
            
            self.__areaTarget = self.root.CurrentScenario.Children.New(STKObjects.eAreaTarget,self.ID)
            self.__areaTarget = self.__areaTarget.QueryInterface(STKObjects.IAgAreaTarget)
            self.__areaTarget.AreaType = STKObjects.ePattern
            self.__patterns = self.__areaTarget.AreaTypeData
            self.__patterns = self.__patterns.QueryInterface(STKObjects.IAgAreaTypePatternCollection)
            
            for point in coordList:
                self.__patterns.Add(point[0],point[1])
                
            self.__areaTarget.AutoCentroid = True
            
            self.center = Toolbox.ComputeCenterTarget(coordList)
            
            self.root.EndUpdate()
    
    def SetElevationConstraint(self, angle):
        """

        Adds elevation constraint for access.
    
        Parameters:
            angle (float or str): Angle of constraint (measured from horizon).
        

        """ 

        self.root.ExecuteCommand("SetConstraint " + \
                                 "*/AreaTarget/" + str(self.ID) + \
                                 " ElevationAngle " + str(float(angle)))
    
    def GetTarget(self):
        """

        Returns the reference to the area target object.

        Returns:
            self.__areaTarget: The reference to the area target objects.

        """

        return self.__areaTarget

    def GetPatterns(self):
        """

        Returns the patterns for the area target objects.

        Returns:
            self.__patterns: The reference to the patterns

        """
        
        return self.__patterns

    def GetGuardian(self):
        """

        Returns the guardian of the class (the scenario).

        Returns:
            self.__guardian: The scenario the area target is in.

        """

        return self.__guardian

class Camera:

    def __init__(self, hostSat, name, fov):    
        """

        The camera that can be added to a satellite object.

        Parameters:
            hostSat (STKObjects.eSatellite): The satellite that the camera is to be attached to.
            name (str): A new and unique name of the camera.
            fov (list): A list containing the field of view width and height.

        """

        self.__guardian = hostSat
        
        if not ((type(fov[0]) == int or type(fov[0]) == float) and
                (type(fov[1]) == int or type(fov[1]) == float)):
            raise TypeError, "Field of View parameters of invalid type."
        
        self.root = self.__guardian.GetGuardian().GetGuardian().root
        
        self.root.BeginUpdate()
        
        self.__cameraGen = self.__guardian.GetReference().Children.New(20,name)
        self.__camera = self.__cameraGen.QueryInterface(STKObjects.IAgSensor)
        self.__camera.CommonTasks.SetPatternRectangular(fov[0],fov[1])
        
        self.root.EndUpdate()

    def GetAccess(self, areaTarget):
        #TODO Add multiple area target access computation for satellite.
        """

        Computes the access to an area target with the camera during the time
        interval of the scenario. 

        Parameters:
            areaTarget (STKObjects.IAgAreaTarget): The area target that access
                                            is to be computed to.

        Returns:
            comptuedIntervals: An array containing the start and end time of
                        all passes within the scenario's time interval.

        """

        self.root.BeginUpdate()

        access = self.__cameraGen.GetAccessToObject(areaTarget.GetTarget())
        access.ComputeAccess()
        intervalCollection = access.ComputedAccessIntervalTimes
        try:
            computedIntervals = intervalCollection.ToArray(0,-1)
            self.root.EndUpdate()

            return computedIntervals
        except:
            self.root.EndUpdate()

            return 0

    def GetCamera(self):
        """

        Returns the reference to the camera.

        Returns: 
            self.__camera: Returns the camera of type STKObjects.IAgSensor.

        """
        return self.__camera
    
    def GetCameraGen(self):
        """

        Returns the general camera.

        Returns:
            self.__cameraGen: The camera but of a general type.

        """

        return self.__cameraGen

    def GetGuardian(self):     
        """

        Returns the guardian of the camera.

        Returns
            self.__guardian: The satellite that is the guardian of the camera.

        """
        
        return self.__guardian

class Satellite:

    def __init__(self, scenario, name, sscNumber,StartTime=None,StopTime=None):
        """

        Creates a satellite to be added to the scenario
    
        Parameters:
            scenario (STKObjects.IAgScenario): The scenario that the satellite will be placed in.
            name (str): The unique name of the satellite.
            sscNumber (str or int): The SSC Number of the satellite to model the orbit of.

        """
        
        self.__guardian = scenario
        self.name = name

        self.root = self.__guardian.GetGuardian().root

        TLE_Manager.GenerateTLE(self.root, str(sscNumber))
        self.tle = TLE_Manager.ParseTLE(str(sscNumber) + ".tle")
        if StartTime == None:
            StartTime = self.__guardian.GetReference().StartTime
        if StopTime == None:
            StopTime = self.__guardian.GetReference().StopTime
            
        try:
            self.__satellite = self.root.CurrentScenario.Children.New(STKObjects.eSatellite, name)
        except COMError:
            raise (RuntimeError,'\nIncorrect name format or name already taken for satellite.' + 
                  ' Please do not use spaces or reuse satellite names.')
            
        try:
            self.root.ExecuteCommand('SetState */Satellite/' + self.name + ' TLE "' +
                                     self.tle[0] + '" "' + self.tle[1] +
                                     '" TimePeriod "' +
                                     StartTime + '" "' +
                                     StopTime + '"')
        except COMError:
            raise (RuntimeError, "Failure to add satellite. Check formatting of TLE.")

    def ComputeKeplerians(self, timeInstant):
        """

        Computes the Keplerian parameters for the satellite at a time instant.
        
        Parameters:
            timeInstant (str): The time instant for the Keplerians to be computed
                            in the format that STK provides.

        """
        
        ##TODO: Check time is in correct 24hr clock format
        
        satDPSingle = self.__satellite.DataProviders.Item('Classical Elements')
        satDPSingle = satDPSingle.QueryInterface(STKObjects.IAgDataProviderGroup)
        ceicrf = satDPSingle.Group.Item('ICRF')
        ceicrf = ceicrf.QueryInterface(STKObjects.IAgDataPrvTimeVar)

        result = ceicrf.ExecSingle(timeInstant)

        time = result.DataSets.GetDataSetByName('Time').GetValues()
        sma = result.DataSets.GetDataSetByName('Semi-major Axis').GetValues()
        ecc = result.DataSets.GetDataSetByName('Eccentricity').GetValues()
        inc = result.DataSets.GetDataSetByName('Inclination').GetValues()
        raan = result.DataSets.GetDataSetByName('RAAN').GetValues()
        aop = result.DataSets.GetDataSetByName('Arg of Perigee').GetValues()
        trueAnomaly = result.DataSets.GetDataSetByName('True Anomaly').GetValues()

        arr = [time,sma,ecc,inc,raan,aop,trueAnomaly]
        
        return arr

    def GetAccess(self, areaTargets):    
        """

        Computes access to the area target provided over the time interval of the scenario.
        
        Parameters:
            areaTarget (AreaTarget): The area target to compute access to.
            
        Returns:
            computedIntervals (list): The time intervals of the access times.

        """
        
        #If it is a single areaTarget.
        #TODO add name to end of all accesses for single area target
        if not isinstance(areaTargets,list):
            self.root.BeginUpdate()

            access = self.__satellite.GetAccessToObject(areaTargets.GetTarget())
            access.ComputeAccess()

            intervalCollection = access.ComputedAccessIntervalTimes
            
            try:
                computedIntervals = intervalCollection.ToArray(0,-1)
                self.root.EndUpdate()

                return computedIntervals
            except Exception:
                self.root.EndUpdate()

                return 0
            
        #If it is a list of areaTargets.
        else:
            accessArrays = []
            self.root.BeginUpdate()
            
            #Iterate each area target
            for areaTarget in areaTargets:
                access = self.__satellite.GetAccessToObject(areaTarget.GetTarget())
                access.ComputeAccess()

                intervalCollection = access.ComputedAccessIntervalTimes
            
                try:
                    computedIntervals = intervalCollection.ToArray(0,-1)
                    for line in computedIntervals:
                        line = line + (areaTarget.ID,)
                        accessArrays.append(line)
                    
                except Exception as e:
                    print(e.message)
                    pass
                
            self.root.EndUpdate()
            return Toolbox.SortAllAccess(accessArrays)

    def ComputeDSInfo(self, areaTarget, passArray):
        """

        Computes the information for the dynamic simulations.
        
        Parameters:
            areaTarget (AreaTarget): The area target that is going to be used 
                                in the dynamic simulations.
            passArray (list): The list that contains the start and end time
                                for a pass over the given area target.

        Returns:
            List in the following format:
                [areaTarget.ID, areaTarget.center, keplerians, (startTime, endTime)]

        """
        #TODO Make sure computing DS info still works with name

        startTime = passArray[0]
        endTime = passArray[1]

        keplerians = self.ComputeKeplerians(startTime)

        return [areaTarget.ID, areaTarget.center, keplerians, (startTime, endTime)]


        keplerians = self.ComputeKeplerians(startTime)

        return [areaTarget.ID, areaTarget.center, keplerians, (startTime, endTime)]

    def GetReference(self):
        """

        Get reference to the satellite.

        Returns:
            self.__satellite: Returns the reference to the STKObjects.eSatellite.

        """
        
        return self.__satellite

    def GetGuardian(self):       
        """

        Returns the guardian of the satellite object (the scenario).
        
        Returns:
            self.__guardian: The scenario that the satellite is in.

        """
        return self.__guardian
