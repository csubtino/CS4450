#!/usr/bin/python

import math

class Node:
   def __init__(self, point = None):
      self.Value = point
      self.Children = []

   def AddChild(self, node):
      if not type(node) is Node:
         raise TypeError("Not a node")
      self.Children.append(node)
      self.Value = None
      
   def GetValues(self):
      if self.Value != None:
         return [self.Value]
      return [v for c in self.Children for v in c.GetValues()]

   def MinDistance(self, node):
      if not type(node) is Node:
         raise TypeError("Not a node")

      a_values = self.GetValues()
      b_values = node.GetValues()

      min_dist = -1
      for a in a_values:
         for b in b_values:
            dist = a.Euclidean(b)
            if dist < min_dist or min_dist < 0:
               min_dist = dist

      return min_dist

class Point:
   def __init__(self, xabs, yabs):
      self.XAbs = xabs
      self.YAbs = yabs
      self.X = 0
      self.Y = 0
      
   def Normalize(self, xmin, xmax, ymin, ymax):
      if xmax == xmin or ymax == ymin:
         raise Error("Division by zero")
      self.X = (self.XAbs - xmin)/(xmax - xmin)
      self.Y = (self.YAbs - ymin)/(ymax - ymin)

   def Euclidean(self, b):
      if not type(b) is Point:
         raise TypeError("Not a point")
      return math.sqrt(math.pow(self.X - b.X, 2) + math.pow(self.Y - b.Y, 2))
   
class Cluster:
   def __init__(self):
      self.Root = Node()
      
   def Add(self, node):
      self.Root.AddChild(node)
      
   def Normalize(self):
      values = self.GetValues()
      x_list = [a.XAbs for a in values]
      y_list = [a.YAbs for a in values]
      
      xmin = min(x_list)
      xmax = max(x_list)
      ymin = min(y_list)
      ymax = max(y_list)
      
      any(a.Normalize(xmin, xmax, ymin, ymax) for a in values)
   
   def GetValues(self):
      return self.Root.GetValues()
   
   def BuildMatrix(self):

      self.Proximity = [[0.0 for x in range(len(self.Root.Children))] for x in range(len(self.Root.Children))]

      for i in range(len(self.Root.Children)):
         for j in range(i + 1, len(self.Root.Children)):
            self.Proximity[i][j] = self.Root.Children[i].MinDistance(self.Root.Children[j])

   def PrintProximity(self):
      for i in range(len(self.Proximity)):
         for j in range(len(self.Proximity[i])):
            print('{:3.2f}, '.format(self.Proximity[i][j]), end='')
         print('')

   def Closest(self):
      closest = -1
      closest_i = 0
      closest_j = 0
      for i in range(len(self.Proximity)):
         for j in range(i + 1, len(self.Proximity)):
            if self.Proximity[i][j] < closest or closest < 0:
               closest_i = i
               closest_j = j
               closest = self.Proximity[i][j]
      return closest_i, closest_j

   def Shrink(self):
      i, j = self.Closest()

      node = Node()
      node.AddChild(self.Root.Children[i])
      node.AddChild(self.Root.Children[j])

      self.Root.Children = [self.Root.Children[x] for x in range(len(self.Root.Children)) if x != i and x != j]
      self.Add(node)

if __name__ == '__main__':
   with open ('lab4-data.txt') as file:
      data = [x.split('\t')[0:2] for x in file.read().splitlines()[1:]]
      
      cluster = Cluster()
      any(cluster.Add(Node(Point(float(x[0]), float(x[1])))) for x in data)
      cluster.Normalize()
      cluster.BuildMatrix()
      cluster.PrintProximity()
      print(cluster.Closest())
      cluster.Shrink()
