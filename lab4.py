#!/usr/bin/python

import math
import pygame

class Display:
   def __init__(self, frame_delay = 500):
      self.BackgroundColor = (0xff, 0xff, 0xff)
      self.LineColor = (0x0, 0x0, 0x0)
      self.FrameDelay = frame_delay
      self.Width = 800
      self.Height = 640
      
      pygame.init()
      self.Font = pygame.font.SysFont('Calibri', 16)
      self.Screen = pygame.display.set_mode((self.Width, self.Height))
 
   def Run(self, cluster, fn):
      done = False
      
      while not done:
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
               done = True
   
         fn()
         self.Screen.fill(self.BackgroundColor)
         self.DrawDendrogram(cluster.Root, pygame.Rect(20, 40, 720, 540), 0.5)
         pygame.time.wait(self.FrameDelay)
         pygame.display.flip()

   def DrawDendrogram(self, node, rect, justify):
      depth = node.Depth()
      childrenCount = len(node.GetValues())
      xmargin = 10

      midx = rect.left + (rect.width * justify)
      starty = rect.top
      endy = starty + (rect.height / depth)

      flat_startx = rect.left + (xmargin * justify)
      flat_width = rect.width - xmargin
      flat_endx = flat_startx + flat_width

      pygame.draw.lines(self.Screen, self.LineColor, False, [(midx, starty), (midx, endy)], 1);
      if depth > 1:
         pygame.draw.lines(self.Screen, self.LineColor, False, [(flat_startx, endy), (flat_endx, endy)], 1);

      consumedWidth = 0
      for i in range(len(node.Children)):
         childWeight = len(node.Children[i].GetValues())/childrenCount
         childRect = pygame.Rect(0, 0, 0, 0)
         childRect.left = flat_startx + consumedWidth
         childRect.width = flat_width * childWeight

         childRect.top = endy
         childRect.height = rect.top + rect.height - endy

         childJustify = float(i) / (len(node.Children) - 1)
         self.DrawDendrogram(node.Children[i], childRect, childJustify)
         consumedWidth += childRect.width

   #def DrawPoints(self):
   #   dw = 600
   #   dh = 600
   #   db = 10
   #   offx = 170
   #   offy = 10
   #
   #   pygame.draw.rect(self.Screen, (0x0, 0x0, 0x0), (offx, offy, dw + 2*db, dh + 2*db), 1)
   #
   #   for d in self.Points:
   #      x = d.X
   #      y = d.Y
   #      color = (0xff, 0x0, 0x0)
   #      pygame.draw.circle(self.Screen, color, (int(dw * x) + offx + db, int(dh * y) + offy + db), 5, 0)
      
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

   def Depth(self):
      if self.Value != None:
         return 1

      max_depth = 0
      for child in self.Children:
         depth = child.Depth()
         if depth > max_depth:
            max_depth = depth
      return 1 + max_depth

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

   def Depth(self):
      return self.Root.Depth()

   def Update(self):
      if len(self.Root.Children) <= 2:
         return

      self.BuildMatrix()
      self.Shrink()
   
if __name__ == '__main__':
   with open ('lab4-data.txt') as file:
      data = [x.split('\t')[0:2] for x in file.read().splitlines()[1:]]
   
   display = Display(500)
   dataCluster = Cluster()
   any(dataCluster.Add(Node(Point(float(x[0]), float(x[1])))) for x in data)
   dataCluster.Normalize()

   testCluster = Cluster()
   testCluster.Add(Node(Point(0.25, 0.25)))
   testCluster.Add(Node(Point(0.50, 0.50)))
   testCluster.Add(Node(Point(0.75, 0.75)))
   testCluster.Normalize()

   display.Run(dataCluster, dataCluster.Update)
   #display.Run(testCluster, testCluster.Update)