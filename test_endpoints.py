import time
start = time.time()


from pytangle.api import API
api = API()


print("\n\n\n\nfetch all lists linked to the current dashboard")

for a_list in api.lists():
    print(a_list)



print("\n\n\n\nget the 5 top overperforming posts")
for a_post in api.posts(count=5):
    print(a_post)    


print("\n\n\n\nget information about a specific post")
post_id = "1515871602074952_5362226790772728"
for a_post in api.post(id=post_id, endpoint='platform'):
    print(a_post)    

print("\n\n\n\nget the first 5 entries in the leaderboard for the current dashboard")
for a_leaderboard in api.leaderboard(count=5):
    print(a_leaderboard)

print("\n\n\n\nget the top 5 sharers of a link")
an_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
for a_post in api.links(count=5, link=an_url):
    print(a_post)    


print("\n\n\n\nget information on an account")
list_id = 34081 # the id of one of your lists
for an_account in api.accounts_in_list(count=5, listId=list_id):
    print(an_account)    

list_ids = [34081] # ids of the lists of interest

print("\n\n\n\nget the 5 top overperforming posts")
for a_post in api.posts(listIds = list_ids, sortBy='interaction_rate',):
    print(a_post)


# print("\n\n\n\nget the 5 top overperforming posts by list")

# for a_post in api.posts(listIds = list_ids,
#                         startDate='2020-10-01',
#                         endDate='2020-10-03'):
#     print(a_post)


print("\n\n\n\nget all posts from a list from Jan until June 2020")

posts = []


# sortBy : ( date, interaction_rate, overperforming, 
# total_interactions, underperforming)

for n, a_post in enumerate(api.posts(listIds=list_ids,
                                     count=1000,
                                     batchSize=100,
                                     sortBy='interaction_rate',
                                     startDate='2019-12-01',
                                     endDate='2020-06-30',
                                     timeframe=None,
                                     )):
    # do something with the post
    posts.append(a_post)
    if not n % 1000:
        print(n)    


print(len(posts)        )
print(posts[0])


print("\n\n\n\n\n\n")
print('It took', time.time()-start, 'seconds.')
