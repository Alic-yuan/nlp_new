# -*- coding:utf-8 -*-
'''
@Author: yanwii
@Date: 2018-08-03 13:55:25

准备评估的数据
'''
import os
import pydat
import sys
import re

class PrepareEvaData(object):
    
    def __init__(self):
        self.tag_file_io = open("data/dev", "w")

    def read(self, file_name, encoding="utf-8"):
        with open(file_name, "rb") as fopen:
            return fopen.read().decode("gbk")
            # return fopen.read().decode("gb2312").encode("utf-8").decode("utf-8")
    
    def make_dat(self, file_name):
        self.pro_dat = pydat.Dat()
        with open(file_name, encoding="gbk") as fopen:
            lines = fopen.readlines()
            for line in lines:
                try:
                    entity, etype = line.split("|")
                    entity = entity.strip()
                    etype = etype.strip()
                except Exception:
                    continue
                if etype == "PRO":
                    self.pro_dat.add_word(entity)
            self.pro_dat.make()

    def find_tag(self, entity_type, tags, news):
        entities = []
        if entity_type == "PRO":
            entities = self.pro_dat.search(news).get("entities", [])
        # elif entity_type == "PER":
        #     entities = self.per_dat.search(news).get("entities", [])
        # elif entity_type == "ORG2":
        #     entities = self.org2_dat.search(news).get("entities", [])
        # elif entity_type == "S-ORG":
        #     entities = self.s_org_dat.search(news).get("entities", [])
        #     entities = self.valid_check(entities, news)
        return entities

    def valid_check(self, entities, news):
        valid_data = []
        threshold = 10
        for entity in entities:
            word = entity.get("entity")
            stop = entity.get("end")

            if stop + threshold > len(news):
                content = "pass"
            else:
                content = news[stop:stop+threshold]
            if re.findall(r"(有限[责任]*公司)", content):
                continue
            valid_data.append(entity)
        return valid_data

    def tag_data(self, entities, entity_type, tags):
        for entity in entities:
            begin = entity.get("begin")
            end = entity.get("end")
            if tags[begin:end] == ["O"] * (end - begin):
                tag = ["I-{}".format(entity_type)] * (end - begin)
                tag[0] = "B-{}".format(entity_type)
                tag[-1] = "E-{}".format(entity_type)
                tags = tags[:begin] + tag + tags[end:]
        return tags

    def load_tag_data(self, file_path):
        tag_files = []
        files = os.listdir(file_path)
        for file in files:
            if "entity" in file:
                continue
            news_file = os.path.join(file_path, file)
            tag_files.append(news_file)
        return tag_files

    def step(self, tag_file, found_tags=["ORG", "PER", "S-ORG"]):
        news_file = tag_file
        print(news_file)
        try:
            news = self.read(news_file, "gbk")
            print(news)
        except Exception as error:
            return
        for sentence in news.split(u"。"):
            sentence = re.sub(r"\s+", "", sentence)
            if not sentence:
                continue
            tags = ["O"] * len(sentence)
            origin_tags = ["O"] * len(sentence)
            for entity_type in found_tags:
                entities = self.find_tag(entity_type, tags, sentence)
                tags = self.tag_data(entities, entity_type, tags)
                tagged_data = list(zip(sentence, tags))
            if tags != origin_tags:
                self.save(tagged_data)

    def save(self, tag_data):
        for i in tag_data:
            self.tag_file_io.write("{} {}\n".format(
                i[0], i[1]
            ))
        self.tag_file_io.write("。\nend\n")

    def main(self, tag_file_path):
        # tag_file_path = "tag_data/20180806"
        self.make_dat(tag_file_path + "/entity.txt.txt")

        tag_files = self.load_tag_data(
            tag_file_path
        )
        for tag_file in tag_files:
            self.step(tag_file, ["PRO"])
            # self.step(tag_file, ["S-ORG"])

if __name__ == "__main__":
    ped = PrepareEvaData()
    assert len(sys.argv) >= 2, Exception("请输入待处理的文件夹名")
    ped.main(sys.argv[1])