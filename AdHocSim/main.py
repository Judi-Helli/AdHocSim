import math
import sys  # This module is used to get both the argv[] list and the exit() function which terminates the program
# when needed.
import operator  # This module used with the attrgettter() function to get an attribute of an object as a key.

# Essential variables declaration
ps = int(sys.argv[1])
np = -1
ds = -1.0
packetsCounter = 0
secondsCounter = 0
commandsList = []
currentCommand = []
nodesList = []
neighboursDict = {}
routesList = []
indentation = '\t\t '  # indentation to seperate the time stamp from the results


# This class forms the node object including its data.
class Node:
    def __init__(self, label, location, transmissionRange, battery):
        self.label = label
        self.location = location
        self.transmissionRange = transmissionRange
        self.battery = battery


# This class forms the route between source and destination, stores the list of routing nodes and find its cost by
# its internal methods.
class Route:
    def __init__(self, route):
        self.route = route #one route between source and destination.
        self.totalCost = self.totalCost() #the cost of this route.

    #The used methods to calculate the cost
    def distance(self, i, j):
        return math.sqrt((i.location['x'] - j.location['x']) ** 2 + (i.location['y'] - j.location['y']) ** 2)

    def cost(self, i, j):
        return self.distance(i, j) / j.battery

    def totalCost(self):
        totalCost = 0
        for iIndex in range(len(self.route) - 1):
            i = self.route[iIndex]
            j = self.route[iIndex + 1]
            totalCost += self.cost(i, j)
        return totalCost


# This function loads the commands file from the disc to memory (from commands.txt file to commandsList),
# storing a list of commands, knowing that each command includes a list of arguments.
def loadFile(fileName):
    global commandsList
    with open(fileName) as commandsFile:
        for line in commandsFile:
            command = line.split('\t')
            commandsList.append(command)


# A util function used to find a node by its label attribute, since we are dealing with objects(addresses in the memory
# and label is just a part(attribute) of that object).
def findNode(targetLabel):
    for node in nodesList:
        if node.label == targetLabel:
            return node


# This function creates a new node if there is no one with the same label.
def crnode(label, location, transmissionRange, battery):
    # Converting the location and transmission range data format to dictionaries, in order to make it easier to
    # understand
    if findNode(targetLabel=label) is not None:
        print('This node already exist!')
        return

    location = location.split(';')
    locationDict = {}
    locationDict['x'] = int(location[0])
    locationDict['y'] = int(location[1])
    transmissionRange = transmissionRange.split(';')
    transmissionRangeDict = {}
    transmissionRangeDict['x1'] = int(transmissionRange[0])
    transmissionRangeDict['x2'] = int(transmissionRange[1])
    transmissionRangeDict['y1'] = int(transmissionRange[2])
    transmissionRangeDict['y2'] = int(transmissionRange[3])
    battery = int(battery)

    newNode = Node(label, locationDict, transmissionRangeDict, battery)  # a node object

    nodesList.append(newNode)
    print('COMMAND *CRNODE*: New node %s is created' % label)


# This function initializes the packet sending operation between the source and destination if any route esists.
# here we find calculate the number of packets and send the firs one.
def send():
    discoverNeighbours()
    discoverRoutes(source=source,
                   destination=destination,
                   route=[], visited=set())
    if routesList is not None:
        print("COMMAND *SEND*: Data is ready to send from %s to %s" % (source.label, destination.label))
        global np, ds, ps
        np = math.ceil(ds / ps)
        updatePacketStatus()
        updateRoutingStatus()
    else:
        print("NO ROUTE FROM %s TO %s FOUND." % (source.label, destination.label))
        print('********************************\nAD-HOC NETWORK SIMULATOR -  END\n********************************')
        sys.exit()


# This function changes the location of a node after making sure that it is really exists.
def move(node, newLocation):
    print(end=indentation)
    if node is None:
        print("This node does not exist!")
        return
    newLocation = newLocation.split(';')
    newLocationDict = {}
    newLocationDict['x'] = int(newLocation[0])
    newLocationDict['y'] = int(newLocation[1])
    node.location = newLocationDict
    print('COMMAND *MOVE*: The location of node %s is changed' % node.label)


# This function changes the battery of a node after making sure that it really exists.
def chbttry(node, newBattery):
    print(end=indentation)
    if node is None:
        print("This node does not exist!")
        return
    newBattery = int(newBattery)
    node.battery = newBattery
    print('COMMAND *CHBTTRY*: Battery level of node %s is changed to %d' % (node.label, node.battery))


# This function is used to remove a node from the nodes list after making sure that it is really exists.
def rmnode(node):
    global nodesList
    print(end=indentation)
    if node is None:
        print("This node already does not exist!")
        return
    nodesList.remove(node)

    print('COMMAND *RMNODE*: Node %s is removed' % node.label)



# this function discovers the neighbours of each node considering their transmission range.
# the used data structure is a dictionary of objects (neighboursDict).
def discoverNeighbours():
    global nodesList, neighboursDict
    for n1 in nodesList:
        n1Neighbours = []
        for n2 in nodesList:
            if n1 is not n2:
                x1Point = n1.transmissionRange['x1'] + n1.location['x']
                y1Point = n1.transmissionRange['y1'] + n1.location['y']
                x2Point = n1.location['x'] - n1.transmissionRange['x2']
                y2Point = n1.location['y'] - n1.transmissionRange['y2']
                if x2Point <= n2.location['x'] <= x1Point and y2Point <= n2.location['y'] <= y1Point:
                    n1Neighbours.append(n2)
        neighboursDict[n1] = n1Neighbours


# This function discovers the available routes from source to destination using the dfs(depth first search) algorithm.
# a pre-condition of using this function is discovering the neighbours of the nodes in the network.
def discoverRoutes(source, destination, route, visited):
    global routesList, neighboursDict
    visited.add(source)
    route.append(source)

    if source == destination:
        routesList.append(Route(route.copy()))
    else:
        for neighbour in neighboursDict[source]:
            if neighbour not in visited:
                discoverRoutes(neighbour, destination, route, visited)

    route.pop()
    visited.remove(source)


# This function gets the the totalCost attribute from each route object and returns the route object which has the minimum cost.
#returns a Route object
def findOptimalRoute():
    return min(routesList, key=operator.attrgetter('totalCost'))


# This function is used to update and show the routinf details, knowing that route discovering depends on the neighbours
# of the node, so we start by discovering the neighbours of each node then discovering the routes and finally showing the results.
def updateRoutingStatus():
    global routesList, source, destination
    discoverNeighbours()
    routesList = []
    discoverRoutes(source=source, destination=destination, route=[], visited=set())

    print(end=indentation)
    if routesList is None:
        print('NO ROUTE FROM %s TO %s FOUND.' % (source.label, destination.label))
        sys.exit()

    optimalRoute = findOptimalRoute()
    print('NODES & THEIR NEIGHBORS:', end='')
    for node in nodesList:
        print('%s ->' % node.label, end=' ')
        print(",".join([neighbour.label for neighbour in neighboursDict[node]]), end=' | ')
    print()

    print(end=indentation)
    routesNumber = len(routesList)
    print('%d ROUTE(S) FOUND:' % routesNumber)

    for routeIndex in range(routesNumber):
        print(end=indentation)
        print('ROUTE %d:' % (routeIndex + 1), end=' ')
        aRoute = routesList[routeIndex].route
        aCost = routesList[routeIndex].totalCost
        print('->'.join([node.label for node in aRoute]), 'COST: %.4f' % aCost)

    optimalRouteIndex = routesList.index(optimalRoute)
    print(end=indentation)

    print('SELECTED ROUTE (ROUTE %d):' % (optimalRouteIndex + 1), end='')
    print('->'.join([node.label for node in optimalRoute.route]))


# this function is used to simulate the packet and show its updated status.
def updatePacketStatus():
    global packetsCounter
    global ds

    if ds < ps:
        ds = 0
    else:
        ds -= ps
    packetsCounter += 1
    print(end=indentation)
    print('PACKET %d HAS BEEN SENT' % packetsCounter)
    print(end=indentation)
    print('REMAINING DATA SIZE: %.1f BYTE' % ds)


# This fumction is to convert the seconds counter into a time stamp of hh:mm:ss format.
def showTimer(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    print("SIMULATION TIME: %02d:%02d:%02d" % (hour, minutes, seconds))


# This function sets up the network nodes and initializes the simulator after applying the crnode and  send  commands.
def configureNetwork():
    global currentCommand, secondsCounter

    if commandsList:
        currentCommand = commandsList[0]
    showTimer(secondsCounter)
    while int(currentCommand[0].strip()) == 0:
        print(end=indentation)
        if currentCommand[1].strip() == 'CRNODE':
            crnode(label=currentCommand[2].strip(), location=currentCommand[3].strip(),
                   transmissionRange=currentCommand[4].strip(), battery=currentCommand[5].strip())
        elif currentCommand[1].strip() == 'SEND':
            global ds, source, destination
            source = findNode(targetLabel=currentCommand[2].strip())
            destination = findNode(targetLabel=currentCommand[3].strip())
            ds = float(currentCommand[4].strip())
            send()
        else:
            print("Not a configuration command!")

        del commandsList[0]
        if commandsList:
            currentCommand = commandsList[0]
    secondsCounter += 1


# This is the main function that implements the commands in the file and controls the flow of the simulator
def AdHocSim():
    global secondsCounter, currentCommand
    print('********************************\nAD-HOC NETWORK SIMULATOR - BEGIN\n********************************')
    loadFile('commands.txt')
    configureNetwork()
    while ds != 0.0:
        showTimer(secondsCounter)

        if commandsList and int(currentCommand[0].strip()) == secondsCounter:
            if currentCommand[1].strip() == 'CRNODE':
                crnode(label=currentCommand[2].strip(), location=currentCommand[3].strip(),
                       transmissionRange=currentCommand[4].strip(), battery=currentCommand[5].strip())
            elif currentCommand[1].strip() == 'MOVE':
                move(node=findNode(targetLabel=currentCommand[2].strip()), newLocation=currentCommand[3].strip())
            elif currentCommand[1].strip() == 'CHBTTRY':
                chbttry(node=findNode(targetLabel=currentCommand[2].strip()), newBattery=currentCommand[3].strip())
            elif currentCommand[1].strip() == 'RMNODE':
                rmnode(node=findNode(targetLabel=currentCommand[2].strip()))
            else:
                print(end=indentation)
                print('Not a valid command!')
            updatePacketStatus()
            updateRoutingStatus()

            del commandsList[0]
            if commandsList:
                currentCommand = commandsList[0]
        else:
            updatePacketStatus()

        secondsCounter += 1

    print('********************************\nAD-HOC NETWORK SIMULATOR -  END\n********************************')



# starting the simulator
AdHocSim()
