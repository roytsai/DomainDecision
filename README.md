# DomainDecision
### 我在這想要解決的問題是當語句進來時，來判斷是屬於什麼類別，也可當作是Word2Vec的一個延伸應用
1. 訓練Word2Vec模型
    * 首先取得訓練資料，使用[wiki](https://zh.wikipedia.org/wiki/Wikipedia:%E6%95%B0%E6%8D%AE%E5%BA%93%E4%B8%8B%E8%BD%BD)資料，因為是使用gensim處理wiki資料，所以這邊只接受zhwiki-latest-pages-articles.xml.bz2 這個檔案才能夠正確處理資料，wiki_to_txt的處理過程就是把wiki html file的資料parser出來，並移除特殊符號及數字，或者您也可以透過crawl來取得PTT的資料來training。
    ~~~
    python wiki_to_txt.py zhwiki-latest-pages-articles.xml.bz2
    ~~~
    * 開始斷詞，在這之前若是使用wiki的朋友就必須先由簡轉繁([openCC](https://pypi.org/project/OpenCC/))，我在這就不贅述了，
    ~~~
    python segment.py
    ~~~   
    * 開始訓練資料
    ~~~
    python train.py
    ~~~
    * 測試模型，此模型可把有存在模型中的詞轉換成詞向量，輸入兩個詞可得到該兩個詞的cos值，越小表示詞意越相近。
    ~~~
    python demo.py
    ~~~

2. 再來是衍伸發展，我們可自行定義topic_list = ['音樂','天氣','財經','飲食','娛樂','新聞','生活','工具','社交']，然後我們會定義各個topic的特徵詞如 music = ['音樂','歌手','專輯','樂器','歌名','歌曲'] ...，當輸入詞進來時，可跟各個topic的特徵詞去計算相似度，進而決定出該詞語哪個topic較為接近，若    有些朋友有架在server的需求話，我的這個專案是透過Django web framework來建構，可在localhost測試: http://127.0.0.1:8000/word2vec/?key=五月天 。
    ~~~
    python manage.py runserver
    ~~~

### 這裡將對Word2Vec做個簡單的說明
* 首先要有大量的文章，所以文章的來源會是影響這個模型的關鍵1
* 再來是將文章做斷詞，但會有很多專有詞，需要透過添加客製詞的步驟，這會是影響模型的關鍵2
~~~
    jieba.load_userdict("jieba_dict/cus_dict/music.txt")
~~~
* 再來就是開始訓練，先以簡單的邏輯來說，如果資料如下所示，那我們預期其實香蕉跟芭蕉詞向量是很接近的
~~~
    我 愛 吃 香蕉 蛋糕
    我 愛 吃 芭蕉 蛋糕
~~~
* 但為何是這樣的結果呢，如果window=1，意思就是離該詞的距離為1，訓練資料的過程中所有的詞彙先做下列的分析，判斷的依據就是某詞widow內的詞，若與另外一詞的widow內的詞很相近的話，那他們的詞義上就會很接近，以此邏輯來看，[香蕉]與[芭蕉]意思會很接近，最後整個訓練出來的模型就會是我們所要的感覺。
~~~
    我 -> [愛]
    愛 -> [我][吃]
    吃 -> [愛][香蕉]
    香蕉 -> [吃][蛋糕]
    蛋糕 -> [香蕉]
    
    我 -> [愛]
    愛 -> [我][吃]
    吃 -> [愛][芭蕉]
    芭蕉 -> [吃][蛋糕]
    蛋糕 -> [芭蕉]
~~~

