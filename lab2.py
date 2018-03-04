import math
import random

class KNN:
   def __init__(self, k, training_data, testing_data, attrib_cols, class_col):
      self.K = k
      self.TrainingData = training_data
      self.TestingData = testing_data
      self.AttributeColumns = attrib_cols
      self.ClassColumn = class_col
      
      self.SampleTestData = []
      self.SampleData = []
      self.Classes = set(x[2] for x in training_data)
      
   def NormalizeColumns(self):
      new_list = []
      for i in self.TrainingData:
         new_list.append([])
         
      for i in range(0, len(self.TrainingData[0]) - 1):
         col = [x[i] for x in self.TrainingData]
         col_max = max(col)
         col_min = min(col)
         for j in range(len(col)):
            new_list[j].append((col[j] - col_min) / (col_max - col_min))
            
      for i in range(len(self.TrainingData)):
         new_list[i].append(self.TrainingData[i][-1])
            
      self.TrainingData = new_list
      
      new_list = []
      for i in self.TestingData:
         new_list.append([])
         
      for i in range(0, len(self.TestingData[0]) - 1):
         col = [x[i] for x in self.TestingData]
         col_max = max(col)
         col_min = min(col)
         for j in range(len(col)):
            new_list[j].append((col[j] - col_min) / (col_max - col_min))
            
      for i in range(len(self.TestingData)):
         new_list[i].append(self.TestingData[i][-1])
         
      self.TestingData = new_list

   def TestRandomSample(self, percent):
      sample_idx = random.sample(range(0, len(self.TrainingData)), math.ceil(len(self.TrainingData) * percent))
      self.SampleTestData = [self.TrainingData[i] for i in range(0, len(self.TrainingData)) if i in sample_idx]
      self.SampleData = [self.TrainingData[i] for i in range(0, len(self.TrainingData)) if i not in sample_idx]

   def TestUnknown(self):
      self.SampleTestData = self.TestingData
      self.SampleData = self.TrainingData
      
   def EuclidianDistance(self, a, b):
      x = 0
      for i in range(self.AttributeColumns):
         x += math.pow(a[i] - b[i], 2)
      return math.sqrt(x)

   def PredictSet(self):
      for t in self.SampleTestData:
         t.append(self.PredictSingle(t))
      
   def PredictSingle(self, row):
      neighbors = []
      for i in self.SampleData:
         dist = self.EuclidianDistance(row, i)
         neighbors.append(i + [dist])
         neighbors.sort(key=lambda x:x[-1])
         top = neighbors[0:0+self.K]
         temp_classes = {x: 0 for x in self.Classes}
         for t in top:
            temp_classes[t[self.ClassColumn]] += 1
      class_pick = max(temp_classes, key = lambda x: temp_classes[x])
      return class_pick
         
   def PredictionRate(self):
      matches = 0
      for i in self.SampleTestData:
         matches += 1 if i[self.ClassColumn] == i[self.ClassColumn + 1] else 0
      return matches/len(self.SampleTestData)
         
if __name__ == '__main__':
   with open('lab1-training-data.txt') as file:
      training_lines = [x.split('\t') for x in file.read().split('\n')]
   training_data = []
   for x in training_lines[1:-1]:
      training_data.append([float(x[0]), float(x[1]), x[2].replace('\xa0', ' ')])

   with open('lab1-test-data.txt') as file:
      testing_lines = [x.split('\t') for x in file.read().split('\n')]
   testing_data = []
   for x in testing_lines[1:-1]:
      testing_data.append([float(x[0]), float(x[1]), x[2].replace('\xa0', ' ')])

   k_values = [(x*2)+1 for x in range(0, 10)]
   percent_values = [0.2, 0.25, 0.33]
   run_count = 100
   best_prediction = [0, 0, 0]
   
   for i in k_values:
      k = KNN(i, training_data, testing_data, 2, 2)
      k.NormalizeColumns()
      for j in percent_values:
         for r in range(0, run_count):
            k.TestRandomSample(j)
            k.PredictSet()
            prediction_rate = k.PredictionRate()
            print("Running test K: " + str(i) + " P: " + str(j) + " Correct %: " + str(prediction_rate))
            if prediction_rate > best_prediction[2]:
               best_prediction = [i, j, prediction_rate]
               
   print("Best Prediction K: " + str(best_prediction[0]) + " P: " + str(best_prediction[1]) + " Correct %: " + str(best_prediction[2]))
   
   k = KNN(1, training_data, testing_data, 2, 2)
   k.NormalizeColumns()
   k.TestUnknown()
   k.PredictSet()
   prediction_rate = k.PredictionRate()
   for i in k.SampleTestData:
      print(i)
   print("Unknown Data Correct %: " + str(prediction_rate))