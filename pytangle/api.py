import json
import os
import sys

from pytangle.connectivity import Paginator
from pytangle.endpoints import PostsEndpoint, PostEndpoint, SearchEndpoint, LeaderboardEndpoint, ListsEndpoint, LinksEndpoint, \
    AccountsEndpoint
from pytangle.utils import remove_null_values_from_dict
import logging

CONFIG_FILE_LOCATIONS = [os.path.join(os.path.dirname(sys.modules[__name__].__file__), "config.json"),
                         os.path.join(os.path.expanduser('~'), "config.json"),
                         os.path.join(os.path.abspath('.'), "config.json"),
                         ]
logger = logging.getLogger()


class API:
    """Wrapper for calling crowdtangle endpoints. All methods return iterators over the objects returned by
        crowdtangle. Rate limiting, deduplication, and pagination are handled automatically."""
    def __init__(self, token=None):
        """
        Sets the token for the current API instance.
        If no token is provided, it will try to load it from config.py, if found in  CONFIG_FILE_LOCATIONS

        Args:
            token: (str, default None) A valid crowdtangle token
        """
        if token is None:
            # try to get the token from the configuration files
            for config_file_location in CONFIG_FILE_LOCATIONS:
                if os.path.exists(config_file_location) and os.path.isfile(config_file_location):
                    with open(config_file_location) as f:
                        token = json.load(f)['token']

        if token is None:
            raise ValueError("Pass a token value, or set it in the configuration file. None found. Looked here: " + \
                             str(CONFIG_FILE_LOCATIONS))
        self._token = token

    def posts(
            self,
            listIds=None,
            startDate=None,
            endDate=None,
            sortBy="overperforming",
            count=10,
            includeHistory=None,
            batchSize=100,
            language=None,
            minInteractions=0,
            offset=0,
            searchTerm=None,
            timeframe='6 HOUR',
            types=None,
            weightAngry=0,
            weightComment=0,
            weightHaha=0,
            weightLike=0,
            weightLove=0,
            weightSad=0,
            weightShare=0,
            weightView=0,
            weightWow=0,
    ):
        """
        Args:
        listIds : ( None, i.e. entire dashboard ) The IDs of lists or saved searches to retrieve. These can be separated
                    by commas to include multiple lists.
        startDate : ( 0000-00-00 ) The earliest date at which a post could be posted. Time zone is UTC. Format is
                    “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00). This must be before endDate.
                    Timeframe and startDate are mutually exclusive; if both are passed, startDate will be preferred.
        endDate : ( 0000-00-00, default now ) The latest date at which a post could be posted. Time zone is UTC. Format is
                    “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00).
        sortBy : ( date, interaction_rate, overperforming, total_interactions, underperforming, default overperforming )
                    The method by which to filter and order posts. If you do not set this parameter, it will default to
                     sorting by overperforming.
        count : ( positive int or -1, default 10 ) The number of posts to return. -1 means to return all available.
                    If requesting more than 100 posts, batchSize must be set.
        includeHistory : (None or True, default None (does not include)) Includes timestep data for growth of each post
                    returned.
        batchSize : ( 1-100, default 100 ) Number of posts to return at most per call to the endpoint. Between 1-100.
        language : ( None, i.e. all languages ) Exceptions: Some languages require more than two characters: Chinese
                    (Simplified) is zh-CN and Chinese (Traditional) is zh-TW.
        minInteractions : ( None, default 0 ) If set, will exclude posts with total interactions below this threshold.
        offset : ( >= 0, default 0 ) The number of posts to offset (generally used for pagination). Pagination links
                    will also be provided in the response.
        searchTerm : ( None ) Returns only posts that match this search term. Terms AND automatically. Separate with
                    commas for OR, use quotes for phrases. E.g. CrowdTangle API -> AND. CrowdTangle, API -> OR.
                    "CrowdTangle API" -> AND in that exact order.
        timeframe : ( Any valid SQL interval, default 6 HOUR )
                    The interval of time to consider from the endDate. Timeframe and startDate are mutually exclusive;
                    if both are passed, startDate will be preferred. Depending on the number of posts, longer timeframes
                    may not return within the timeout window. If you get a 504, try shortening your timeframe.
        types : ( episode, extra_clip, link, live_video, live_video_complete, live_video_scheduled, native_video, photo,
                    status, trailer, tweet, video, vine, youtube, default None i.e. all ) The types of post to include.
                    These can be separated by commas to include multiple types. If you want all live videos (whether
                    currently or formerly live), be sure to include both live_video and live_video_complete. The "video"
                    type does not mean all videos, it refers to videos that aren't native_video, youtube or vine (e.g.
                    a video on Vimeo).
        weightAngry : ( 0-10, default 0 ) How much weight to give to each type of interaction. If you send in no weights, all
                    weights will use the current dashboard defaults. If you send in at least one weight, all other
                    weights will default to 0. Weights are multiplied by interaction counts: e.g. weightsComment at 1
                    and all others at 0 will find the most commented-on posts. weightLike at 1 and weightShare at 2 will
                    give shares twice the impact as likes when computing scores.
        weightComment : ( 0-10, default 0 )
        weightHaha : ( 0-10, default 0 )
        weightLike : ( 0-10, default 0 )
        weightLove : ( 0-10, default 0 )
        weightSad : ( 0-10, default 0 )
        weightShare : ( 0-10, default 0 )
        weightView : ( 0-10, default 0 )
        weightWow : ( 0-10, default 0 )

        Returns:
        iterator of posts (dict)

        Example use:
        from api import API
        api = API()

        # get the 5 top overperforming posts
        for a_post in api.posts(count=5):
            print(a_post)

        """
        params = dict(
            token=self._token,
            listIds=listIds,
            startDate=startDate,
            endDate=endDate,
            sortBy=sortBy,
            count=count,
            includeHistory=includeHistory,
            batchSize=batchSize,
            language=language,
            minInteractions=minInteractions,
            offset=offset,
            searchTerm=searchTerm,
            timeframe=timeframe,
            types=types,
            weightAngry=weightAngry,
            weightComment=weightComment,
            weightHaha=weightHaha,
            weightLike=weightLike,
            weightLove=weightLove,
            weightSad=weightSad,
            weightShare=weightShare,
            weightView=weightView,
            weightWow=weightWow,
        )
        yield from Paginator(endpoint=PostsEndpoint(args=remove_null_values_from_dict(params)))

    def post(
            self,
            id,
            account=None,
            includeHistory=None,
            endpoint='ct'
    ):
        """
        Args:
        id : ( None ) If endpoint == "platform", the ID of the post on its platform. For Facebook and Instagram,
                    requires the full [number]_[number] ID format. If endpoint == "ct", The CrowdTangle ID of the post.
                    This is provided as a path variable in the URL.
        account : ( None ) Ignored if endpoint == "ct". The slug or ID of the posting account on its platform. This is
                    required for Reddit, ignored for Facebook and Instagram (where a post ID contain the account's ID).
        includeHistory : (None or True, default None (does not include)) Includes timestep data for growth of each post
                    returned.
        endpoint : ( platform, ct, default ct ) which API endpoint to query.

        Returns:
        iterator with a single post (dict) if available

        Example use:
        from api import API
        api = API()

        # get information about a specific post
        post_id = "1515871602074952_5362226790772728"
        for a_post in api.post(id=post_id, endpoint='platform'):
            print(a_post)

       """
        params = dict(id=id,
                      token=self._token,
                      account=account,
                      includeHistory=includeHistory,
                      )
        yield from Paginator(endpoint=PostEndpoint(endpoint=endpoint, args=remove_null_values_from_dict(params)))

    def search(
            self,
            and_=None,
            not_=None,
            count=10,
            includeHistory=None,
            batchSize=100,
            startDate=None,
            endDate=None,
            inAccountIds=None,
            inListIds=None,
            minInteractions=0,
            minSubscriberCount=0,
            notInAccountIds=None,
            notinListIds=None,
            notinTitle=None,
            offset=0,
            platforms=None,
            searchTerm=None,
            searchField="text_fields_and_image_text",
            sortBy="overperforming",
            timeframe="6 HOUR",
            types=None,
            verifiedOnly=False,
            language=None,
    ):
        """
        Args:
        and_ : ( None ) An AND term that is added to the search query. For instance, if your searchTerm is 'lebron james,
                    steph curry' and your and term is 'GOAT,' the posts must match ('lebron james' AND 'GOAT') OR
                    ('steph curry' AND 'GOAT')
        not_ : ( None ) A corollary to and_, not_ will exclude all posts matching this word.
        count : ( positive int or -1, default 10 ) The number of posts to return. -1 means to return all available.
                    If requesting more than 100 posts, batchSize must be set.
        includeHistory : (None or True, default None (does not include)) Includes timestep data for growth of each post
                    returned.
        batchSize : ( 1-100, default 100 ) Number of posts to return at most per call to the endpoint. Between 1-100.
        startDate : ( 0000-00-00 ) The earliest date at which a post could be posted. Time zone is UTC. Format is
                    “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00). This must be before endDate.
                    Timeframe and startDate are mutually exclusive; if both are passed, startDate will be preferred.
        endDate : ( 0000-00-00, default now ) The latest date at which a post could be posted. Time zone is UTC. Format is
                    “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00).
        inAccountIds : ( None ) A comma-separated list of the IDs of accounts to search within.
        inListIds : ( None ) A comma-separated list of the IDs of lists to search within.
        minInteractions : ( None, default 0 ) If set, will exclude posts with total interactions below this threshold.
        minSubscriberCount : ( None, default 0 ) The minimum number of subscribers an account must have to be included
                    in the search results.
        notInAccountIds : ( None ) A comma-separated list of the IDs of accounts to exclude. This behaves the same as
                    notInListIds, except with specific accounts.
        notinListIds : ( None ) A comma-separated list of the the IDs of lists to exclude from results. For instance, if
                    don't want to see news outlet mentions of your search term, 'Lebron James,' you could exclude your
                    sports publishers list.
        notinTitle : ( None ) Exclude all posts whose account title matches this term. E.g. search for "CrowdTangle" but
                    ignore any accounts that include the word "CrowdTangle" to see what other accounts are posting.
        offset : ( >= 0, default 0 ) The number of posts to offset (generally used for pagination). Pagination links will also be
                    provided in the response.
        platforms : ( facebook,instagram, default None i.e. all platforms ) The platforms from which to retrieve posts.
                    This value can be comma-separated.
        searchTerm : ( None ) Returns only posts that match this search term. Terms AND automatically. Separate with
                    commas for OR, use quotes for phrases. E.g. CrowdTangle API -> AND. CrowdTangle, API -> OR.
                    "CrowdTangle API" -> AND in that exact order.
        searchField : ( text_fields_and_image_text, include_query_strings , text_fields_only , account_name_only,
                    image_text_only, default text_fields_and_image_text )  	This allows you to search image text, URLs
                    with query strings, and account names, in addition to text fields only or both text fields and
                    image text.
        sortBy : ( date, interaction_rate, overperforming, total_interactions, underperforming, default overperforming )
                    The method by which to filter and order posts. If you do not set this parameter, it will default to
                    sorting by overperforming.
        timeframe : ( None, default 6 HOUR ) The interval of time to consider from the endDate. Timeframe and startDate
                    are mutually exclusive; if both are passed, startDate will be preferred.
        types : ( episode, extra_clip, link, live_video, live_video_complete, live_video_scheduled, native_video, photo,
                    status, trailer, video, vine, youtube, default None, i.e. all ) The types of post to include. These
                    can be separated by commas to include multiple types. If you want all live videos (whether currently
                     or formerly live), be sure to include both live_video and live_video_complete.
        verifiedOnly : ( False ) Limit results to verified accounts only. Note, this only applies to platforms that
                    supply information about verified accounts.
        language : ( None, i.e. all languages ) Exceptions: Some languages require more than two characters: Chinese
                    (Simplified) is zh-CN and Chinese (Traditional) is zh-TW.

        Returns:
        iterator of posts (dict)

        Example use:

        from api import API
        api = API()
        list_ids = [12345, ] # your lists
        search_term = "pytangle"
        for n, a_post in enumerate(api.posts(inListIds=list_ids,
                                             count=-1,
                                             batchSize=100,
                                             sortBy='date',
                                             startDate='2020-01-01',
                                             endDate='2020-06-30',
                                             searchTerm=search_term,
                                             )):
            # do something with the post
            if not n % 1000:
                print(n)
        """
        params = dict(
            token=self._token,
            and_=and_,
            not_=not_,
            count=count,
            includeHistory=includeHistory,
            batchSize=batchSize,
            startDate=startDate,
            endDate=endDate,
            inAccountIds=inAccountIds,
            inListIds=inListIds,
            minInteractions=minInteractions,
            minSubscriberCount=minSubscriberCount,
            notInAccountIds=notInAccountIds,
            notinListIds=notinListIds,
            notinTitle=notinTitle,
            offset=offset,
            platforms=platforms,
            searchField=searchField,
            searchTerm=searchTerm,
            sortBy=sortBy,
            timeframe=timeframe,
            types=types,
            verifiedOnly=verifiedOnly,
            language=language,
        )
        yield from Paginator(endpoint=SearchEndpoint(args=remove_null_values_from_dict(params)))

    def leaderboard(
            self,
            accountIds=None,
            count=50,
            batchSize=100,
            startDate=None,
            endDate=None,
            listId=0,
            offset=0,
            orderBy="desc",
            sortBy="total_interactions",
    ):
        """
        Args:
        accountIds : ( None ) A list of CrowdTangle accountIds to retrieve leaderboard data for. These should be
                    provided comma-separated. This and listId are mutually exclusive; if both are sent, accountIds will
                     be preferred.
        count : ( positive int or -1, default 50 ) The number of AccountStatistics to return. -1 means to return all available.
                    If requesting more than 100 AccountStatistics, batchSize must be set.
        batchSize : ( 1-100, default 100 ) Number of AccountStatistics to return at most per call to the endpoint. Between 1-100.
        startDate : ( 0000-00-00, default one day earlier than endDate ) The startDate of the leaderboard rage. Time
                    zone is UTC. Format is “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00). This must
                    be before endDate.
        endDate : ( 0000-00-00, default now ) The endDate of the leaderboard range. Time zone is UTC. Format is
                    “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00).
        listId : ( 0, i.e. the entire dashboard ) The list of the leaderboard to retrieve. This and accountIds are
                    mutually exclusive; if both are sent, accountIds will be preferred.
        offset : ( >= 0, default 0 ) The number of rows to offset (generally used for pagination). Pagination links
                    will also be provided in the response.
        orderBy : ( default desc ) the order of the sort.
        sortBy : ( total_interactions, interaction_rate, default total_interactions ) The method by which the
                    accountStatistics are sorted.

        Returns:
        iterator of accounts (dict)

        Example use:
        from api import API
        api = API()

        # get the first 5 entries in the leaderboard for the current dashboard
        for a_leaderboard in api.leaderboard(count=5):
            print(a_leaderboard)
        """
        params = dict(
            token=self._token,
            accountIds=accountIds,
            count=count,
            batchSize=batchSize,
            startDate=startDate,
            endDate=endDate,
            listId=listId,
            offset=offset,
            orderBy=orderBy,
            sortBy=sortBy,
        )
        yield from Paginator(endpoint=LeaderboardEndpoint(args=remove_null_values_from_dict(params)))

    def lists(
            self,
    ):
        """
        Retrieve the lists, saved searches and saved post lists of the dashboard associated with the token sent in.

        Returns:
        iterator of lists (dict)
            
        Example use:
        from api import API
        api = API()
        # fetch all lists linked to the current dashboard
        for a_list in api.lists():
            print(a_list)

        """
        params = dict(
            token=self._token,
        )
        yield from Paginator(endpoint=ListsEndpoint(args=remove_null_values_from_dict(params)))

    def links(
            self,
            count=100,
            includeHistory=None,
            batchSize=100,
            startDate=None,
            endDate=None,
            sortBy="date",
            offset=0,
            link=None,
            includeSummary=False,
            platforms=None,
    ):
        """
        Args:
        count : ( positive int or -1, default 100 ) The number of posts to return. -1 means to return all available.
                    If requesting more than 100 posts, batchSize must be set.
        includeHistory : (None or True, default None (does not include)) Includes timestep data for growth of each post
                    returned.
        batchSize : ( 1-100, default 100 ) Number of posts to return at most per call to the endpoint. Between 1-100.
        startDate : ( 0000-00-00 ) The earliest date at which a post could be posted. Time zone is UTC. Format is
                    “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00).
        endDate : ( default now ) The latest date at which a post could be posted. Time zone is UTC. Format is
                    “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd”.
        sortBy : ( date, subscriber_count, total_interactions, default date ) The method by which to order posts (defaults to the most
                    recent). If subscriber_count, a startDate is required.
        offset : ( >= 0, default 0 ) The number of posts to offset (generally used for pagination). Pagination links will also be
                    provided in the response.
        link : ( None ) The link to query by. Required.
        includeSummary : ( default False ) Adds a "summary" section with AccountStatistics for each platform that has posted this
                    link. It will look beyond the count requested to summarize across the time searched. Requires a value
                    for startDate.
        platforms : ( facebook,instagram, default None i.e. all platforms ) The platforms from which to retrieve links. This value can be comma-separated.

        Returns:
        iterator of posts (dict)
            
        Example use:
        from api import API
        api = API()

        # get the top 5 sharers of a link
        an_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        for a_post in api.links(count=5, link=an_url):
            print(a_post)

        """
        params = dict(
            token=self._token,
            count=count,
            includeHistory=includeHistory,
            batchSize=batchSize,
            startDate=startDate,
            endDate=endDate,
            sortBy=sortBy,
            offset=offset,
            link=link,
            includeSummary=includeSummary,
            platforms=platforms,
        )
        yield from Paginator(endpoint=LinksEndpoint(args=remove_null_values_from_dict(params)))

    def accounts_in_list(
            self,
            listId,
            count=10,
            batchSize=100,
            offset=0,
    ):
        """
        Args:
        listId : ( int ) The id of the list for which to retrieve accounts. This is provided as a path variable in the URL.
        count : ( positive int or -1, default 10 ) The number of accounts to return. -1 means to return all available.
                If requesting more than 100 accounts, batchSize must be set.
        batchSize : ( 1-100, default 100 ) Number of accounts to return at most per call to the endpoint. Between 1-100.
        offset : ( >= 0, default 0 ) The number of accounts to offset (generally used for pagination). Pagination links will also
                    be provided in the response.

        Returns:
        iterator of accounts (dict)
            
        Example use:

        from api import API
        api = API()

        # get information on an account
        list_id = a_list['id']
        for an_account in api.accounts_in_list(count=5, listId=list_id):
            print(an_account)

        """
        params = dict(
            token=self._token,
            count=count,
            batchSize=batchSize,
            offset=offset,
            listId=listId,
        )
        yield from Paginator(endpoint=AccountsEndpoint(args=remove_null_values_from_dict(params)))
