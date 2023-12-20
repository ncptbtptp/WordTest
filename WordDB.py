#encoding=utf-8

import datetime
import math
import pandas
import pprint
import sqlite3

"""
'''
Filter table: words in this table are so will not be checked
'''


'''
复习优先级（高->低）
1.上次答错的（打错次数多的排在答错次数少的前）
2.上次答对的
'''

'''
#---------------------------------------------#
#-------------------卡片属性-------------------#
#---------------------------------------------#
Front(str): 需要记忆的内容或问题
Back(str): 备注或答案
FieldName1(str): 比如“引用”
FieldValue1(str): 比如英语单词可以记录被多少个句子引用
FieldName2(str): 比如“例句”
FieldValue2(str): 比如英语单词可以记录所有该单词的例句 
FieldName3(str):
FieldValue3(str):
FieldName4(str):
FieldValue4(str):
FieldName5(str):
FieldValue5(str):
Flags(str):  标记列表。支持筛选指定flag的记录

#---------------------------------------------#
#-------------------复习属性-------------------#
#---------------------------------------------#
Mastered(bool): 1: The item is completely mastered
TestCount(int): 测试次数
FailedCount(int)：错误次数
NextReviewDate(str)：下一次复习日期
Reviews(str): 每次复习结果列表（1：答对，0：答错）（一共六次：1天、2天、4天、7天、15天、1月、3月、6月）
'''

''' A test cycle is modelled after H.Ebbinghaus memory curve and comprised of milestones 1, 2, 4, 7, 15, 30, (60), 90, 180
    (in terms of T0 when you first learn the thing). The original version is 1, 2, 4, 7, 15, 30, 90, 180.
    ==-========================================================================================================================
    Below are the progression rules:
    (1) For a new item learned on T0, it will be tested immediately on the second day (the "1" in the list).
    (2) If a test passes on T0 + (i)th milestone, it's moved to the next one. The next test date will be T0 + (i+1)th milestone.
    (3) If a test fails on T0 + (i)th milestone, we restart the whole cycle and the next test date will be the second day ("1").
        For instance, if you fail on T0 + 360, we will start over again like learning it new unfortunately. Fortunately I think
        it's less likely for human beings to not memorize something after at least 10 tries in a row spread out in 180+ days.
        Mr. Ebbinghaus'd get up if otherwise..
    (4) When a test passes and it's already the last milestone ("180"), the item is marked as "Mastered" automatically.
    (5) There is a way to force close/master an item.
    ==-========================================================================================================================

    A test results is a list of past test results(each w/ a test date and result (passed/failed)),
    followed by an integer denoting the 
    The serialized form is "date-result,date-result". E.g., "20210123-0,20210124-1", 1 for passed.

    TODO!!! may be, the last tuple is for "next_milestone_date-next_milestone_index"?
'''
class CTestResults:
    # @results: test results string "20200121:0" or ""
    def __init__(self, results = ""):
        self.INTER_DELIM = ","
        self.INTRA_DELIM = "-"
        self.PASS = "1"
        self.FAIL = "0"
        self.CYCLE = [1, 2, 4, 7, 15, 30, 60, 90, 180]

        # self.results: [("20210123", "0"),("20210124", "1")]
        self.results = __deserialize(results)

    # @result: True or False
    # @return: (new results string, NextReviewDate)
    def append(self, date, result):
        self.results.append((date, result? self.PASS : self.FAIL))
        self.nextMillstone = 0 # todo

    def is_last_failed(self):
        return self.results and self.results[-1][-1] == self.PASS


    # @results: "20210123-0,20210124-1"
    # @return: [("20210123", "0"),("20210124", "1")]
    def __deserialize(self, results):
        if not results:
            return []

        li = []
        for result in results.split(self.INTER_DELIM):
            date, res = result.split(self.INTRA_DELIM)
            li.append((date, res))
        return li





class CItemsDB:
    def __init__(self, db_path):
        self.path = db_path
        self.main_table_name = 'items'

    def open(self):
        # If it's the first time to open the database it will create a new one w/o any table
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def insert_record(self, front, back, fieldName1, fieldVal1, fieldName2, fieldVal2, fieldName3, fieldVal3, \
                      fieldName4, fieldVal4, fieldName5, fieldVal5, flags, passed, nextReviewDate, reviews):

        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.main_table_name()}\
                            (front text primary key,         \
                            back text,                      \
                            fieldName1 text,                     \
                            fieldVal1 text, \
                            fieldName2 text,                     \
                            fieldVal2 text, \
                            fieldName3 text,                     \
                            fieldVal3 text, \
                            fieldName4 text,                     \
                            fieldVal4 text, \
                            fieldName5 text,                     \
                            fieldVal5 text, \
                            flags text, \
                            passed int, \
                            nextReviewDate text, \
                            reviews text)')

        self.cursor.execute(f'INSERT OR IGNORE INTO {self.main_table_name()} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', \
            (front, back, fieldName1, fieldVal1, fieldName2, fieldVal2, fieldName3, fieldVal3, fieldName4, fieldVal4, fieldName5, fieldVal5, \
            flags, passed, nextReviewDate, reviews))

    def 

    def query_record(self, due):
        self.cursor.execute(f"SELECT * FROM {self.main_table_name()} WHERE nextReviewDate <= '{due}'")
    



"""

"""
输入汉字使用频率总表，根据网上Excel生成
-character 汉字（主键）
-frequency 使用频率（整型）
"""

class CWordsDB:
    def __init__(self, db_path):
        self.path = db_path
        # 汉字字典（包括使用频率）- readonly!
        self.dict_table_name = 'dictionary'
        self.dict_column_name_character = 'character'
        self.dict_column_name_frequency = 'frequency'
        self.dict_column_name_frequency = 'coverage'

        # 已掌握
        self.learned_table_name = 'learned'
        self.learned_column_name_character = 'character'
        self.learned_column_name_date = 'date'

    def open(self):
        # If it's the first time to open the database it will create a new one w/o any table
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()

    def save(self):
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()

    """ $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        字典数据库
        Columns:
        - character (primary key)  汉字
        - frequency (int)          样本中使用次数
        - coverage  (real)         覆盖率，或难易度。60%，样本中有60%的字比该字简单
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""

    """ If present, return (character, frequency, coverage); Else None """
    def dict_is_character_present(self, character):
        self.cursor.execute(f"SELECT * FROM {self.dict_table_name} WHERE {self.dict_column_name_character}='{character}'")
        return self.cursor.fetchone()
    
    """ 返回字典中汉字的累计使用概率分布。越靠前的使用越频繁，越靠后的字越少见。所以后面10%的频率带中的汉字会越来越多（生偏字）：
         0% —— 10% 哪些汉字
        10% —— 20% 哪些汉字
        30% —— 40% 哪些汉字
        ...    
    """
    def dict_stats_distribution(self):
        self.cursor.execute(f"SELECT * FROM {self.dict_table_name}")
        rows = self.cursor.fetchall()

        dist = {}
        for range in (10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
            dist[range] = []

        def inner_next_range(x):
            quotient, mod = divmod(x, 10)
            return (int(quotient) + (0 if mod == 0 else 1)) * 10

        for character, frequency, coverage in rows:
            range = inner_next_range(coverage)
            dist[range].append(character)

        return dist

    """ 很简单：返回在dictionary但不在learned中的所有characters """
    def dict_stats_new_characters(self):
        self.cursor.execute(f"SELECT character FROM {self.dict_table_name} WHERE NOT EXISTS (SELECT character FROM {self.learned_table_name} \
        WHERE {self.dict_table_name}.character = {self.learned_table_name}.character) ORDER BY frequency DESC")
        return [x[0] for x in self.cursor.fetchall()]

    def dict_stats_new_characters_all_info(self):
        self.cursor.execute(f"SELECT * FROM {self.dict_table_name} WHERE NOT EXISTS (SELECT * FROM {self.learned_table_name} \
        WHERE {self.dict_table_name}.character = {self.learned_table_name}.character) ORDER BY frequency DESC")
        return self.cursor.fetchall()

    # 搜索生字集合，只返回存在的rows
    def dict_new_search(self, characters):
        if not characters:
            return None

        query_list = ""
        for char in characters:
            query_list += f"'{char}',"
        query_list = query_list[:-1]
        #query_list = "'不', '是'"
        # E.g., SELECT * FROM employees WHERE first_name IN ('Sarah', 'Jane', 'Heather');
        self.cursor.execute(f"SELECT * FROM {self.dict_table_name} WHERE NOT EXISTS (SELECT * FROM {self.learned_table_name} \
        WHERE {self.dict_table_name}.character = {self.learned_table_name}.character) AND character IN ({query_list}) ORDER BY frequency DESC")

        return self.cursor.fetchall()

    #字典数据库dictionary.db已经创建完毕（12041个汉字），现在开始read-only
    """
    def dict_insert_record(self, character, frequency, coverage):
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.dict_table_name} (character text primary key, frequency int, coverage real)')
        self.cursor.execute(f'INSERT OR IGNORE INTO {self.dict_table_name} VALUES ("{character}", {frequency}, {coverage})')

    # excel_file: 汉字单字字频总表.xls
    # 例子：
    # 序列号	汉字	频率	累计频率(%)	拼音	英文翻译 */
    #1	的	8302698	3.20749981	de/di2/di4	(possessive particle)/of, really and truly, aim/clear
    #2	一	3728398	4.647855207	yi1	one/1/single/a(n)
    #3	不	3083707	5.839153459	bu4/bu2	(negative prefix)/not/no
    #..

    def dict_initialize(self, excel_file, skip_row_list, character_column_idx, frequency_column_idx, coverage_column_idx):
        df = pandas.read_excel(excel_file, header=None, skiprows=skip_row_list, \
            usecols=[character_column_idx, frequency_column_idx, coverage_column_idx], names = ["character", "frequency", "coverage"])

        for index, row in df.iterrows():
            # string, int, float
            self.dict_insert_record(row['character'], row['frequency'], row['coverage'])
    """


    """ $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        识字数据库
        Columns:
        - character (primary key)  汉字
        - date (string)            添加日期
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""

    # 搜索指定的汉字集合，只返回存在的rows
    def learned_search(self, characters):
        if not characters:
            return None

        query_list = ""
        for char in characters:
            query_list += f"'{char}',"
        query_list = query_list[:-1]
        #query_list = "'不', '是'"
        # E.g., SELECT * FROM employees WHERE first_name IN ('Sarah', 'Jane', 'Heather');
        self.cursor.execute(f'SELECT character, date FROM {self.learned_table_name} where character IN ({query_list}) ORDER BY date')
        return self.cursor.fetchall()

    def learned_all(self):
        self.cursor.execute(f'SELECT character, date FROM {self.learned_table_name}')
        return self.cursor.fetchall()

    def learned_delete_record(self, character):
        self.cursor.execute(f'DELETE FROM {self.learned_table_name} WHERE character="{character}"')
        print(f"Character {character} was successfully deleted")

    def learned_insert_record(self, character, date):
        # Don't insert if this character does not even exist in the dictionary
        if self.dict_is_character_present(character) is None:
            print(f"Character {character} does not exist in the dictionary!")
            return False

        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.learned_table_name} (character text primary key, date text)')
        self.cursor.execute(f'INSERT OR IGNORE INTO {self.learned_table_name} VALUES ("{character}", "{date}")')
        print(f"Character {character} was successfully inserted")
        return True

    def learned_stats_total(self):
        self.cursor.execute(f'SELECT COUNT(*) FROM {self.learned_table_name}')
        return self.cursor.fetchone()[0]

    """ 统计认识的字所占字典字符集各概率分布的比例 
        10: [568: 200]  表示0%~10%比例中一共有568个汉字，其中200个汉字已经认识
    """
    def learned_stats_distribution(self):
        dict_stats = self.dict_stats_distribution()

        # 这个汉字落在哪个频率range
        def inner_get_range(character):
            for range, characters in dict_stats.items():
                if character in characters:
                    return range
            return None
        
        # Initialize the output dict
        learned_stats = {}
        for range, characters in dict_stats.items():
            learned_stats[range] = [len(characters), 0]

        self.cursor.execute(f'SELECT * FROM {self.learned_table_name}')
        rows = self.cursor.fetchall()

        for character, date in rows:
            range = inner_get_range(character)
            if not range:
                print(f"Character {character} does not exist in dictionary, ignoring for stats")
                continue
            learned_stats[range][-1] += 1

        return learned_stats





"""
def dict_create_from_excel(self):
    db = CWordsDB(r"F:\repos\WordTest\dictionary.db")
    db.open()
    db.dict_initialize(r"F:\repos\WordTest\work_frequency_list.xls", 6, 1, 2, 3)
    db.close()
"""

"""
db = CWordsDB(r"F:\repos\WordTest\dictionary.db")
db.open()
today = str(datetime.date.today())
"""

"""
db.learned_insert_record('汉', today)
db.learned_insert_record('中', today)
db.learned_insert_record('国', today)
"""


"""
res = db.learned_stats_total()
res = db.dict_stats_distribution()
for range, characters in res.items():
    print(range, len(characters))
"""

"""
res = db.learned_stats_distribution()
pprint.pprint(res)
"""

#res = db.dict_stats_new_characters()
#pprint.pprint(len(res))


#db.close()

