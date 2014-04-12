# -*- coding: utf-8 -*-
from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from models import Discussion, User, Group, Comment
from factories import GroupFactory, UserFactory, CommentFactory, DiscussionFactory
import simplejson as json
from datetime import datetime

# GROUP_ID = 47241470410797
# GROUP_NAME = u'Кока-Кола'
#
# GROUP_OPEN_ID = 53038939046008

GROUP1_ID = 47241470410797
GROUP_DISCUSSION1_ID = 62190641299501

GROUP2_ID = 53038939046008
GROUP_DISCUSSION2_ID = 62465446084728

GROUP3_ID = 53008333209712
GROUP_DISCUSSION_WITH_MANY_COMMENTS_ID = 62503929662320

class OdnoklassnikiDiscussionsTest(TestCase):

    def test_fetch_group_discussions(self):

        group = GroupFactory(id=GROUP3_ID)

        self.assertEqual(Discussion.objects.count(), 0)

        discussions = Discussion.remote.fetch(group=group, all=True)

        self.assertTrue(discussions.count() > 94)
        self.assertEqual(discussions.count(), Discussion.objects.count())
        self.assertEqual(discussions.count(), group.discussions.count())

    def test_fetch_discussion_comments(self):

        discussion = DiscussionFactory(id=GROUP_DISCUSSION_WITH_MANY_COMMENTS_ID, type='GROUP_TOPIC')

        self.assertEqual(Comment.objects.count(), 0)

        comments = discussion.fetch_comments(all=True)

        self.assertTrue(discussion.comments_count > 2900)
        self.assertEqual(discussion.comments_count, comments.count())
        self.assertEqual(discussion.comments_count, Comment.objects.count())
        self.assertEqual(discussion.comments_count, discussion.comments.count())

    def test_fetch_discussion(self):

        self.assertEqual(Discussion.objects.count(), 0)

        instance = Discussion.remote.fetch(id=GROUP_DISCUSSION1_ID, type='GROUP_TOPIC')

        self.assertEqual(Discussion.objects.count(), 1)
        self.assertEqual(instance.id, GROUP_DISCUSSION1_ID)
        self.assertEqual(instance.author, User.objects.get(pk=163873406852))
        self.assertEqual(instance.owner, Group.objects.get(pk=GROUP1_ID))
        self.assertTrue(isinstance(instance.entities, dict))

        instance = Discussion.remote.fetch(id=GROUP_DISCUSSION2_ID, type='GROUP_TOPIC')

        self.assertEqual(Discussion.objects.count(), 2)
        self.assertEqual(instance.id, GROUP_DISCUSSION2_ID)
        self.assertEqual(instance.author, instance.owner)
        self.assertEqual(instance.owner, Group.objects.get(pk=GROUP2_ID))
        self.assertTrue(isinstance(instance.entities, dict))

    def test_parse_discussion(self):

        response = u'''{"discussion": {
                 "attrs": {"flags": "c,l,s"},
                 "creation_date": "2013-10-12 14:29:26",
                 "last_activity_date": "2013-10-12 14:29:26",
                 "last_user_access_date": "2013-10-12 14:29:26",
                 "like_count": 1,
                 "liked_it": false,
                 "message": "Topic in the {group:47241470410797}Кока-Кола{group} group",
                 "new_comments_count": 0,
                 "object_id": "62190641299501",
                 "object_type": "GROUP_TOPIC",
                 "owner_uid": "163873406852",
                 "ref_objects": [{"id": "47241470410797",
                                   "type": "GROUP"}],
                 "title": "Кока-Кола  один из спонсоров  Олимпиады в Сочи.  Хотелось бы  видеть фото- и видео-  репортажи с Эстафеты  олимпийского огня !",
                 "total_comments_count": 137},
                 "entities": {"groups": [{"main_photo": {"id": "507539161645",
                                                    "pic128x128": "http://itd0.mycdn.me/getImage?photoId=507539161645&photoType=23&viewToken=a6WsJVtOYvuLUbMSMQVMGg",
                                                    "pic50x50": "http://groupava2.mycdn.me/getImage?photoId=507539161645&photoType=4&viewToken=a6WsJVtOYvuLUbMSMQVMGg",
                                                    "pic640x480": "http://dg54.mycdn.me/getImage?photoId=507539161645&photoType=0&viewToken=a6WsJVtOYvuLUbMSMQVMGg"},
                                    "name": "Кока-Кола",
                                    "uid": "47241470410797"}],
                       "themes": [{"id": "62190641299501",
                                    "title": "Кока-Кола  один из спонсоров  Олимпиады в Сочи.  Хотелось бы  видеть фото- и видео-  репортажи с Эстафеты  олимпийского огня !"}],
                       "users": [{"first_name": "Любовь",
                                   "gender": "female",
                                   "last_name": "Гуревич",
                                   "pic128x128": "http://umd2.mycdn.me/getImage?photoId=432276861828&photoType=6&viewToken=P_qCWfSCiGBGVoiqWQMgsw",
                                   "pic50x50": "http://i508.mycdn.me/getImage?photoId=432276861828&photoType=4&viewToken=P_qCWfSCiGBGVoiqWQMgsw",
                                   "pic640x480": "http://uld9.mycdn.me/getImage?photoId=432276861828&photoType=0&viewToken=P_qCWfSCiGBGVoiqWQMgsw",
                                   "uid": "163873406852"}]}}'''
        instance = Discussion()
        instance.parse(json.loads(response))
        instance.save()

        self.assertEqual(instance.id, 62190641299501)
        self.assertEqual(instance.type, 'GROUP_TOPIC')
        self.assertEqual(instance.message, u"Topic in the {group:47241470410797}Кока-Кола{group} group")
        self.assertEqual(instance.title, u"Кока-Кола  один из спонсоров  Олимпиады в Сочи.  Хотелось бы  видеть фото- и видео-  репортажи с Эстафеты  олимпийского огня !")
        self.assertEqual(instance.new_comments_count, 0)
        self.assertEqual(instance.comments_count, 137)
        self.assertEqual(instance.likes_count, 1)
        self.assertEqual(instance.liked_it, False)
        self.assertEqual(instance.author, User.objects.get(pk=163873406852))
        self.assertEqual(instance.owner, Group.objects.get(pk=47241470410797))
        self.assertTrue(isinstance(instance.last_activity_date, datetime))
        self.assertTrue(isinstance(instance.last_user_access_date, datetime))
        self.assertTrue(isinstance(instance.date, datetime))
        self.assertTrue(isinstance(instance.entities, dict))
        self.assertTrue(isinstance(instance.attrs, dict))

    def test_parse_comment(self):

        response = u'''{"attrs": {"flags": "l,s"},
            "author_id": "538901295641",
            "date": "2014-04-11 12:53:02",
            "id": "MTM5NzIwNjM4MjQ3MTotMTU5NDE6MTM5NzIwNjM4MjQ3MTo2MjUwMzkyOTY2MjMyMDox",
            "like_count": 123,
            "liked_it": false,
            "reply_to_comment_id": "MTM5NzIwNjMzNjI2MTotODE0MzoxMzk3MjA2MzM2MjYxOjYyNTAzOTI5NjYyMzIwOjE=",
            "reply_to_id": "134519031824",
            "text": "наверное и я так буду делать!",
            "type": "ACTIVE_MESSAGE"}'''
        comment = CommentFactory(id='MTM5NzIwNjMzNjI2MTotODE0MzoxMzk3MjA2MzM2MjYxOjYyNTAzOTI5NjYyMzIwOjE=')
        author = UserFactory(id=134519031824)
        discussion = DiscussionFactory()
        instance = Comment(discussion=discussion)
        instance.parse(json.loads(response))
        instance.save()

        self.assertEqual(instance.id, 'MTM5NzIwNjM4MjQ3MTotMTU5NDE6MTM5NzIwNjM4MjQ3MTo2MjUwMzkyOTY2MjMyMDox')
        self.assertEqual(instance.type, 'ACTIVE_MESSAGE')
        self.assertEqual(instance.text, u"наверное и я так буду делать!")
        self.assertEqual(instance.likes_count, 123)
        self.assertEqual(instance.liked_it, False)
        self.assertEqual(instance.author, User.objects.get(pk=538901295641))
        self.assertEqual(instance.reply_to_comment, comment)
        self.assertEqual(instance.reply_to_author, User.objects.get(pk=134519031824))
        self.assertTrue(isinstance(instance.date, datetime))
        self.assertTrue(isinstance(instance.attrs, dict))
