# -*- coding: utf-8 -*-

import jieba
import logging

def main():


    # jieba custom setting.
    jieba.set_dictionary('jieba_dict/dict.txt.big')
    jieba.load_userdict("jieba_dict/userdict.txt")
    jieba.load_userdict("jieba_dict/cus_dict/movie.txt")
    jieba.load_userdict("jieba_dict/cus_dict/music.txt")
    jieba.load_userdict("jieba_dict/cus_dict/八大菜系_zh.txt")
    jieba.load_userdict("jieba_dict/cus_dict/飲食大全_zh.txt")
    jieba.load_userdict("jieba_dict/cus_dict/熱門電影大全_zh.txt")
    
    
#     test
#     words = jieba.cut("王天才", cut_all=False)
#     for word in words:
#         print (word)

    
    
    # load stopwords set
    stopword_set = set()
    with open('jieba_dict/stopwords.txt','r', encoding='utf-8') as stopwords:
        for stopword in stopwords:
            stopword_set.add(stopword.strip('\n'))
  
#     output = open('wiki_seg.txt', 'w', encoding='utf-8')
#     with open('wiki_zh_tw.txt', 'r', encoding='utf-8') as content :
    output = open('test_seg.txt', 'w', encoding='utf-8')
    with open('test.txt', 'r', encoding='utf-8') as content :    
        for texts_num, line in enumerate(content):
            line = line.strip('\n')
            words = jieba.cut(line, cut_all=False)
            for word in words:
                if word not in stopword_set:
                    output.write(word + ' ')
            output.write('\n')
  
            if (texts_num + 1) % 5000 == 0:
                logging.info("已完成前 %d 行的斷詞" % (texts_num + 1))
    output.close()
    logging.info("已完成")
if __name__ == '__main__':
    main()
