
import struct
import sys
import binascii 
import pdb
import importlib
import opencc
import time
from datetime import datetime

#搜狗的scel詞庫就是保存的文本的unicode編碼，每兩個位元組一個字元（中文漢字或者英文字母）
#找出其每部分的偏移位置即可
#主要兩部分
#1.全域拼音表，貌似是所有的拼音組合，字典序
#       格式為(index,len,pinyin)的列表
#       index: 兩個位元組的整數 代表這個拼音的索引
#       len: 兩個位元組的整數 拼音的位元組長度
#       pinyin: 當前的拼音，每個字元兩個位元組，總長len
#       
#2.漢語片語表
#       格式為(same,py_table_len,py_table,{word_len,word,ext_len,ext})的一個列表
#       same: 兩個位元組 整數 同音詞數量
#       py_table_len:  兩個位元組 整數
#       py_table: 整數清單，每個整數兩個位元組,每個整數代表一個拼音的索引
#
#       word_len:兩個位元組 整數 代表中文片語位元組數長度
#       word: 中文片語,每個中文漢字兩個位元組，總長度word_len
#       ext_len: 兩個位元組 整數 代表擴展資訊的長度，好像都是10
#       ext: 擴展資訊 前兩個位元組是一個整數(不知道是不是詞頻) 後八個位元組全是0
#
#      {word_len,word,ext_len,ext} 一共重複same次 同音詞 相同拼音表


#拼音表偏移，
startPy = 0x1540;

#漢語片語表偏移
startChinese = 0x2628;

#全域拼音表

GPy_Table ={}

#解析結果
#元組(詞頻,拼音,中文片語)的列表
GTable = []

def byte2str(data):
    '''將原始位元組碼轉為字串'''
    pos = 0
    str = ''
    while pos < len(data):
        c = chr(struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0])
        if c != chr(0):
            str += c
        pos += 2
    return str
#獲取拼音表
def getPyTable(data):

    data = data[4:]
    pos = 0
    while pos < len(data):
        index = struct.unpack('H', bytes([data[pos],data[pos + 1]]))[0]
        pos += 2
        lenPy = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]
        pos += 2
        py = byte2str(data[pos:pos + lenPy])

        GPy_Table[index] = py
        pos += lenPy


#獲取一個片語的拼音
def getWordPy(data):
    pos = 0
    ret = ''
    while pos < len(data):
        index = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]
        ret += GPy_Table[index]
        pos += 2
    return ret


#讀取中文表    
def getChinese(data):
    pos = 0
    while pos < len(data):
        # 同音詞數量
        same = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]

        # 拼音索引表長度
        pos += 2
        py_table_len = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]

        # 拼音索引表
        pos += 2
        py = getWordPy(data[pos: pos + py_table_len])

        # 中文片語
        pos += py_table_len
        for i in range(same):
            # 中文片語長度
            c_len = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]
            # 中文片語
            pos += 2
            word = byte2str(data[pos: pos + c_len])
            # 擴展資料長度
            pos += c_len
            ext_len = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]
            # 詞頻
            pos += 2
            count = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]

            # 保存
            GTable.append((count, py, word))

            # 到下個詞的偏移位置
            pos += ext_len

def deal(file_name):
    print ('-'*60)
    f = open(file_name,'rb')
    data = f.read()
    f.close()
    if data[0:12] !=b"@\x15\x00\x00DCS\x01\x01\x00\x00\x00":
        print ("確認你選擇的是搜狗(.scel)詞庫?")
        sys.exit(0)
    #pdb.set_trace()
    
    print ("詞庫名：" ,byte2str(data[0x130:0x338]))#.encode('GB18030')
    print ("詞庫類型：" ,byte2str(data[0x338:0x540]))#.encode('GB18030')
    print ("描述資訊：" ,byte2str(data[0x540:0xd40]))#.encode('GB18030')
    print ("詞庫示例：",byte2str(data[0xd40:startPy]))#.encode('GB18030')
    
    getPyTable(data[startPy:startChinese])
    getChinese(data[startChinese:])
    return byte2str(data[0x130:0x338])
            
if __name__ == '__main__':

    #將要轉換的詞庫添加在這裡就可以了
    o = [
         '熱門電影大全.scel'
    ]
    
    cc = opencc.OpenCC('s2t')
    for f in o:
        name = deal(f)  
    with open('sogou.txt', 'w', encoding ='utf8') as output:
        start_time = datetime.now()
        size = len(GTable)
        cache_str = ''
        for i in range(size):
            if i == (size-1):
                cache_str = cache_str + GTable[i][2]
            else :
                cache_str = cache_str + GTable[i][2]+','
                
            if (i+1)%200 == 0 or i == (size-1):
                cache_str = cc.convert(cache_str)
                cache_str =  cache_str.replace(",", "\n")
                output.writelines(cache_str) 
                print("已完成"+str(i+1)+'筆') 
                cache_str = ''
        output.close()       
        print('總共花費時間 : '+str(datetime.now() - start_time))    
        print("==========保存結束========")
            
            
            
            
            
  
