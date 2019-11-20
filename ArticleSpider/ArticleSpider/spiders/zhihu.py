# -*- coding: utf-8 -*-
import datetime
import json

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from mouse import move, click
import pickle
import base64
from zheye import zheye
from urllib import parse
import re
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem

class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    start_answer_url = "https://www.zhihu.com/api/v4/questions/{}/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B*%5D.topics&offset={}&limit={}&sort_by=default&platform=desktop"

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        """
        Scrape all urls in the webpage, and parse each one of them
        if the format of the url is /question/xxx, pass it to parse_question
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # pass urls that contain questions to parse_question
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
            else:
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)


    def parse_question(self, response):
        match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        question_id = match_obj.group(2)

        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", "h1.QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
        item_loader.add_css("watch_user_num", ".NumberBoard-itemValue::text")
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

        question_item = item_loader.load_item()

        yield scrapy.Request(self.start_answer_url.format(question_id, 3, 5), headers=self.headers,
                             callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # deal with each answer of each question
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]
        # print(ans_json["data"])

        # fields that are of interest
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["question_title"] = answer["question"]["title"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)


    # Uncomment the following code if it needs verification

    # def start_requests(self):
    #     chrome_option = Options()
    #     chrome_option.add_argument("--disable-extensions")
    #     chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    #
    #     browser = webdriver.Chrome(executable_path="C:/Users/F_RPG/Desktop/chromedriver.exe",
    #                                chrome_options=chrome_option)
    #     try:
    #         browser.maximize_window()
    #     except:
    #         pass
    #
    #     browser.get("https://www.zhihu.com/signin")
    #     browser.find_element_by_css_selector("div.SignFlow-tabs > div:nth-child(2)").click()
    #     browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
    #     browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("example@email.com")
    #     browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
    #     browser.find_element_by_css_selector(".SignFlow-password input").send_keys("password")
    #
    #     browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
    #     time.sleep(10)
    #
    #     login_success = False
    #     while not login_success:
    #         try:
    #             notify_ele = browser.find_element_by_class_name("Popover PushNotifications AppHeader-notifications")
    #             login_success = True
    #         except:
    #             pass
    #
    #         try:
    #             english_captcha_element = browser.find_element_by_class_name("Captcha-englishImg")
    #         except:
    #             english_captcha_element = None
    #
    #         try:
    #             chinese_captcha_element = browser.find_element_by_class_name("Captcha-chineseImg")
    #         except:
    #             chinese_captcha_element = None
    #
    #         if chinese_captcha_element:
    #             x_related = chinese_captcha_element.location["x"]
    #             y_related = chinese_captcha_element.location["y"]
    #             browser_navigation_panel_height = browser.execute_script(
    #                 "return window.outerHeight - window.innerHeight;"
    #             )
    #
    #             base64_text = chinese_captcha_element.get_attribute("src")
    #             code = base64_text.replace("data:image/jpg;base64,").replace("%0A", "")
    #             fh = open("yzm_cn.jpeg", "wb")
    #             fh.write(base64.b64decode(code))
    #             fh.close()
    #
    #             z = zheye()
    #             positions = z.Recognize('yzm_cn.jpeg')
    #             last_position = []
    #             if len(positions) >= 2:
    #                 if positions[0][1] > positions[1][1]:
    #                     last_position.append([positions[1][1], positions[1][0]])
    #                     last_position.append([positions[0][1], positions[0][0]])
    #                 else:
    #                     last_position.append([positions[0][1], positions[0][0]])
    #                     last_position.append([positions[1][1], positions[1][0]])
    #
    #                 first_position = [int(last_position[0][0]/2), int(last_position[0][1]/2)]
    #                 second_position = [int(last_position[1][0] / 2), int(last_position[1][1] / 2)]
    #                 move(x_related + first_position[0], y_related + browser_navigation_panel_height + first_position[1])
    #                 click()
    #                 move(x_related + second_position[0], y_related + browser_navigation_panel_height + second_position[1])
    #                 click()
    #             else:
    #                 last_position.append([positions[0][1], positions[0][0]])
    #                 first_position = [int(last_position[0][0] / 2), int(last_position[0][1] / 2)]
    #                 move(x_related + first_position[0], y_related + browser_navigation_panel_height + first_position[1])
    #                 click()
    #
    #             browser.find_element_by_css_selector("div.SignFlow-tabs > div:nth-child(2)").click()
    #             browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
    #                 Keys.CONTROL + "a")
    #             browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
    #                 "example@email.com")
    #             browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
    #             browser.find_element_by_css_selector(".SignFlow-password input").send_keys("password")
    #
    #             browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
    #
    #         if english_captcha_element:
    #             base64_text = english_captcha_element.get_attribute("src")
    #             code = base64_text.replace('data:image/jpg;base64,', '').replace("%0A", "")
    #             # print code
    #             fh = open("yzm_en.jpeg", "wb")
    #             fh.write(base64.b64decode(code))
    #             fh.close()
    #
    #             from tools.yundama_requests import YDMHttp
    #             yundama = YDMHttp("da_ge_da1", "dageda", 3129, "40d5ad41c047179fc797631e3b9c3025")
    #             code = yundama.decode("yzm_en.jpeg", 5000, 60)
    #             while True:
    #                 if code == "":
    #                     code = yundama.decode("yzm_en.jpeg", 5000, 60)
    #                 else:
    #                     break
    #
    #             browser.find_element_by_xpath(
    #                 '//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[3]/div/div/div[1]/input').send_keys(
    #                 Keys.CONTROL + "a")
    #             browser.find_element_by_xpath(
    #                 '//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[3]/div/div/div[1]/input').send_keys(
    #                 code)
    #
    #             browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
    #                 Keys.CONTROL + "a")
    #             browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
    #                 "example@email.com")
    #             browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
    #             browser.find_element_by_css_selector(".SignFlow-password input").send_keys("password")
    #
    #             browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
