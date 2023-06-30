import requests

from .data import Data
from .. import exceptions
from .. import helpers


class Actions:
    def __init__(self, session, data: Data) -> None:
        self.data = data
        self.session = session

    def like_tweet(self, tweet_id: str) -> None:
        data = self.session.post(
            'https://twitter.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            json={"variables": {"tweet_id": tweet_id}, "queryId": "lI07N6Otwv1PhnEgXILM7A"}
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")

    def retweet(self, tweet_id: str) -> None:
        data = self.session.post(
            'https://twitter.com/i/api/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            json={
                "variables": {
                    "tweet_id": tweet_id,
                    "dark_request": False
                },
                "queryId": "ojPdsZsimiJrUGLR1sjUtA"
            }
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")

    def tweet(self, content: str, reply_tweet_id: str = None) -> None:
        payload = {
            "variables": {
                "tweet_text": content,
                "dark_request": False,
                "media": {
                    "media_entities": [],
                    "possibly_sensitive": False
                },
                "semantic_annotation_ids": []
            },
            "features": {
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_enhance_cards_enabled": False
            },
            "queryId": "GUFG748vuvmewdXbB5uPKg"
        }

        if reply_tweet_id:
            payload['variables']['reply'] = {}
            payload['variables']['reply']['in_reply_to_tweet_id'] = reply_tweet_id
            payload['variables']['reply']['exclude_reply_user_ids'] = []

        data = self.session.post(
            'https://twitter.com/i/api/graphql/GUFG748vuvmewdXbB5uPKg/CreateTweet',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            json=payload
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")

    def follow(self, user_id: str) -> None:
        data = self.session.post(
            'https://twitter.com/i/api/1.1/friendships/create.json',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            data={
                "include_profile_interstitial_type": "1",
                "include_blocking": "1",
                "include_blocked_by": "1",
                "include_followed_by": "1",
                "include_want_retweets": "1",
                "include_mute_edge": "1",
                "include_can_dm": "1",
                "include_can_media_tag": "1",
                "include_ext_has_nft_avatar": "1",
                "include_ext_is_blue_verified": "1",
                "include_ext_verified_type": "1",
                "include_ext_profile_image_shape": "1",
                "skip_status": "1",
                "user_id": user_id,
            }
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")

    def unfollow(self, user_id: str) -> None:
        data = self.session.post(
            'https://twitter.com/i/api/1.1/friendships/destroy.json',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            data={
                "include_profile_interstitial_type": "1",
                "include_blocking": "1",
                "include_blocked_by": "1",
                "include_followed_by": "1",
                "include_want_retweets": "1",
                "include_mute_edge": "1",
                "include_can_dm": "1",
                "include_can_media_tag": "1",
                "include_ext_has_nft_avatar": "1",
                "include_ext_is_blue_verified": "1",
                "include_ext_verified_type": "1",
                "include_ext_profile_image_shape": "1",
                "skip_status": "1",
                "user_id": user_id,
            }
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")

    def upload_media(self, media_path: str, proxy: str) -> str:
        media_size = helpers.get_file_size(media_path)
        media_checksum = helpers.get_file_checksum(media_path)

        data = self.session.post(
            f'https://upload.twitter.com/i/media/upload.json?command=INIT&total_bytes={str(media_size)}&media_type=image%2Fjpeg',
            headers=helpers.headers({
                "accept": "*/*",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            })
        )
        if data.status_code != 202:
            raise exceptions.TwitterHTTPException(f"Expected 202, got {data.status_code} ({data.text})")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")

        media_id = data.json()['media_id_string']

        data = requests.post(
            f'https://upload.twitter.com/i/media/upload.json?command=APPEND&media_id={media_id}&segment_index=0',
            headers=helpers.headers({
                "accept": "*/*",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            files={
                "media": open(media_path, 'rb')
            },
            cookies={
                "ct0": self.session.cookies.get('ct0'),
                "auth_token": self.session.cookies.get('auth_token')
            },
            proxies={
                "https": f"http://{proxy}",
                "http": f"http://{proxy}"
            }
        )
        if data.status_code != 204:
            raise exceptions.TwitterHTTPException(f"Expected 204, got {data.status_code} ({data.text})")

        data = self.session.post(
            f'https://upload.twitter.com/i/media/upload.json?command=FINALIZE&media_id={media_id}&original_md5={media_checksum}',
            headers=helpers.headers({
                "accept": "*/*",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            })
        )
        if data.status_code != 201:
            raise exceptions.TwitterHTTPException(f"Expected 201, got {data.status_code} ({data.text})")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")

        return media_id

    def follow_topic(self, topic_id: str) -> None:
        data = self.session.post(
            f'https://twitter.com/i/api/graphql/ElqSLWFmsPL4NlZI5e1Grg/TopicFollow',
            headers=helpers.headers({
                "accept": "*/*",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            json={"variables": {"topicId": topic_id}, "queryId": "ElqSLWFmsPL4NlZI5e1Grg"}
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code} ({data.text})")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")

    def fetch_timeline(self) -> list:
        data = self.session.get(
            f'https://twitter.com/i/api/graphql/zmpJ47b7DYqZ0sQzKJvbeA/HomeTimeline',
            headers=helpers.headers({
                "accept": "*/*",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            params={
                'variables': '{"count":20,"includePromotedContent":true,"latestControlAvailable":true,"requestContext":"launch","withCommunity":true}',
                'features': '{"rweb_lists_timeline_redesign_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":false,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_enhance_cards_enabled":false}',
            }
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code} ({data.text})")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")

        tweets = data.json()['data']['home']['home_timeline_urt']['instructions'][0]['entries']
        tweet_data = []
        for tweet in tweets:
            tweet = tweet['content'].get("itemContent", {}).get("tweet_results", {}).get("result", {})
            if tweet.get('rest_id'):
                tweet_id = tweet['rest_id']
                user_bio = tweet['core']['user_results']['result']['legacy']['description']
                user_name = tweet['core']['user_results']['result']['legacy']['name']
                tweet_content = tweet['legacy']['full_text']
                tweet_data.append({"user_name": user_name, "tweet_content": tweet_content, "tweet_id": tweet_id,
                                   "user_bio": user_bio})

        return tweet_data

    def fetch_connect_timeline(self) -> list:
        data = self.session.get(
            f'https://twitter.com/i/api/graphql/E4XpbntNRRRJHn2ONk-1_w/ConnectTabTimeline?variables=%7B%22count%22%3A20%2C%22context%22%3A%22%7B%7D%22%7D&features=%7B%22rweb_lists_timeline_redesign_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Afalse%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D&fieldToggles=%7B%22withArticleRichContentState%22%3Afalse%7D',
            headers=helpers.headers({
                "accept": "*/*",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            })
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code} ({data.text})")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")
        users = data.json()['data']['connect_tab_timeline']['timeline']['instructions'][2]['entries'][0]['content'][
            'items']
        user_ids = []
        for user_id in users:
            user_id = user_id['item']['itemContent']['user_results']['result'].get("rest_id")
            if user_id:
                user_ids.append(user_id)

        return user_ids

    def fetch_topics_picker(self) -> list:
        data = self.session.get(
            'https://twitter.com/i/api/graphql/McZ3yKuxYwCbxA6uaR8g9Q/TopicsPickerPage?variables=%7B%7D&features=%7B%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22rweb_lists_timeline_redesign_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Afalse%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D&fieldToggles=%7B%22withArticleRichContentState%22%3Afalse%7D',
            headers=helpers.headers({
                "accept": "*/*",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            })
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code} ({data.text})")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")
        topics = data.json()['data']['viewer']['topics_picker_page']['body']['timeline']['instructions'][2]['entries']
        topic_ids = []
        for category in topics:
            category = category['content']['items']
            for topic in category:
                if "categoryrecommendations" in topic['entryId']:
                    topic_id = topic['item']['itemContent']['content']['topic']['topic_id']
                    topic_ids.append(topic_id)
                elif "topicmodule" in topic['entryId']:
                    topic_id = topic['item']['itemContent']['topic']['topic_id']
                    topic_ids.append(topic_id)

        return topic_ids
