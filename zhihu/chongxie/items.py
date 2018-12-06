# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class ZhihuspiderItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    '''
    son_href = Field()
    son_name = Field()
    son_content = Field()
    topic_name = Field()

    title = Field()
    name = Field()
    question_id = Field()
    topic = Field()
    '''
    huati = Field()             # 话题
    question = Field()          # 问题题目
    author = Field()            # 答题人id
    content = Field()           # 答案内容
    voteup_count = Field()      # 赞了该答案的人数
    answer_id = Field()         # 该回答id（唯一标识）
    comment = Field()           # 评论

