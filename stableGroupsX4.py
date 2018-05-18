"""
#
#  Author : James Hope          
#  Date   : 13 May 2018          
#
"""

import sys
import csv
import numpy as np
import pandas as pd
import sets
import copy

# parse command line options    
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
        #print("entering new engagement")
        if proposer in self.engagements:
            #print("new engagement1")
            self.engagements[self.engagements.tolist().index(proposer)] = np.nan

        if acceptor in self.engagements:
            #print("new engagement2")
            self.engagements[self.engagements.tolist().index(acceptor)] = np.nan

        self.engagements[acceptor-1] = proposer
        self.engagements[proposer-1] = acceptor
        #print("new engagement made")

    def is_complete(self):
        """
        Return True if complete
        """
        if (np.isnan(self.engagements).any()):
            return False
        else:
            return True

    def not_engaged(self,proposer):
        """
        Return True if engaged otherwise False
        """
        if proposer in self.engagements:
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

    def get_preference_number(self,acceptor,proposer,null_position):
        """
        Return the preference of the acceptor for the proposer passed. Return 0 if value is null or if the preference is not in the list.
        """
        #if (proposer==null_position) or (acceptor==null_position): 
        #    return 0

        if proposer in self.values[acceptor-1]:
            return self.values[acceptor-1].index(proposer)+1
        else: 
            return 0

    def is_proposal_accepted(self,acceptor,proposer,pool_object,pools_object,null_position,orphan_round,max_set_size,names,preference,acceptors_table,proposer_object):
        """
        If proposer is in accepter preferences return true else return false
        """
        if debug: print("position of preference in acceptor table (for proposal):", self.get_preference_number(acceptor,proposer))
        if debug: print("acceptor is currently engaged to:", pool_object.get_current_engagement(acceptor))
        if debug: print("position of preference in acceptor table (for current engagement):", self.get_preference_number(acceptor,pool_object.get_current_engagement(acceptor)))

        #check if the proposal would create a set size that exceeds the maximum set size and if so return false
        if is_set_size_allowed(acceptors_table,pool_object,names,preference,proposer,proposer_object,pools_object,max_set_size)==False:
            return False

        if orphan_round: 
            # If Orphan then If Engagements empty accept, Elseif better than current engagement accept; Else reject (i.e. not listed)
            if (np.isnan(pool_object.get_current_engagement(acceptor)) and np.isnan(pool_object.get_current_engagement(proposer)) and pools_object.is_orphan(proposer) and pools_object.is_valid_engagement(acceptor,proposer) and (self.get_preference_number(acceptor,proposer,null_position)!=0)):
                return True
            elif ((pools_object.is_orphan(proposer) and pools_object.is_valid_engagement(acceptor,proposer) and (self.get_preference_number(acceptor,proposer,null_position)!=0) and (self.get_preference_number(acceptor,proposer,null_position) < self.get_preference_number(acceptor,pool_object.get_current_engagement(acceptor),null_position)))): 
                return True 
            else:
                return False
        else:
            # Same logic as above but do not restrict to orphans
            if (np.isnan(pool_object.get_current_engagement(acceptor)) and np.isnan(pool_object.get_current_engagement(proposer)) and (self.get_preference_number(acceptor,proposer,null_position)!=0) and pools_object.is_valid_engagement(acceptor,proposer)):
                return True
            elif ((pools_object.is_valid_engagement(acceptor,proposer) and (self.get_preference_number(acceptor,proposer,null_position)!=0) and (self.get_preference_number(acceptor,proposer,null_position) < self.get_preference_number(acceptor,pool_object.get_current_engagement(acceptor),null_position)))): 
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
        #print("proposer",proposer,"iteration",iteration,"result",self.values[proposer][iteration])
        return self.values[proposer][iteration]

# Pools Class :: holds pool (engagement) objects  
class Pools:
    def __init__(self):
        """
        Construct the proposer preferences
        """
        self.values = []

    def length(self):
        """
        Return the length of the pools set
        """
        return len(self.values)

    def add_pool(self,pool_object):
        """
        Add pool objects to the Pools object class
        """
        self.values.append(pool_object)
        
    def remove_pool(self):
        """
        Remove last object added to values
        """
        self.values.pop(len(self.values)-1)

    def is_valid_engagement(self,acceptor,proposer):
        """
        If already engaged to proposer in previous iteration; otherwise return True
        """
        for i in range(len(self.values)):   
            if self.values[i].get_current_engagement(acceptor)==proposer: 
                return False #if found don't allow engagement
        
        return True 
        
    def is_orphan(self,proposer):
        """
        Check if the proposer appears on any previous set of engagements (pool) and if so return True to indicate orphan
        """
        for i in range(len(self.values)):   
            if not np.isnan(self.values[i].get_current_engagement(proposer)): 
                return False  #if found don't allow engagement
        return True 

    def get_pool_object(self,pool_object_number):
        """
        Return the pool object from the pools class
        """
        return self.values[pool_object_number]

def import_preferences(input_file):
    """
        Read the data from file and return the names and preferences
    """
    with open(input_file) as csvfile:
        preferences = []
        names = []
        reader = csv.reader(csvfile)
        print("\n Input file read from file \n")
        for row in reader:
            data = list(row)
            print("{}".format(data))
            preferences.append(data[1:])    
            names.append(data[0])
        return(preferences[1:], names[1:])

def encode(names,name):
    """
    Return the index of the name in the list of names
    """
    return names.index(name)+1

def return_null_position(names):
    """
    Return tye position of the null value
    """
    return names.index("null")+1

def is_set_size_allowed(acceptors_table,pool_object,names,preference,proposer,proposer_object,pools_object,max_set_size):
    """
    If engagement creates a set size that exeeds max_set_size return False; otherwise return True 
    """
    # create dummy pool and pools
    pool_test = Pool(acceptors_table)
    pool_test = copy.deepcopy(pool_object)     
    pool_test.new_engagement(proposer_object.get_proposal(proposer,preference),proposer+1)
    
    pools_test = Pools()
    pools_test = copy.deepcopy(pools_object)  
    pools_test.add_pool(pool_test)
    
    if (len(build_groups(names,build_pairs(names,pools_test),pools_test))>max_set_size):        
        #print(build_groups(names,build_pairs(names,pools_object),pools_object))        
        return False
        
    del pool_test
    del pools_test
        
    return True

def encode_preferences(preferences,names,no_of_preferences):
    """
    Encode the preferences 
    """
    df = pd.DataFrame(data=preferences)
    
    for i in range(0,no_of_preferences):
        df[i] = df[i].apply(lambda x: encode(names,x))

    return(df.values.tolist())

def dec(names,index):
    """
    Return the index of the name in the list of names
    """
    return names[index-1]

def decode(pairs,names):
    """
    Decode the engagements
    """  
    df = pd.DataFrame(data=pairs)
    df[0] = df[0].fillna(-2)  
    df = pd.DataFrame(data=pairs).astype(int)    
    df[0] = df[0].apply(lambda x: dec(names,x) if x>0 else None) #decode engagements (ignore negative values)
    return(df.values.tolist())

def stable_pairs(pool_object,pools_object,proposer_object,proposers_table,accepter_object,acceptors_table,no_of_preferences,null_position,orphan_round,max_set_size,names):
    """
    Create stable engagements and return the list
    """
    for preference in range(0,no_of_preferences):
        if debug: print("/n PREFERENCE:", preference+1)
        #print("width",range(len(proposers_table[preference])))
        for proposer in range(len(proposers_table)-1):

            if pool_object.not_engaged(proposer+1):
                if debug: print("PROPOSAL:", proposer+1, "---->", proposers_table[proposer][preference])        
                
                if accepter_object.is_proposal_accepted(proposer_object.get_proposal(proposer,preference),proposer+1,pool_object,pools_object,null_position,orphan_round,max_set_size,names,preference,acceptors_table,proposer_object): #if proposal is accepter
                    if debug: print("PROPOSAL ACCEPTED")
                    pool_object.new_engagement(proposer_object.get_proposal(proposer,preference),proposer+1)
                else:
                    if debug: print("PROPOSAL FAILED")

                #print(pool_object.get_all_engagements())

            if pool_object.is_complete():
                return pool_object

    return pool_object

def stable_marriage(pools_object,proposer_object,proposers_table,accepter_object,acceptors_table,iteration,no_of_preferences,null_position,max_set_size,names):
    """
    Call the stable_pairs function iteratively and update the Pools object
    """
    for i in range(iteration):
        if debug: print("ITERATION:",i+1)
        
        # add pool object with stable pairs
        pool_object = Pool(acceptors_table) #create a pool object
        pools_object.add_pool(stable_pairs(pool_object,pools_object,proposer_object,proposers_table,accepter_object,acceptors_table,no_of_preferences,null_position,False,max_set_size,names)) #call stable pairs
        print("\n Engagements (all members) found at iteration {} \n {}".format(i+1,pool_object.get_all_engagements()))
        
        # add pool object with orphans
        pool_object = Pool(acceptors_table) #create a pool object
        pools_object.add_pool(stable_pairs(pool_object,pools_object,proposer_object,proposers_table,accepter_object,acceptors_table,no_of_preferences,null_position,True,max_set_size,names)) #call stable pairs
        print("\n Engagements (Orpans) found at iteration {} \n {}".format(i+1,pool_object.get_all_engagements()))
        
def build_pairs(names,pools_object):
    """
    Build a list of all stable pairs by fetching pairs from each pool_object in the pools_object
    """
    pairs = pd.DataFrame()
    pairs[0] = names

    for i in range(pools_object.length()):
        pairs[i+1] = np.array(decode(pools_object.get_pool_object(i).get_all_engagements(), names)).flatten() #pd.DataFrame(data=engagements)  

    return(pairs)

def check_if_intersection(set_1,set_2):
    """
    Returns true if an intersection between two lists is found, otherwise false
    """
    set1 = set(set_1)
    set2 = set(set_2)

    if ((set1.intersection(set2) != set()) and (not "null" in set1) and(not "null" in set2)):
        return True
    else:
        return False

def get_union(set_1,set_2):
    """
    Returns the union of two lists
    """
    set1 = set(set_1)
    set2 = set(set_2)
    result = set1.union(set2)
    
    if "null" in result:
        result.remove("null")
    return result

def build_groups(names,pairs,pools_object):
    """
    From the pairs data, build lists of sets and return the set lists (provided there are more than 2 columns)
    """
    sets = []
    pairs = pairs.fillna(value="null")
    
    #only perform traverse if we have a minimum of two columns
    if pairs.shape[1]>1:
        
        #create sets for members at first level
        for i in range(len(names)):
            result = list(get_union(list([pairs[0][i]]),list([pairs[1][i]])))
            if result not in sets:
                sets.append(result)
        #print("output of level1 join", sets)
    
        # Now join level2, level3 etc members and maintain the trees
        for i in range(2,pools_object.length()+1): #or   #pairs.shape[1]
            for j in range(len(names)):
                index_to_join = -1
                index_to_remove = -1
    
                #check if the student is already in a set somewhere else and if so get the index of that set
                for k in range(len(sets)):
                    if pairs[i][j] in sets[k]:
                        index_to_remove = k
                        if debug: print("index to remove", index_to_remove)
    
                #get the index of the set the student is already in 
                for k in range(len(sets)):
                    if pairs[0][j] in sets[k]:
                        index_to_join = k
                        if debug: print("index to join",index_to_join)
    
                if (index_to_join==index_to_remove):
                    #print("idex to join = index to remove")
                    pass
                elif ((index_to_remove!=-1) and (index_to_join!=-1)):
                    sets[index_to_join] = list(get_union(sets[index_to_join],sets[index_to_remove]))
                    sets.pop(index_to_remove) 
    
    df = pd.DataFrame(data=sets)
    df = df.transpose()
    return df 

def main():

    try:
        input_file = "Preferences4.csv"
        #input_file = sys.argv[1]
        iteration = 2
        #iteration = int(sys.argv[2]) # Number of runs of stable pairs algoirthm. Subsequent runs ignore stable pairs already built.
        no_of_preferences = 5
        #no_of_preferences = int(sys.argv[3]) # Number of preferences to read from input file
        max_set_size = 12
        #max_set_size = int(sys.argv[4]) # Maximum number in a set
        
    except: 
        print("stableGroups.py --[input_file] --[iteration] --[no_of_preferences] --[max_set_size]\n")
        print("--[input_file] \n input file in csv format \n")
        print("--[iteration] \n number of runs of Stable Pairs Algorithm \n")
        print("--[no_of_preferences] \n number of preferences to read from input file \n")
        print("--[max_set_size] \n maximum size of a set \n")
        sys.exit()
    else: pass

    output_file_stable_pairs = 'pools.csv'
    output_file_sets = 'sets.csv'
    
    # Import and Encode the preferences data
    preferences,names = import_preferences(input_file) 
    preferences = encode_preferences(preferences,names,no_of_preferences)
    print("\n Input file with {} preferences read and encoded successfully as \n {}".format(no_of_preferences, preferences))

    null_position = return_null_position(names)
    print("\n Instantiating Acceptor and Proposer objects with input preference data... \n")
    acceptors_table = preferences
    #acceptors_table = [[1,3,2,4],[3,4,1,2],[4,2,3,1],[3,2,1,4]]
    proposers_table = acceptors_table

    # Instantiate the Acceptor and Proposer class objects
    accepter_object = Acceptor(acceptors_table)
    proposer_object = Proposer(proposers_table)
    print("\n Instantiating Pool and Pools objects ready to hold engagements... \n")

    # Instantiate the Pools Class object
    pools_object = Pools()

    # Run the Algorithm
    print("\n Finding Stable Pairs with {} iterations of the algorithm... \n".format(iteration))
    stable_marriage(pools_object,proposer_object,proposers_table,accepter_object,acceptors_table,iteration,no_of_preferences,null_position,max_set_size,names)

    # Write the engagements to file
    pairs = build_pairs(names,pools_object)
    print("\n Writing pairs to file (1st iteration row 1 - 2, 2nd iteration 1 - 3 etc.)\n {}".format(pairs))
    #print("\n Writing pairs to file (1st iteration row 1 - 2, 2nd iteration 1 - 3 etc.)\n")
    pairs.to_csv(output_file_stable_pairs)

    # Convert engagements to sets and write to file
    groups = build_groups(names,pairs,pools_object)
    print("\n Writing sets to file (a set is a column)\n {}".format(groups))
    print("length of groups", len(groups))
    groups.to_csv(output_file_sets)

if __name__ == "__main__":
    main()

