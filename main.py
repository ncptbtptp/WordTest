#encoding=utf-8

"""
import sqlite3

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
