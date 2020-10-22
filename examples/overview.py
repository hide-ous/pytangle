# Copyright (C) 2020 Mattia Samory

from pytangle.api import API

if __name__ == '__main__':

    api = API()

    # fetch all lists linked to the current dashboard
    for a_list in api.lists():
        print(a_list)

    # get the 5 top overperforming posts
    for a_post in api.posts(count=5):
        print(a_post)

    # get information about a specific post
    post_id = "1515871602074952_5362226790772728"
    for a_post in api.post(id=post_id, endpoint='platform'):
        print(a_post)

    # get the first 5 entries in the leaderboard for the current dashboard
    for an_account in api.leaderboard(count=5):
        print(an_account)

    # get the top 5 sharers of a link
    an_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    for a_post in api.links(count=5, link=an_url, platforms='instagram'):
        print(a_post)
    exit()

    # get information on an account
    list_id = a_list['id']
    for an_account in api.accounts_in_list(count=5, listId=list_id):
        print(an_account)

    # get all posts in the dashboard from Jan until June 2020
    list_ids = [a_list['id']]
    for n, a_post in enumerate(api.posts(listIds=list_ids,
                                         count=-1,
                                         batchSize=100,
                                         sortBy='date',
                                         startDate='2020-01-01',
                                         endDate='2020-06-30',
                                         timeframe=None,
                                         )):
        # do something with the post
        if not (n+1) % 1000:
            print(n+1)
            # stopping at 1000 posts, otherwise it may take some time...
            break
    print(n)
