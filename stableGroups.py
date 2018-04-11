import sys
import requests
import numpy as np
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import pandas as pd
from flask import Flask, jsonify, request

debug = False

# Pool Class :: holds engagements
class Pool:
    def __init__(self, acceptors):
        """
        Construct an array which will hold the engagements. Instatiate each maximum preference number that 
        """
        self.engagements = np.empty(shape=len(acceptors))
        self.engagements.fill(np.nan) 

    def new_engagement(self,acceptor,proposer):
        """
        Update (replace) the engagement in the pool 
        """
        if proposer in self.engagements:
            print(proposer, "in position", self.engagements.tolist().index(proposer)+1, "set to NaN")
            self.engagements[self.engagements.tolist().index(proposer)] = np.nan

        self.engagements[acceptor-1] = proposer
 
    def is_complete(self):
        """
        Return True if complete
        """
        if (np.isnan(self.engagements).any()):
            return False
        else:
            return True

    def get_current_engagement(self,acceptor): 
        """
        Return the current engagement for a acceptor
        """
        return self.engagements[acceptor-1]

    def get_all_engagements(self):
        """
        Return all the current engagements
        """        
        return self.engagements

# Acceptor Class :: holds the acceptor preferences
class Acceptor:
    def __init__(self,values):
        """
        Construct the acceptor preferences
        """
        self.values = values

    def get_preference_number(self,acceptor,proposer):
        """
        Return the preference of the acceptor for the proposer passed
        """
        #print(self.values[acceptor-1])
        if proposer in self.values[acceptor-1]:
            return self.values[acceptor-1].index(proposer)+1
        else: 
            return 0

    def is_proposal_accepted(self,acceptor,proposer):
        """
        If proposer is in accepter preferences return true else return false
        """
        if debug: (print("acceptor preference of proposal", self.get_preference_number(acceptor,proposer)))
        if debug: (print("acceptor currently engaged to", pool_object.get_current_engagement(acceptor)))
        if debug: (print("acceptor preference of current engagement", self.get_preference_number(acceptor,pool_object.get_current_engagement(acceptor))))

        if (np.isnan(pool_object.get_current_engagement(acceptor)) and (self.get_preference_number(acceptor,proposer)!=0)):
            return True
        
        if (self.get_preference_number(acceptor,proposer) < self.get_preference_number(acceptor,pool_object.get_current_engagement(acceptor))): 
            return True 
        else:
            return False

# Proposer Class :: holds the proposer preferences
class Proposer:
    def __init__(self, values):
        """
        Construct the proposer preferences
        """
        self.values = values

    def get_proposal(self,proposer,iteration):
        """
        Return the acceptor value (proposal to try) for the proposer and iteration passed
        """
        #return self.values.iloc[proposer,iteration]
        return self.values[proposer][iteration]

# Create dummy data
acceptors_table = [[1,2,3,4],[3,4,1,2],[4,2,3,1],[3,2,1,4]]
proposers_table = [[2,1,3,4],[4,1,2,3],[1,3,2,4],[2,3,1,4]]

# Instantiate the Acceptor and Proposer class
accepter_object = Acceptor(acceptors_table)
proposer_object = Proposer(proposers_table)

print("Acceptors Table:", accepter_object.values)
print("Proposers Table:", proposer_object.values)

# Instantiate the pool class
pool_object = Pool(np.unique(acceptors_table))
if debug: print("Pool Object:", pool_object.get_all_engagements())

def stable_marriage():
    for iteration in range(len(proposers_table)):
        print("\n Round:", iteration+1)
        for proposer in range(len(proposers_table[iteration])):
            print("PROPOSAL:", proposer+1, "---->", proposers_table[proposer][iteration])        
            
            if accepter_object.is_proposal_accepted(proposer_object.get_proposal(proposer,iteration),proposer+1): #if proposal is accepter
                if debug: print("PROPOSAL ACCEPTED")
                pool_object.new_engagement(proposer_object.get_proposal(proposer,iteration),proposer+1)
            else:
                if debug: print("PROPOSAL FAILED")
            print("ENGAGEMENTS:", pool_object.get_all_engagements())

            if pool_object.is_complete():
                return pool_object.get_all_engagements()

print("\n FINAL ENGAGEMENTS:", stable_marriage())

