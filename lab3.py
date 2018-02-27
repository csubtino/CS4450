#!/usr/bin/python

import pygame
import random
import math
import os
import time
import sys

class Point:
   def __init__(self, xabs = 0, yabs = 0, xnorm = 0, ynorm = 0):
      self.XAbs = xabs
      self.YAbs = yabs
      self.Centroid = 0
      self.X = xnorm
      self.Y = ynorm

   def Normalize(self, x_min, x_max, y_min, y_max):
      self.X = (self.XAbs - x_min) / (x_max - x_min)
      self.Y = (self.YAbs - y_min) / (y_max - y_min)
      
      return self
      
class Cluster:
   def __init__(self, data, centroid_count, save_image = False, frame_delay = 500):
      self.Data = data
      self.Normalize()
      self.K = centroid_count
      self.Centroids = []
      self.CentroidsStable = False
      
      self.SaveImageOn = save_image
      self.FrameDelay = frame_delay
      
      random.seed()
      self.RandomCentroids()
      self.CentroidColors = [
         (0xff, 0x0, 0x0), 
         (0x0, 0xff, 0x0), 
         (0x0, 0x0, 0xff), 
         (0xff, 0x0, 0xff), 
         (0xff, 0xff, 0x0)
      ]
      self.CentroidColor = (0x0, 0x0, 0x0)
      self.BackgroundColor = (0xff, 0xff, 0xff)
      self.Width = 800
      self.Height = 640
      
      pygame.init()
      self.Font = pygame.font.SysFont('Calibri', 16)
      self.Screen = pygame.display.set_mode((self.Width, self.Height))
      
   def Normalize(self):
      col_x = [d.XAbs for d in self.Data]
      col_y = [d.YAbs for d in self.Data]
      
      x_min = min(col_x)
      x_max = max(col_x)
      y_min = min(col_y)
      y_max = max(col_y)
      
      self.Data = list(map(lambda x: x.Normalize(x_min, x_max, y_min, y_max), self.Data))
      
   def Print(self):
      print("Centroids: " + str(self.Centroids))
      #for i in self.Data:
      #   print(i)
      
   def RandomCentroids(self):
      self.Centroids = [
         Point(xnorm = random.random(), ynorm = random.random()) 
         for _ in range(0, self.K)]
         
      self.InitialCentroids = list(self.Centroids)
         
   def AssignCentroids(self):
      delta = 0
      for d in self.Data:
         min_dist = -1
         min_centroid_i = -1
         new_centroid = -1
         for i in range(len(self.Centroids)):
            dist = self.EuclideanDistance(d, self.Centroids[i])
            if dist < min_dist or min_dist < 0:
               new_centroid = i
               min_dist = dist
         if new_centroid >= 0:
            if new_centroid != d.Centroid:
               delta += 1
            d.Centroid = new_centroid
            
      if delta == 0:
         self.CentroidsStable = True
               
   def EuclideanDistance(self, a, b):
      return (math.pow(a.X - b.X, 2) + math.pow(a.Y - b.Y, 2)) / 2
      
   def UpdateCentroids(self):
      for i in range(0, len(self.Centroids)):
         members = self.GetCentroidMembers(i)
         self.Centroids[i] = self.GetMeanPosition(self.Centroids[i], members)
      
   def GetCentroidMembers(self, idx):
      return [x for x in self.Data if x.Centroid == idx]
      
   def GetMeanPosition(self, centroid, points):
      if len(points) <= 0:
         return centroid
      x = y = 0
      for p in points:
         x += p.X
         y += p.Y
      x = x / len(points)
      y = y / len(points)
      
      return Point(xnorm = x, ynorm = y)
      
   def Run(self):
      done = False
      
      while not done:
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
               done = True
         
         self.Screen.fill(self.BackgroundColor)
         
         self.AssignCentroids()
         self.DrawText()
         self.DrawPoints()
         if self.CentroidsStable:
            if self.SaveImageOn:
               self.SaveImage()
            return
         self.UpdateCentroids()
         pygame.time.wait(self.FrameDelay)
      
         pygame.display.flip()
      
   def SaveImage(self):
      if not os.path.isdir('lab3_images'):
         os.mkdir('lab3_images')
      pygame.image.save(self.Screen, 'lab3_images\K_{0:d}_{1}.png'.format(self.K, time.strftime('%H_%M_%S')))
      
   def DrawText(self):
      text = self.Font.render("K: {:d}".format(self.K), True, (0x0, 0x0, 0x0))
      self.Screen.blit(text, (20, 10, 0, 0))
      
      text = self.Font.render("Initial Position", True, (0x0, 0x0, 0x0))
      self.Screen.blit(text, (20, 30, 0, 0))
      for i in range(len(self.InitialCentroids)):
         pygame.draw.circle(self.Screen, self.CentroidColors[i], (10, 16*(i+1)+35), 5, 0)
         centroid_coords = '({0:5.3f}, {1:5.3f})'.format(self.InitialCentroids[i].X, self.InitialCentroids[i].Y)
         text = self.Font.render(centroid_coords, True, (0x0, 0x0, 0x0))
         self.Screen.blit(text, (20, 16*(i+1) + 30, 0, 0))
         

      text = self.Font.render("Final Position", True, (0x0, 0x0, 0x0))
      self.Screen.blit(text, (20, 150, 0, 0))
      for i in range(len(self.InitialCentroids)):
         pygame.draw.circle(self.Screen, self.CentroidColors[i], (10, 16*(i+1)+155), 5, 0)
         centroid_coords = '({0:5.3f}, {1:5.3f})'.format(self.Centroids[i].X, self.Centroids[i].Y)
         text = self.Font.render(centroid_coords, True, (0x0, 0x0, 0x0))
         self.Screen.blit(text, (20, 16*(i+1) + 150, 0, 0))         
         
   def DrawPoints(self):
      dw = 600
      dh = 600
      db = 10
      offx = 170
      offy = 10
   
      pygame.draw.rect(self.Screen, (0x0, 0x0, 0x0), (offx, offy, dw + 2*db, dh + 2*db), 1)
   
      for d in self.Data:
         x = d.X
         y = d.Y
         color = self.CentroidColors[d.Centroid]
         pygame.draw.circle(self.Screen, color, (int(dw * x) + offx + db, int(dh * y) + offy + db), 5, 0)
         
      for d in self.Centroids:
         x = d.X
         y = d.Y
         pygame.draw.circle(self.Screen, self.CentroidColor, (int(dw * x) + offx + db, int(dh * y) + offy + db), 10, 2)
      
if __name__ == '__main__':
   with open('lab3-data.txt') as file:
      data = [x.split('\t') for x in file.read().split('\n')]
      data = [Point(float(x[0]), float(x[1])) for x in data[1:-1]]
      
      save_image = True if '--image' in sys.argv or '-i' in sys.argv else False
      frame_delay = 500
      run_count = 5 
      
      delayFound = False
      countFound = False
      for arg in sys.argv:
         if delayFound:
            frame_delay = int(arg)
            delayFound = False
         if countFound:
            run_count = int(arg)
            countFound = False
         if arg == '-d' or arg == '--delay':
            delayFound = True
         if arg == '-c' or arg == '--count':
            countFound = True
      
      for k in range(2, 6):
         for _ in range(0, run_count):         
            cluster = Cluster(data, k, save_image, frame_delay)
            cluster.Run()
            print("K: {}".format(cluster.K))
            for d in cluster.Data:
               print('{0:2.1f}\t{1:2.1f}\tGroup {2:d}'.format(d.XAbs, d.YAbs, d.Centroid + 1))
