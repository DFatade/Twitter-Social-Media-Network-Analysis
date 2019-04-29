import tweepy
import time
import networkx as nx
from matplotlib import rcParams
import matplotlib.pyplot as plt

rcParams["figure.figsize"]=20,10
rcParams['axes.titlesize']=20

#This program was written in tweepy since I could not get the twitter api to work on
#my pc. I wrote most of the program by myself. The only function that I made use of
#from the textbook is the setwise_friends_followers_analysis function.

#This function will generate the api

def genereate_api():
    
    #consumer key for auhtentication purposes
    consumer_key= "2xsheoZ9NhGB62h6tM2TInnTM"
    consumer_secret="HoaS7DovZoJ9EPBVuAkt5LnjNnz0mCNxyvnpucnY9HYgnmPGLH"
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    
    #access token for auhtentication purposes
    access_token="1171944902-joVLh3WDoRskbCSBTL4zs8OPSV9pgLMQMuhqkza" 
    access_token_secret="buVkUsSaBR2coAM9hXbS3ZlPqyCVakuj2sMvpZTgzVSSG"
    
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    return api


def get_friends_and_followers(username_or_id):
    
    #return the ids of friends in a list
    api=genereate_api()
    friends_id=api.friends_ids(username_or_id)
    
    #returns a list of my followers ID's
    followers_id=api.followers_ids(username_or_id)
    
    return friends_id, followers_id

#returns reciprocal friends in a list format

#function displays number of my followers, number of people I am following as well as
#my reciprocal followers and non-reciprocal followers

#This setwise function comes from the textbook provided by Professor Yu.

def setwise_friends_followers_analysis(screen_name, friends_ids, followers_ids):
    
    friends_ids, followers_ids = set(friends_ids), set(followers_ids)
    
    print('{0} is following {1}'.format(screen_name, len(friends_ids)))
    
    print('{0} is being followed by {1}'.format(screen_name, len(followers_ids)))
    
    print('{0} of {1} are not following {2} back'.format(
            len(friends_ids.difference(followers_ids)), 
            len(friends_ids), screen_name))
    
    print('{0} of {1} are not being followed back by {2}'.format(
            len(followers_ids.difference(friends_ids)), 
            len(followers_ids), screen_name))
    
    print('{0} has {1} mutual friends'.format(
            screen_name, len(friends_ids.intersection(followers_ids))))
    
    return list(friends_ids.intersection(followers_ids))


#This function will return the follower count of your reciprocal friends.

def get_your_friends_follower_count(reciprocal_friends):
    
    #generate the api
    api=genereate_api()
    #dictionary will store information about friend and their follower count
    get_info={}
    #list to hold mined ids
    mined_ids=[]
    
    #list to hold mined follower counts
    mined_followers_count=[]
    
    #these lists will hold final values
    ids=[]
    followers_count=[]
    
    #this portion of the code will execute only if the length of the reciporcal friends list is greater than 100
    if len(reciprocal_friends) > 100:
        
        #tweepy will only let me return the information of 100 followers at a time.
        #This code calculates values of 100 per number of followers
        #So if one has 1000 followers, the function will be calculated like: 100,200 and so on.
        value=len(reciprocal_friends)
        iters=int(value/100)
        it=-1
        vals=[]
        for i in range(0,iters):
            vals.append([(it+1)*100,(it+2)*100])
            it=it+1
            
        vals.append([iters*100,(iters*100)+(value%100)])
         
        a=[]   
        
        #Using the ranges in our vals list, we use list slcing to effectively make api calls
        for j in range(0,len(vals)):
            
            #json formated dict is stored in mined lists
            mined_ids.extend(api.lookup_users(user_ids=reciprocal_friends[vals[j][0]:vals[j][1]]))
            mined_followers_count.extend(api.lookup_users(user_ids=reciprocal_friends[vals[j][0]:vals[j][1]]))
        
        #exact target values are stored in this list
        for k in range(0,len(mined_ids)):
            ids.append(mined_ids[k]._json['id'])
            followers_count.append(mined_followers_count[k]._json['followers_count'])
            
    
    else:
        a=api.lookup_users(user_ids=reciprocal_friends[0:100])
        for i in range(0,len(a)):
            ids.append(str(a[i]._json['id']))
            followers_count.append(a[i]._json['followers_count'])

     
    #convert both lists to a dictionary and return the data
    list_to_dict=zip(ids,followers_count)
    info=dict(list_to_dict)
    
    return info


def get_top_5_friends(info):
    
    #convert the values we received from the previous function into a list and sort it
    values=list(info.values())
    values.sort()
    top_friends_followers_ids=[]
    
    #top 5 follower counts will be the 5 greatest at the end of the list sp we take those
    follower_counts=values[len(values)-5:len(values)]
    
    i=0
    
    if len(info) <5:
        return info
    
    #iterate through the keys of the info dict, if the value in the dict is
    #equal to the follower counts stored in the follower_counts list, store it in the top_friends_followers_ids list
    
    while(i<5):
        
        for element in list(info.keys()):
            if info[element]==follower_counts[i]:
                top_friends_followers_ids.append(element)
        i=i+1
        
        
        top_5=zip(top_friends_followers_ids,follower_counts)
        top_5=dict(top_5)
        
    return top_5


def get_distance_one_friends(username_or_id):
    
    #function calls all our previous functions to generate distance-1 friends with the top 5 highest 
    #follower counts.
    
    friends_id, followers_id=get_friends_and_followers(username_or_id)
    reciprocal_friends=setwise_friends_followers_analysis(username_or_id, friends_id,followers_id)
    info=get_your_friends_follower_count(reciprocal_friends)
    top_5=get_top_5_friends(info)
    return top_5



def get_distance_two_friends(username_or_id):
    
    #function calls distance -1 friends and uses this data to find information about each of their top
    #5 most popular followers.
    
    data=get_distance_one_friends(username_or_id)
    information=[]
    list_data_keys=list(data.keys())
    
    for element in list_data_keys:
        information.append(get_distance_one_friends(element))
        
    return information



def get_distance_three_friends(data):
    
    #This function makes use of data receieved from the distance -2 friends fucntion to find
    #find information about each of their top 5 most popular followers.
    
    information=[]
    
    for element in data:
        for i in list(element.keys()):
            try:
                information.append(get_distance_one_friends(i))
            #I had to add this try catch statement because this function would occasionally run into Tweepy's
            # rate limit error. So this exception block would sleep for 15 minutes when that error occured.
            except tweepy.TweepError:
                time.sleep(60 * 15)
                continue
        
    
    return information
    


def graph_object(data_1,data_2,data_3):
    
    #instantiate a networkx graph object
    G=nx.Graph()
    head=1171944902
    G.add_node(head)
    
    #converts dictionaries into list format from data points 1,2 and 3
    
    list_data_1=list(data_1.keys())
    G.add_nodes_from(list_data_1)
    list_data_2=[]

    for element in data_2:
        for i in element.keys():
            list_data_2.append(i)
            
    
            
    list_data_3=[]

    for element in data_3:
        for i in element.keys():
            list_data_3.append(i)
            
    
    
            
    #add edges from my account and my top 5 most popular friends
    for i in range(0,len(list_data_1)):
        G.add_edges_from([(1171944902,list_data_1[i])])
        
    #add edges between distance 1 friends and distance 2 friends    
    for j in range(0,len(data_2)):
        for k in list(data_2[j].keys()):
            G.add_edges_from([(list_data_1[j],k)])
    
    
    #add edges between distance 2 friends and distance 3 friends 
    for l in range(0,len(data_3)):
        for m in list(data_3[l].keys()):
            G.add_edges_from([(list_data_2[l],m)])
        
    
    
    #Just generate a little title for my graph plot
    plt.title("Daniel Fatade's Social Media Network")    
    nx.draw_spring(G, node_color='bisque',with_labels=True)
    
    #This saves the graph figure.
    #plt.savefig('my_network_graph')
    
    #These functions calculate the diamter of the graph, the number of nodes and edges present in the graph
    #and the average distance of the graph 
    
    n_edges=G.number_of_edges()
    diameter=nx.diameter(G)
    average_dist=nx.average_shortest_path_length(G)
    
    n_nodes=G.nodes()
    
    print("This graph contains {0} distinct nodes with {1} edges. ".format(len(n_nodes),n_edges))
    print("The Diameter of this network is: {0} ".format(diameter))
    print("The average distance between each node in the Graph is: {0}".format(average_dist))


data_1=get_distance_one_friends(1171944902)
data_1
data_2=get_distance_two_friends(1171944902)
data_2
data_3=get_distance_three_friends(data_2)
data_3

graph_object(data_1,data_2,data_3)







