# WordTest
Education purpose: extract English words from textbooks and create tests. Track correct and wrong answers and customize tests based on it.

#TODO
1. Have a DB column for next-date so that:
- search for today or a specific date in DB is much easier.
- we can draw a histogram on the next days/weeks to see how many items to learn on that day/week.


��ʹ��Anki��ԭ��
- û�дʻ���ͳ��
- ����̫�࣬��������


[Words] ���ʿ�
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

������ʶ�ֿ�
- ���֣�������
- �������
- ���1 ����������������
- ���2
- ���3
- �Ѷȣ�1��һ���ֱ�2�������ֱ�


����
- ��ѯһ��������
- ĳ�����Ƿ���ʶ
- �������ʶ����
- ʶ�������ߡ�Ŀǰʶ������״ͼ
- ����һƪ���£����������Ƕ��٣�*****

����
- ����
- һ���ļ����ļ�������������ʶ���֣�

