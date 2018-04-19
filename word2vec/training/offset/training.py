'''
Created on 2018年3月13日

@author: roykt_tsai
'''

import os
import word2vec
import word2vec.training.demo_domain as demo_domain
import math
from botocore.vendored.requests.compat import str
from django.template.defaultfilters import lower

def compute_accuracy(training_sentences, is_show):
    total = 0
    match_conuter = 0
    selected_topic_counter = 0
    for i in range(len(training_sentences)):
        total = total + len(training_sentences[i]) 
        for sentence in training_sentences[i]:
            sentence_seg = sentence.split(",")
            topic_list = demo_domain.domain_decision(sentence_seg)[0]
            selected_topic_counter = selected_topic_counter + len(topic_list)
#             log(str(sentence_seg)+' = '+str(topic_list), is_show)   
            if i==0 and demo_domain.topic_list_en[0] in topic_list:
                match_conuter = match_conuter + 1     
            elif  i==1 and demo_domain.topic_list_en[1] in topic_list:
                match_conuter = match_conuter + 1
            elif  i==2 and demo_domain.topic_list_en[2] in topic_list:
                match_conuter = match_conuter + 1
            elif  i==3 and demo_domain.topic_list_en[3] in topic_list:
                match_conuter = match_conuter + 1
            elif  i==4 and demo_domain.topic_list_en[4] in topic_list:
                match_conuter = match_conuter + 1
            elif  i==5 and demo_domain.topic_list_en[5] in topic_list:
                match_conuter = match_conuter + 1
            elif  i==6 and demo_domain.topic_list_en[6] in topic_list:
                match_conuter = match_conuter + 1    
            elif  i==7 and demo_domain.topic_list_en[7] in topic_list:
                match_conuter = match_conuter + 1
            elif  i==8 and demo_domain.topic_list_en[8] in topic_list:
                match_conuter = match_conuter + 1           
            else:
                log('not match sentence = '+str(sentence_seg)+' = '+str(topic_list), is_show)
    cover_rate = round(match_conuter*100/total,2)   
    if selected_topic_counter == 0:
        accuracy_rate = 0
    else:
        accuracy_rate = round(match_conuter*100/selected_topic_counter,2)                                                                                        
    log('Cover rate = '+str(cover_rate)+'%', is_show) 
    log('Accuracy rate = '+str(accuracy_rate)+'%', is_show) 
    return cover_rate, accuracy_rate


def integrating_cal(cover_rate, accuracy_rate):
    return cover_rate+accuracy_rate

def log(str, is_show):
    if is_show :
        print(str) 
        
def start_training(training_sentences):   

    #init
    demo_domain.offset = 0.01
    learning = 0.002
    max_integrating_rate = [0,0]
    max_cover_rate = [0,0]
    max_accuracy_rate = [0,0]
     
    final_offset ={}
    lower_bound = 2*1/demo_domain.TOPIC_SIZE*100

    while(True):
        rate = compute_accuracy(training_sentences, False)
        if integrating_cal(rate[0], rate[1]) > integrating_cal(max_integrating_rate[0], max_integrating_rate[1]):
            max_integrating_rate = rate
            final_offset['integrating'] = demo_domain.offset
            print('[update] integrating offset = '+str(final_offset['integrating'])+', CoverRate = '+str(max_integrating_rate[0])+'%, AccuracyRate = '+str(max_integrating_rate[1])+'%')
         
         
        if rate[0] > max_cover_rate[0]:
            max_cover_rate = rate
            final_offset['cover']  = demo_domain.offset
            print('[update] cover offset       = '+str(final_offset['cover'])+', CoverRate = '+str(max_cover_rate[0])+'%, AccuracyRate = '+str(max_cover_rate[1])+'%')
             
        if rate[1] > max_accuracy_rate[1]:
            max_accuracy_rate = rate
            final_offset['accuracy']  = demo_domain.offset
            print('[update] accuracy offset    = '+str(final_offset['accuracy'])+', CoverRate = '+str(max_accuracy_rate[0])+'%, AccuracyRate = '+str(max_accuracy_rate[1])+'%')     
             
             
        if rate[0] == 100 and rate[1] < lower_bound:
            break
             
        demo_domain.offset = round(demo_domain.offset + learning, 3)
    
    print('='*80) 
    print('[final] integrating offset = '+str(final_offset['integrating'])+', CoverRate = '+str(max_integrating_rate[0])+'%, AccuracyRate = '+str(max_integrating_rate[1])+'%')
    print('[final] cover offset = '+str(final_offset['cover'])+', CoverRate = '+str(max_cover_rate[0])+'%, AccuracyRate = '+str(max_cover_rate[1])+'%')
    print('[final] accuracy offset = '+str(final_offset['accuracy'])+', CoverRate = '+str(max_accuracy_rate[0])+'%, AccuracyRate = '+str(max_accuracy_rate[1])+'%')
    
    demo_domain.offset = final_offset['integrating']  
    compute_accuracy(training_sentences, True)         

if __name__ == '__main__':
    
   
    demo_domain.init_model()
    demo_domain.is_log_showing = False
    path = os.path.dirname(word2vec.__file__)
    training_sentences = []
 
     
    with open(os.path.join(path, 'training', 'offset', 'Music.txt'), 'r', encoding='utf-8') as file:
        training_sentences.append( file.read().splitlines() ) 
    with open(os.path.join(path, 'training', 'offset', 'Weather.txt'), 'r', encoding='utf-8') as file:
        training_sentences.append( file.read().splitlines() )
    with open(os.path.join(path, 'training', 'offset', 'Finance.txt'), 'r', encoding='utf-8') as file:
        training_sentences.append( file.read().splitlines() )
    with open(os.path.join(path, 'training', 'offset', 'Food.txt'), 'r', encoding='utf-8') as file:
        training_sentences.append( file.read().splitlines() )
    with open(os.path.join(path, 'training', 'offset', 'Entertainment.txt'), 'r', encoding='utf-8') as file:
        training_sentences.append( file.read().splitlines() )
    with open(os.path.join(path, 'training', 'offset', 'News.txt'), 'r', encoding='utf-8') as file:
        training_sentences.append( file.read().splitlines() )
    with open(os.path.join(path, 'training', 'offset', 'Life.txt'), 'r', encoding='utf-8') as file:
        training_sentences.append( file.read().splitlines() ) 
    with open(os.path.join(path, 'training', 'offset', 'Tool.txt'), 'r', encoding='utf-8') as file:
        training_sentences.append( file.read().splitlines() )   
    with open(os.path.join(path, 'training', 'offset', 'Social.txt'), 'r', encoding='utf-8') as file:
        training_sentences.append( file.read().splitlines() )   
        
        
    try:
        while True:
            print("1:offset training start")
            print("2:set offset status")
            print("3:exit")
            query = int(input())
        
            if query == 2:             
                print("輸入offset:")
                query = float(input())
                demo_domain.offset = query
                compute_accuracy(training_sentences, True)
            elif query == 1:
                start_training(training_sentences)
            else:
                print("離開")
                break    
    except Exception as e:
        print(repr(e))    
                                    
    

    

