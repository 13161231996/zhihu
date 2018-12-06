#coding: utf-8
import scrapy
from scrapy import FormRequest,Request
from lxml import etree
import json
import redis,time,random
from chongxie.items import ZhihuspiderItem

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/topics']
    topic_question = 'https://www.zhihu.com/api/v4/topics/{}/feeds/essence?limit={}&offset={}'
    topic_anwser ='https://www.zhihu.com/api/v4/questions/{}/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B*%5D.topics&offset={}&limit={}&sort_by=default'
    topic_comment ='https://www.zhihu.com/api/v4/answers/{}/comments?include=data%5B*%5D.author%2Ccollapsed%2Creply_to_author%2Cdisliked%2Ccontent%2Cvoting%2Cvote_count%2Cis_parent_author%2Cis_author%2Calgorithm_right&order=normal&limit=20&offset={}&status=open'
    # def ipdaili(self):
    #     r = redis.Redis(host='47.75.188.8',port=6379,db=0)
    #     ip_list = r.lrange('ip_pool',0,-1)
    #     if ip_list ==[]:
    #         time.sleep(5)
    #         print('数据库没有ip')
    #         self.ipdaili()
    #     i =random.choice(ip_list)
    #     print(i)
    #     con = i.decode('utf-8')
    #     data = eval(con)
    #     pro_ip = 'http://'+data["ip"]+':'+str(data["port"])
    #     return pro_ip
    # def start_requests(self):
    #     yield Request(url=self.start_urls[0],meta={"proxy":self.ipdaili()},callback=self.parse)
    def parse(self, response):
        # 父话题的 url
        topic_url = "https://www.zhihu.com/node/TopicsPlazzaListV2"
        topics = response.xpath('//div[@class="zm-topic-cat-page"]/ul/li')
        print(topics)
        name = topics[0].xpath('./a/text()').extract_first()
        print(name)
        topic_id = topics[0].xpath('./@data-id').extract_first()
        print(topic_id)
        unicornHeader = {
            'origin': 'https: // www.zhihu.com',
            'referer': 'https://www.zhihu.com/topics',
        }
        params = {"topic_id":topic_id,"offset":0,"hash_id":""}
        yield FormRequest(url=topic_url,headers = unicornHeader,method='POST',formdata={"method": "next","params": json.dumps(params)},meta={"offset":0,"topic_id":topic_id,"name":name},callback = self.parse_topic,dont_filter=True)

    def parse_topic(self, response):
        print(response.text)
        offset = response.meta.get("offset")
        topic_id = response.meta.get("topic_id")
        name = response.meta.get("name")
        # 解析父话题页面
        json_info = json.loads(response.text)  # 此时json_info为一个字典
        msg_info = json_info['msg']  # 键为 msg 的值对应为一个列表
        offset += len(msg_info)
        for msg in msg_info:
            html = etree.HTML(msg)
            href = html.xpath('.//a[@target="_blank"]/@href')
            num = href[0].split('/')[-1]
            topic_name = html.xpath('.//strong/text()')
            yield Request(url=self.topic_question.format(num,10,0),meta={"offset":0,"limit":10,"num":num,'name':name,'topic_name':topic_name[0]},callback=self.parse_question,dont_filter=True)
        if not len(msg_info)<20:
            yield FormRequest("https://www.zhihu.com/node/TopicsPlazzaListV2",callback=self.parse_topic,dont_filter=True,meta={"offset":offset,"topic_id":topic_id,"name":name},
                    formdata={"method": "next","params": json.dumps({"topic_id":topic_id,"offset":offset,"hash_id":""})})
        else:
            print("name:{},topic_num:{}".format(name,offset))


    def parse_question(self, response):
        offset = response.meta.get('offset')
        limit = response.meta.get('limit')
        num = response.meta.get('num')
        name = response.meta.get("name")
        topic_name = response.meta.get("topic_name")
        # 解析“精华问题”页面，
        json_info = json.loads(response.text)
        data_info = json_info['data']
        offset += len(data_info)
        canshu1 = {'include':'data[*].is_normal,admin_closed_comment, reward_info, is_collapsed, annotation_action, annotation_detail, collapse_reason, is_sticky, collapsed_by, suggest_edit, comment_count, can_comment, content, editable_content, voteup_count, reshipment_settings, comment_permission, created_time, updated_time, review_info, relevant_info, question, excerpt, relationship.is_authorized, is_author, voting, is_thanked, is_nothelp;data[*].mark_infos[*].url;data[*].author.follower_count, badge[*].topics',
                    'offset':0,
                    'limit':3,
                    'sort_by':'default'
        }
        # 获取“问题”的页面链接所需的参数，构造页面链接，交给parse_anwser函数处理，获取该问题的所有答案信息
        for data in data_info:
            if 'zhuanlan' in data['target']['url']:
                continue
            anwser_id = data['target']['question']['id']
            print('2222222222222',anwser_id)
            yield Request(self.topic_anwser.format(anwser_id,0,5),callback=self.parse_anwser,dont_filter=True,
                                meta={"offset":0,"limit":5,"anwser_id":anwser_id,"name":name})#添加name

    def parse_anwser(self, response):
        print('已经到达答案页面')
        name = response.meta.get('name')
        topic_name = response.meta.get('topic_name')
        # print('aaaaaaaa', topic_name)
        offset = response.meta.get('offset')
        limit = response.meta.get('limit')
        anwser_id = response.meta.get('anwser_id')
        # 解析获得的单个精华问题的答案页面
        json_info = json.loads(response.text)
        data_info = json_info['data']
        offset = offset + len(data_info)
        print('1111111111111111111111111111111111111111111111')
        # 解析含有答案内容的 json 内容
        for data in data_info:
            # item = ZhihuspiderItem()
            # item['huati'] = name                                    #话题
            # item['question'] = data['question']['title']            # 问题题目
            # item['name'] = data['author']['name']                   # 答题人id
            # item['voteup_count'] = data['voteup_count']             # 赞了该答案的人数
            # item['content'] = data['content']                       # 答案内容
            # item['answer_id'] = data["id"]                          # 该回答id（唯一标识）
            # # print(item)
            # yield item
            print('解析含有答案的内容')
            answer_url = data["id"]  # 该回答id

            com_offset = 0
            comment_text = ''
            yield Request(self.topic_comment.format(answer_url, str(com_offset)), callback=self.parse_comment,
                          dont_filter=True,
                          meta={"com_offset": com_offset, "data_info": data, 'name': name, "answer_url": answer_url,
                                "comment_text": comment_text})

        # 如果获取的答案数小于总的答案数，就继续获取
        paging_info = json_info['paging']
        if offset < paging_info['totals']:
            yield Request(self.topic_anwser.format(anwser_id, offset, limit), callback=self.parse_anwser,
                          dont_filter=True,
                          meta={"offset": offset, "limit": limit, "anwser_id": anwser_id, 'name': name})
        else:
            print("anwser_id:{},offset:{}".format(anwser_id, offset))

    def parse_comment(self, response):
        name = response.meta.get('name')
        print('222222222222222222222222', name)
        data = response.meta.get('data_info')
        com_offset = response.meta.get('com_offset')
        answer_url = response.meta.get('answer_url')
        comment_text = response.meta.get('comment_text')

        # 解析获得的单个答案的评论json
        json_com_info = json.loads(response.text)
        totals = json_com_info["common_counts"]
        com_info = json_com_info['data']
        if com_info != '':

            # 获取当前页内容
            for comment in com_info:
                com_content = comment["content"]
                author = comment["author"]["member"]["name"]
                if "reply_to_author" in comment.keys():
                    member = comment["reply_to_author"]["member"]["name"]
                    comment_text += author + ' 回复 ' + member + ':' + com_content + '\n'
                else:
                    comment_text += author + ':' + com_content + '\n'
            if totals > 20 and com_offset + 20 < totals:
                # 获取下一页评论
                com_offset += 20
                yield Request(self.topic_comment.format(answer_url, str(com_offset)), callback=self.parse_comment,
                              dont_filter=True,
                              meta={"com_offset": com_offset, "data_info": data, 'name': name, "answer_url": answer_url,
                                    "comment_text": comment_text})

        contents = etree.HTML(data['content'])
        con = contents.xpath('.//text()')
        text = ''
        for content in con:
            text += content
            print('22222222222222222222222')
            # 已经获取所有评论，存入数据库
            item = ZhihuspiderItem()
            item['huati'] = name  # 话题
            item['answer_id'] = answer_url  # 该回答id（唯一标识）
            item['comment'] = comment_text  # 评论
            item['question'] = data['question']['title']  # 问题题目
            item['author'] = data['author']['name']  # 答题人id
            item['voteup_count'] = data['voteup_count']  # 赞了该答案的人数
            item['content'] = text  # 答案内容
            yield item
