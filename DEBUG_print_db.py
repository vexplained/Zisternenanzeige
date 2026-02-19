import pickle
from pprint import pprint

with open("data/database.pkl", "rb") as file:
    content = pickle.load(file)

pprint(content)
