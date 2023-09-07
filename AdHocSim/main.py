import math
import sys

ps = sys.argv[1]

class Node:
    def __init__(self, label, location, transmissionRange, battery):
        self.label = label
        self.location = location
        self.transmissionRange = transmissionRange
        self.battery = battery
class Route:
    def __init__(self, route):
        self.route = route

    def totalCost(self):

    def cost(self,i, j):

    def distance(self,i,j):
        



def load_file(fileName):
    commandsList = []
    with open(fileName) as commandsFile:
        for line in commandsFile:
            command = line.split()
            commandsList.append(command)
    return commandsList

def isNodeInList(nodes, newNode):
    for n in nodes:
        if newNode.label == n.label:
            return True
    return False

def crnode(nodes, label, location, transmissionRange, battery):
    # Converting the location and transmission range data format to dictionaries, in order to make it easier to
    # understand

    location = location.split(';')
    locationDict = dict()
    locationDict['x'] = int(location[0])
    locationDict['y'] = int(location[1])
    transmissionRange = transmissionRange.split(';')
    transmissionRangeDict = dict()
    transmissionRangeDict['x1'] = int(transmissionRange[0])
    transmissionRangeDict['x2'] = int(transmissionRange[1])
    transmissionRangeDict['y1'] = int(transmissionRange[2])
    transmissionRangeDict['y2'] = int(transmissionRange[3])
    battery = int(battery)
    newNode = Node(label, locationDict, transmissionRangeDict, battery)# a node object

    if isNodeInList(newNode=newNode, nodes=nodes):
        print("Node %s already exists!" % newNode.label)
        return


    nodes.append(newNode)
    print('COMMAND *CRNODE*: New node %s is created' % label)

#
# def discoverNeighbours(nodes):
#     for key in nodes.keys():
#
#
#
#
# def send(source, destination, ds):
#     discoverNeighbours()
#     global ps
#     np = math.ceil(ds / ps)

def discoverNeighbours(nodes):
    nodesNeighbours = dict()
    for n1 in nodes:
        n1Neighbours = []
        for n2 in nodes:
            if n1 is not n2:
                x1Point = n1.transmissionRange['x1'] + n1.location['x']
                y1Point = n1.transmissionRange['y1'] + n1.location['y']
                x2Point = n1.location['x'] - n1.transmissionRange['x2']
                y2Point = n1.location['y'] - n1.transmissionRange['y2']
                if x2Point <= n2.location['x'] <= x1Point and y2Point <= n2.location['y'] <= y1Point:
                    n1Neighbours.append(n2)
        nodesNeighbours[n1] = n1Neighbours

    return nodesNeighbours

def discoverRoutes(source, destination, neighbours, route, visited, routes):#dfs(depth first search) algorithm
    visited.add(source)
    route.append(source)

    if source == destination:
        routes.append(Route(route.copy()))
    else:
        for neighbour in neighbours[source]:
            if neighbour not in visited:
                discoverRoutes(neighbour, destination, neighbours, route, visited, routes)

    route.pop()
    visited.remove(source)
    return routes

def findNode(nodes, targetLabel):
    for n in nodes:
        if n.label == targetLabel:
            return n

def simulator():
    commandsList = load_file('commands.txt')
    nodes = []
    seconds = 0
    aCommand = commandsList[0]
    while (int(aCommand[0]) == 0):
        if aCommand[1] == 'CRNODE':
            crnode(nodes=nodes, label=aCommand[2], location=aCommand[3],
                   transmissionRange=aCommand[4], battery=aCommand[5])
        elif aCommand[1] == 'SEND':
            # send(source=aCommand[2], destination=aCommand[3], ds=aCommand[4])
            print("Not a configuration command!")
        else:
            print("Not a configuration command!")
        del commandsList[0]
        aCommand = commandsList[0]

    nodesNeighbours = discoverNeighbours(nodes=nodes)
    routes = discoverRoutes(findNode(nodes, 'x1'), findNode(nodes, 'x9'), nodesNeighbours, route=[], visited=set(), routes=[])
    for r in routes:
        print("->", end='')
        for n in r:
            print(n.label, end='')
        print()
    print(routes)

simulator()