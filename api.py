from connectivity import make_request, make_request_1_every_10s, iterate_request, make_request_1_every_30s


def lists(**args):
    response = make_request('https://api.crowdtangle.com/lists', args)
    return response['result']['lists']


def posts(**args):
    return iterate_request(args, 'https://api.crowdtangle.com/posts', 'posts', make_request_1_every_10s)


def links(**args):
    return iterate_request(args, 'https://api.crowdtangle.com/links', 'links', make_request_1_every_30s)


def leaderboard(**args):
    return iterate_request(args, 'https://api.crowdtangle.com/leaderboard', 'leaderboard', make_request_1_every_10s)


def search(**args):
    return iterate_request(args, 'https://api.crowdtangle.com/search', 'leaderboard', make_request_1_every_10s)


def accounts_in_list(**args):
    list_id = args.pop('listId')
    return iterate_request(args, 'https://api.crowdtangle.com/lists/{}/accounts'.format(list_id), 'accounts',
                           make_request_1_every_10s)


class API:
    def __init__(self, token):
        self._token = token

    def posts(
            self,
            listIds=None,
            startDate="0000 - 00 - 00",
            endDate="0000 - 00 - 00",
            sortBy="date",
            count=100,
            language=None,
            minInteractions=None,
            offset=0,
            searchTerm=None,
            timeframe=None,
            types="episode",
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
        listIds : ( None ) The IDs of lists or saved searches to retrieve. These can be separated by commas to include multiple lists.
        startDate : ( 0000-00-00 ) The earliest date at which a post could be posted. Time zone is UTC. Format is “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00). This must be before endDate. Timeframe and startDate are mutually exclusive; if both are passed, startDate will be preferred.
        endDate : ( 0000-00-00 ) The latest date at which a post could be posted. Time zone is UTC. Format is “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00).
        sortBy : ( date, interaction_rate, overperforming, total_interactions, underperforming ) The method by which to filter and order posts. If you do not set this parameter, it will default to sorting by overperforming.
        count : ( 1-100 ) The number of posts to return. Between 1-100.
        language : ( None ) Exceptions: Some languages require more than two characters: Chinese (Simplified) is zh-CN and Chinese (Traditional) is zh-TW.
        minInteractions : ( None ) If set, will exclude posts with total interactions below this threshold.
        offset : ( >= 0 ) The number of posts to offset (generally used for pagination). Pagination links will also be provided in the response.
        searchTerm : ( None ) Returns only posts that match this search term. Terms AND automatically. Separate with commas for OR, use quotes for phrases. E.g. CrowdTangle API -> AND. CrowdTangle, API -> OR. "CrowdTangle API" -> AND in that exact order.
        timeframe : ( Any valid SQL interval (No, we don't pass it through to our database. Don't be silly) ) The interval of time to consider from the endDate. Timeframe and startDate are mutually exclusive; if both are passed, startDate will be preferred. Depending on the number of posts, longer timeframes may not return within the timeout window. If you get a 504, try shortening your timeframe.
        types : ( episode, extra_clip, link, live_video, live_video_complete, live_video_scheduled, native_video, photo, status, trailer, tweet, video, vine, youtube ) The types of post to include. These can be separated by commas to include multiple types. If you want all live videos (whether currently or formerly live), be sure to include both live_video and live_video_complete. The "video" type does not mean all videos, it refers to videos that aren't native_video, youtube or vine (e.g. a video on Vimeo).
        weightAngry : ( 0-10 ) How much weight to give to each type of interaction. If you send in no weights, all weights will use the current dashboard defaults. If you send in at least one weight, all other weights will default to 0. Weights are multiplied by interaction counts: e.g. weightsComment at 1 and all others at 0 will find the most commented-on posts. weightLike at 1 and weightShare at 2 will give shares twice the impact as likes when computing scores.
        weightComment : ( 0-10 )
        weightHaha : ( 0-10 )
        weightLike : ( 0-10 )
        weightLove : ( 0-10 )
        weightSad : ( 0-10 )
        weightShare : ( 0-10 )
        weightView : ( 0-10 )
        weightWow : ( 0-10 )
        """
        params = dict(
            token=self._token,
            listIds=listIds,
            startDate=startDate,
            endDate=endDate,
            sortBy=sortBy,
            count=count,
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
        yield from posts(params)

    def search(
            self,
            and_=None,
            not_=None,
            count=100,
            startDate="0000 - 00 - 00",
            endDate="0000 - 00 - 00",
            inAccountIds=None,
            inListIds=None,
            minInteractions=None,
            minSubscriberCount=None,
            notInAccountIds=None,
            notinListIds=None,
            notinTitle=None,
            offset=0,
            platforms="facebook",
            searchTerm=None,
            sortBy="date",
            timeframe=None,
            types=None,
            verifiedOnly=False,
            language=None,
    ):
        """
        Args:
        and_ : ( None ) An AND term that is added to the search query. For instance, if your searchTerm is 'lebron james, steph curry' and your and term is 'GOAT,' the posts must match ('lebron james' AND 'GOAT') OR ('steph curry' AND 'GOAT')
        not_ : ( None ) A corollary to and_, not_ will exclude all posts matching this word.
        count : ( 1-100 ) The number of posts to return. Between 1-100.
        startDate : ( 0000-00-00 ) The earliest date at which a post could be posted. Time zone is UTC. Format is “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00). This must be before endDate. Timeframe and startDate are mutually exclusive; if both are passed, startDate will be preferred.
        endDate : ( 0000-00-00 ) The latest date at which a post could be posted. Time zone is UTC. Format is “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00).
        inAccountIds : ( None ) A comma-separated list of the IDs of accounts to search within.
        inListIds : ( None ) A comma-separated list of the IDs of lists to search within.
        minInteractions : ( None ) If set, will exclude posts with total interactions below this threshold.
        minSubscriberCount : ( None ) The minimum number of subscribers an account must have to be included in the search results.
        notInAccountIds : ( None ) A comma-separated list of the IDs of accounts to exclude. This behaves the same as notInListIds, except with specific accounts.
        notinListIds : ( None ) A comma-separated list of the the IDs of lists to exclude from results. For instance, if don't want to see news outlet mentions of your search term, 'Lebron James,' you could exclude your sports publishers list.
        notinTitle : ( None ) Exclude all posts whose account title matches this term. E.g. search for "CrowdTangle" but ignore any accounts that include the word "CrowdTangle" to see what other accounts are posting.
        offset : ( >= 0 ) The number of posts to offset (generally used for pagination). Pagination links will also be provided in the response.
        platforms : ( facebook,instagram ) The platforms from which to retrieve posts. This value can be comma-separated.
        searchTerm : ( None ) Returns only posts that match this search term. Terms AND automatically. Separate with commas for OR, use quotes for phrases. E.g. CrowdTangle API -> AND. CrowdTangle, API -> OR. "CrowdTangle API" -> AND in that exact order.
        sortBy : ( date, interaction_rate, overperforming, total_interactions, underperforming ) The method by which to filter and order posts. If you do not set this parameter, it will default to sorting by overperforming.
        timeframe : ( None ) The interval of time to consider from the endDate. Timeframe and startDate are mutually exclusive; if both are passed, startDate will be preferred.
        types : ( None ) The types of post to include. These can be separated by commas to include multiple types. If you want all live videos (whether currently or formerly live), be sure to include both live_video and live_video_complete.
        verifiedOnly : ( False ) Limit results to verified accounts only. Note, this only applies to platforms that supply information about verified accounts.
        language : ( None ) Exceptions: Some languages require more than two characters: Chinese (Simplified) is zh-CN and Chinese (Traditional) is zh-TW.
        """
        params = dict(
            token=self._token,
            and_=and_,
            not_=not_,
            count=count,
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
            searchTerm=searchTerm,
            sortBy=sortBy,
            timeframe=timeframe,
            types=types,
            verifiedOnly=verifiedOnly,
            language=language,
        )
        yield from search(params)

    def leaderboard(
            self,
            accountIds=None,
            count=100,
            startDate="0000 - 00 - 00",
            endDate="0000 - 00 - 00",
            listid=None,
            offset=0,
            orderBy="desc",
            sortBy="total_interactions",
    ):
        """
        Args:
        accountIds : ( None ) A list of CrowdTangle accountIds to retrieve leaderboard data for. These should be provided comma-separated. This and listId are mutually exclusive; if both are sent, accountIds will be preferred.
        count : ( 1-100 ) The number of AccountStatistics to return. Between 1-100.
        startDate : ( 0000-00-00 ) The startDate of the leaderboard rage. Time zone is UTC. Format is “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00). This must be before endDate.
        endDate : ( 0000-00-00 ) The endDate of the leaderboard range. Time zone is UTC. Format is “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00).
        listid : ( None ) The list of the leaderboard to retrieve. This and accountIds are mutually exclusive; if both are sent, accountIds will be preferred.
        offset : ( >= 0 ) The number of rows to offset (generally used for pagination). Pagination links will also be provided in the response.
        orderBy : ( desc ) the order of the sort.
        sortBy : ( total_interactions, interaction_rate ) The method by which the accountStatistics are sorted.
        """
        params = dict(
            token=self._token,
            accountIds=accountIds,
            count=count,
            startDate=startDate,
            endDate=endDate,
            listid=listid,
            offset=offset,
            orderBy=orderBy,
            sortBy=sortBy,
        )
        yield from leaderboard(params)

    def lists(
            self,
    ):
        """
        """
        params = dict(
            token=self._token,
        )
        return lists(params)

    def links(
            self,
            count=100,
            startDate="0000 - 00 - 00",
            endDate="0000 - 00 - 00",
            sortBy="date",
            offset=0,
            link=None,
            includeSummary=True,
            platforms="facebook",
    ):
        """
        Args:
        count : ( 1-100 ) The number of posts to return. Between 1-100.
        startDate : ( 0000-00-00 ) The earliest date at which a post could be posted. Time zone is UTC. Format is “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd” (defaults to time 00:00:00).
        endDate : ( 0000-00-00 ) The latest date at which a post could be posted. Time zone is UTC. Format is “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd”.
        sortBy : ( date, subscriber_count, total_interactions ) The method by which to order posts (defaults to the most recent). If subscriber_count, a startDate is required.
        offset : ( >= 0 ) The number of posts to offset (generally used for pagination). Pagination links will also be provided in the response.
        link : ( None ) The link to query by. Required.
        includeSummary : ( True ) Adds a "summary" section with AccountStatistics for each platform that has posted this link. It will look beyond the count requested to summarize across the time searched. Requires a value for startDate.

        platforms : ( facebook,instagram ) The platforms from which to retrieve links. This value can be comma-separated.
        """
        params = dict(
            token=self._token,
            count=count,
            startDate=startDate,
            endDate=endDate,
            sortBy=sortBy,
            offset=offset,
            link=link,
            includeSummary=includeSummary,
            platforms=platforms,
        )
        yield from links(params)

    def accounts_in_list(
            self,
            count=100,
            offset=0,
            listId=None,
    ):
        """
        Args:
        count : ( 1-100 ) The number of accounts to return.
        offset : ( >= 0 ) The number of accounts to offset (generally used for pagination). Pagination links will also be provided in the response.
        listId : ( None ) The id of the list for which to retrieve accounts. This is provided as a path variable in the URL.
        """
        params = dict(
            token=self._token,
            count=count,
            offset=offset,
            listId=listId,
        )
        yield from accounts_in_list(params)
