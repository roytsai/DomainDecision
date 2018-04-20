
from gensim.models import word2vec
from gensim import models
import logging
import os
import word2vec
from numpy.ma.core import arange
import jieba
import simplejson as json
from botocore.vendored.requests.compat import str


# topic_list = ['音樂','天氣','財經','食譜','電影','政治','生活','社交']
topic_list = ['音樂','天氣','財經','飲食','娛樂','新聞','生活','工具','社交']
# topic_list_en = ['Music', 'Weather', 'Finance', 'Recipe', 'Movie', 'Politics', 
#                  'Life', 'Social']
topic_list_en = ['Music', 'Weather', 'Finance', 'Food', 'Entertainment', 'News', 'Life', 'Tool', 'Social']
TOPIC_SIZE = len(topic_list)
offset = 0.058

    
music = ['音樂','歌手','專輯','樂器','歌名','歌曲']
weather = ['天氣','氣象','溫度','濕度','穿著','冷','熱']
finance = ['財經','分析','買賣','貨幣']
food = ['食物','餐廳','菜色','飲食']
entertainment = ['娛樂','電臺','電影','星座']
news = ['新聞','政治','財經','運動','社會']
life = ['星座']
tool = ['提醒','時間']

social = ['社交']
# topic_feature_list = [music, weather, finance, recipe, movie, politics, life, social]
topic_feature_list = [music, weather, finance, food, entertainment, news, life, tool, social]


model = None
stopword_set = set()
is_log_showing = True
parameter_similar_list = []


def init_model():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    
    
    log("init_model，尋找相似的domain")
    path = os.path.dirname(word2vec.__file__)
    log("word2vec.__file__ = "+path)
    global model, stopword_set
    
    
    model = models.Word2Vec.load(os.path.join(path, 'training', 'model', 'word2vec.model'))
    jieba.set_dictionary(os.path.join(path, 'training', 'jieba_dict', 'dict.txt.big'))
    jieba.load_userdict(os.path.join(path, 'training', 'jieba_dict', 'userdict.txt'))
    jieba.load_userdict(os.path.join(path, 'training', 'jieba_dict', 'cus_dict', 'singer_zh.txt'))
    jieba.load_userdict(os.path.join(path, 'training', 'jieba_dict', 'cus_dict', 'music_zh.txt'))
    jieba.load_userdict(os.path.join(path, 'training', 'jieba_dict', 'cus_dict', '八大菜系_zh.txt'))
    jieba.load_userdict(os.path.join(path, 'training', 'jieba_dict', 'cus_dict', '飲食大全_zh.txt'))
    jieba.load_userdict(os.path.join(path, 'training', 'jieba_dict', 'cus_dict', '熱門電影大全_zh.txt'))

    
    
    #with open(path+r'\training\jieba_dict\stopwords.txt','r', encoding='utf-8') as stopwords:
    with open(os.path.join(path, 'training', 'jieba_dict', 'stopwords.txt'), 'r', encoding='utf-8') as stopwords:
        for stopword in stopwords:
            stopword_set.add(stopword.strip('\n'))




# input : [ 下雪,周杰倫 ]
# ouput : ['音樂','電影']
def domain_decision_for_list(list):
    
    domain_result = domain_decision(list)
        
    return json.dumps(domain_result[2], ensure_ascii=False)

def domain_decision_detail(list):
    result = ''
    log('domain_decision_detail = '+str(len(list)))
    detail_msg = ''
    domain_result = domain_decision(list) 
    
    if len(domain_result) == 0:
        return "key word not in vocabulary"
    
    result = result + str(list) + '<br>'
    for i in range(TOPIC_SIZE):
        detail_msg = detail_msg + topic_list[i] + ':' + str(domain_result[1][i]) + '<br>'
    result = result + str(domain_result[0]) + '<br>' + detail_msg 
    log('result = '+str(result))
        

    return json.dumps(result, ensure_ascii=False)


# input : 下雪
# ouput : ['天氣','生活'] , [0.111, 0.222]
def domain_decision(parameter_list):
    
    global stopword_set
    corrected_parameter_list = []
    for parameter in parameter_list:
        b = check_in_vocabulary(parameter)
        log("check_in_vocabulary = "+str(b) )
        
        if not b:
            words = jieba_cut_vocabulary(parameter)
            corrected_parameter_list.extend(words)     
        else :
            corrected_parameter_list.append(parameter)
               
    topics_cost = get_topic_cost_by_words(corrected_parameter_list)
    selected_topics = select_topic(topics_cost)
    
    global parameter_similar_list 
    result_parameter_order_list =[]
    
    
    #排序parameter相似度-----
    for topic in selected_topics:
        index = topic_list_en.index(topic)
        log(topic+', index = '+str(index))
        object = {'topic' : topic}
        parameter_list = []
        for i in range(len(parameter_similar_list)):
            word = ''
            obj =()
            for key in parameter_similar_list[i].keys():
                word = key
            obj = (word, parameter_similar_list[i][word][index])      
            #log('word = '+word+', score = '+str(parameter_similar_list[i][word][index]))
            parameter_list.append(obj)
        parameter_list = sorted(parameter_list, key = lambda x : x[1], reverse=True)
        
        parameter_array = []
        for tuple in parameter_list:
            parameter_array.append(tuple[0]) 
        
        object['parameter'] = parameter_array
        result_parameter_order_list.append(object)     
        log('parameter_list = '+str(result_parameter_order_list))  
    #排序parameter相似度-----end      
    
    
#     [{'topic':'music', 'parameter':['五月天','溫柔']}]
    log("選中 ****** "+str(selected_topics)+" ******")
    return [selected_topics, topics_cost, result_parameter_order_list];

# input: [周杰倫,愛,唱歌]
# output:[ 0.11703352075249501, 0.5000000000000002, ......., ......]
def get_topic_cost_by_words(words):
    segment_cost_list = []
    result = []
    words_in_vocabulary = []
    global parameter_similar_list 
    parameter_similar_list = []
    for word in words:
        topic_cost_by_word = get_topic_cost(word)  
        if len(topic_cost_by_word)== TOPIC_SIZE:
            words_in_vocabulary.append(word)
            segment_cost_list.append(topic_cost_by_word)
           

    
    for i in range(len(words_in_vocabulary)):
        object = {}
        object[words_in_vocabulary[i]] = segment_cost_list[i]
        parameter_similar_list.append(object)
        
        log('[ '+str(words_in_vocabulary[i]) + ' ]  cost list')
        msg = ''
        for j in range(TOPIC_SIZE):
            msg = msg + topic_list[j] + ':' + str(segment_cost_list[i][j]) + " | "
        log('>>> ' + msg) 
        
    if len(segment_cost_list) == 0:
        return []
    
    #[[ 0.11703352075249501, .....],[0.5000000000000002, .......],[0.5000000000000002, ......]]
    # >>> [ 0.11703352075249501, 0.5000000000000002, .......,]
    log(str(words))
    log(' === weighting handling ===')
    for i in range(TOPIC_SIZE):
        cost = 0
        words_total_len = 0
        for j in range(len(segment_cost_list)):
            cost = cost + segment_cost_list[j][i] * len(words[j])#TODO
            words_total_len = words_total_len +len(words[j])
        if words_total_len > 0:
            cost = cost / words_total_len
        result.append(cost)    
        log(topic_list[i]+' : '+str(cost))
    return result

# input: 周杰倫
# output:[ 0.11703352075249501, 0.5000000000000002, .....]
def get_topic_cost(key_word):
    topic_cost_list = []
    global topic_list
    
    for i in range(len(topic_list)):
        max_cost = -1
        feature_cost_list = []
        #選出最大feature當作topic cost
        for topic in topic_feature_list[i]:
            try:
                res = model.similarity(key_word, topic)
                if(res > max_cost):
                    max_cost = res
                feature_cost = {}
                feature_cost[topic] = res
                feature_cost_list.append(feature_cost)
            except Exception as e:
                log('get_topic_cost  : '+repr(e))
                return []
        log(key_word+'  >>> feature list : '+str(feature_cost_list))    
#         topic_cost_object['domain'] = feature_cost_list 
        topic_cost_list.append(max_cost)   
    log(' --------------------------------------------- ')
    return topic_cost_list

# input: [ 0.5000000000000002, 0.5600000000000002, 0.11703352075249501, .....]
# output:[ '音樂','天氣' ]
def select_topic(topic_cost_list):

    selected_topic_tuple_list = []
    max_cost = -1
    result = []
    if(len(topic_cost_list) == 0):
        return []; 
    
    for i in range(TOPIC_SIZE):
        cost = topic_cost_list[i]
        if cost > max_cost :
            max_cost = cost
        
    for i in range(TOPIC_SIZE):
        topic_cost = topic_cost_list[i]
        tuple = ()
        if(topic_cost > -1 and (max_cost - topic_cost_list[i]) <= offset ):
            #result.append(topic_list_en[i])
            tuple = (topic_list_en[i], topic_cost)
            selected_topic_tuple_list.append(tuple)
    #排序        
    selected_topic_tuple_list = sorted(selected_topic_tuple_list, key = lambda x : x[1], reverse=True)
    for tuples in selected_topic_tuple_list:
        result.append(tuples[0])
            
    return result
        
def jieba_cut_vocabulary(word):
    words = jieba.cut(word, cut_all=False)
    wordsResult = []
    for word in words:
        log(word)   
        if word not in stopword_set:
            wordsResult.append(word)
    return wordsResult
    
def check_in_vocabulary(word):
    try:
        model.most_similar(word,topn = 1)
        return True
    except Exception as e:
        return False
    
    
def log(str):
    if is_log_showing :
        print(str) 

if __name__ == '__main__':
    init_model()

    
    while True:
        try:
            query = input()
            q_list = query.split()
            if len(q_list) == 1:
                result = domain_decision(q_list[0])
                domain_decision(q_list[0])
                   
                print("相似詞前 100 排序")
                res = model.most_similar(q_list[0],topn = 100)
                for item in res:
                    print(item[0]+","+str(item[1]))
                   
        except Exception as e:
            print(repr(e))

    