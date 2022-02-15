#!/usr/bin/python3
'''A module containing functions for working with the Reddit API.
'''
import re
import requests


BASE_URL = 'https://www.reddit.com'
'''Reddit's base API URL.
'''


def sort_histogram(histogram={}):
    '''Sorts and prints the given histogram.
    '''
    histogram = dict(filter(lambda x: x[1], histogram.items()))
    keys_all = map(lambda x: x.lower(),histogram.keys())
    histogram_aggregate = dict(map(
        lambda k: (k, histogram[k] * keys_all.count(k)),
        set(keys_all)
    ))
    histogram = histogram_aggregate
    histogram_items = histogram.items()
    histogram_items.sort(
        key=lambda x: x[0],
        reverse=False
    )
    histogram_items.sort(
        key=lambda x: x[1],
        reverse=True
    )
    histogram = dict(histogram_items)
    res_str = '\n'.join(
        map(
            lambda x: '{}: {}'.format(x[0], x[1]),
            histogram.items()
        )
    )
    print(res_str)
    return histogram


def count_words(subreddit, word_list, histogram={}, n=0, after=None):
    '''Counts the number of times each word in a given wordlist
    occurs in a given subreddit.
    '''
    api_headers = {
        'Accept': 'application/json',
        'User-Agent': ' '.join([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'AppleWebKit/537.36 (KHTML, like Gecko)',
            'Chrome/97.0.4692.71',
            'Safari/537.36',
            'Edg/97.0.1072.62'
        ])
    }
    sort = 'hot'
    limit = 30
    res = requests.get(
        '{}/r/{}/.json?sort={}&limit={}&count={}&after={}'.format(
            BASE_URL,
            subreddit,
            sort,
            limit,
            n,
            after if after else ''
        ),
        headers=api_headers,
        allow_redirects=False
    )
    if not histogram:
        histogram = dict(list(map(lambda x: (x, 0), word_list)))
        print(histogram.items())
    if res.status_code == 200:
        data = res.json()['data']
        posts = data['children']
        titles = list(map(lambda x: x['data']['title'], posts))
        histogram = dict(map(
            lambda x: x[1] + sum(map(
                lambda txt: len(
                    re.findall(
                        r'\s{}\s'.format(x[0]),
                        ' {} '.format(txt.replace(' ', '  ')),
                        re.IGNORECASE
                    )),
                titles
            )),
            histogram.items()
        ))
        if len(posts) >= limit and data['after']:
            return count_words(
                subreddit,
                histogram,
                n + len(posts),
                data['after']
            )
        else:
            if not histogram:
                return None
            return sort_histogram(histogram)
    else:
        if not histogram:
            return None
        return sort_histogram(histogram)