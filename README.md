# WordTest
Education purpose: extract English words from textbooks and create tests. Track correct and wrong answers and customize tests based on it.

#TODO
1. Have a DB column for next-date so that:
- search for today or a specific date in DB is much easier.
- we can draw a histogram on the next days/weeks to see how many items to learn on that day/week.


不使用Anki的原因
- 没有词汇量统计
- 功能太多，难于上手


[Words] 单词库
Columns
- Word Front (E.g., English): (string, primary key)
- Word Back (E.g., Chinese): (string)
- Front->Back: correct count (number)
- Front->Back: wrong count (number)
- Front->Back: review history (dates[], results[])
- Back->Front: correct count (number)
- Back->Front: wrong count (number)
- Back->Front: review history (dates[], results[])
- Reference (E.g., RAZ C): (string)
- Examples: string[]
- Flag1: (string)
- Flag2: (string)
- Flag3: (string)

中文认识字库
- 汉字（主键）
- 添加日期
- 标记1 （比如书名出处）
- 标记2
- 标记3
- 难度（1：一级字表；2：二级字表）


功能
- 查询一共多少字
- 某个字是否认识
- 添加新认识汉字
- 识字量曲线、目前识字量柱状图
- 输入一篇文章，判生字率是多少！*****

输入
- 新字
- 一个文件（文件中所有字是认识的字）

