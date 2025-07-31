# src/modelmain.py 

import sys 

from preprocessing.preprocess import Preprocessor
from modeling.trainer import ModelTrainer

def PreprocessDataWrapper(): 
    preprocessor = Preprocessor()
    preprocessor.run()

def ModelTrainerWrapper():
  modeltrainer = ModelTrainer()
  modeltrainer.run()

if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1] == "preprocess":
      PreprocessDataWrapper()
  elif sys.argv[1] == 'train':
    ModelTrainerWrapper()
  else: 
      print("Usage: python modelmain.py preprocess")
      sys.exit(1)