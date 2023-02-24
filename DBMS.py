import streamlit as st
import re

def check(s1):
    cnt = 0
    for it in s1:
        if it == '(':
            cnt += 1
        elif it == ')':
            cnt -= 1

    if cnt == 0:
        return True
    else:
        return False


def convert(s1):
    if check(s1):
        st.markdown(""" <span style="border-radius:50%;background:black">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>&nbsp;<span style="color:blue;font-size:30px;">  FIND '}' FOR EVALUATE.</span> """, unsafe_allow_html=True)
        st.markdown("""<h3>STEPS</h3>""", unsafe_allow_html=True)
        l = []
        prev = 0
        for i in range(0, len(s1)):
            if s1[i] == '(':
                l.append(s1[prev:i])
                l.append('{')
                prev = i + 1
            elif s1[i] == ')':
                l.append(s1[prev:i])
                l.append('}')
                prev = i + 1

        l.append(s1[prev:])
        if (len(l) == 0):
            l.append(s1)

        fnl = []
        for it in l:
            if it != '':
                fnl.append(it)

        return fnl
    else:
        st.write('INVALID PARENTHESES ')
        return []


def evaluate(s):
    ans = ""
    if s.find("group by") != -1:
        groupbyInd = s.find("group by")
        selectInd = s.find("select")
        havingInd = s.find("having")
        fromInd = s.find("from")

        #select * from (select id,name from pqr) where id=10
        #select orderid, count(orderid) from sales_order having orderid where orderid  = (select orderid from sales_order)
        #select max(salary),department from table group by department having op=10
        #SELECT DISTINCT users.uid FROM users JOIN opinion o, opinion o2 WHERE users.uid = o.authorid AND users.uid = o2.authorid AND o2.statementid = $sid2 AND o.statementid = $sid1
        #update temp set id=10 where temp.name='yash'
        #delete temp where id=(select id2 from pqr,xyz)
        #delete temp
        #(select * from table1) inner join (select * from table2)
        #select * from table1 where id1 = (select id2 from table2 where id2 = (select id3 from table3 where column2='op'))

        if havingInd == -1:
            ans+=('(g ('+s[groupbyInd+8:]+')   '+s[selectInd+6:fromInd]+' '+'('+f'{s[fromInd+4:groupbyInd]}'+'))')
        else:
            ans+=('( g ('+s[groupbyInd+8:havingInd]+')  '+ s[selectInd+6:fromInd] +'( σ '+s[havingInd+6:]  +'( '+s[fromInd+4:groupbyInd].replace(',','X')+')))')

    elif s[:min(10, len(s))].find("select") != -1:
        selectInd = s.find("select")
        fromInd = s.find("from")
        whereInd = s.find("where")

        ans += ('( π ' + s[selectInd + 6:fromInd])
        if whereInd == -1:

            if(s[fromInd + 4:].find('(') == -1):
                temp=s[fromInd + 4:].replace(',', ' X ')
            else:
                temp=s[fromInd + 4:]

            ans += ('(' + temp + '))')
        else:

            if(s[fromInd + 4:whereInd].find('(') == -1):
                temp=s[fromInd + 4:whereInd].replace(',', ' X ')
            else:
                temp=s[fromInd + 4:whereInd]

            ans += ('( σ ' + s[whereInd + 5:] + '(' + temp + ')))')

        StarInd = ans.find('*')

        if StarInd != -1:
            ans = ans[StarInd + 1:-1]

    elif s[:min(10, len(s))].find("delete") != -1:
        whereInd = s.find("where");
        deleteInd = s.find("delete");
        if whereInd == -1:
            ans += (s[deleteInd + 6:])
            ans += (' <- Φ')
        else:
            ans += (s[deleteInd + 6:whereInd])
            ans += (' <- ' + s[deleteInd + 6:whereInd] + ' - ')
            ans += (f'( σ {s[whereInd + 5:]}({s[deleteInd + 6:whereInd]}))')

    elif s[:min(10, len(s))].find("update") != -1:
        whereInd = s.find("where");
        updateInd = s.find("update");
        setInd = s.find("set");
        equalInd = s.find("=");

        if whereInd == -1:
            ans += (
                f'{s[updateInd + 6:setInd]} <- ( π all_other_attributes,{s[equalInd + 1:]} ({s[updateInd + 6:setInd]}))')
        else:
            p = s[whereInd + 5:].replace('=', '!=');
            ans += (
                f'{s[updateInd + 6:setInd]} <- ( π all_other_attributes,{s[equalInd + 1:whereInd]} (σ {s[whereInd + 5:]} ({s[updateInd + 6:setInd]}))) U ')
            ans += (f'( π all_other_attributes,{s[setInd + 3:equalInd]} (σ {p} ({s[updateInd + 6:setInd]})))')
    else:
        ans = (f'({s})')

    return ans



st.title('SQL TO RA')
SQL = st.text_input('Enter SQL')
SQL=SQL.lower()
SQL=SQL.strip()

result = st.button("Convert")

if result:
    # st.write("Output RA")
    # st.header(SQL)
    # convert(SQL)

    if len(SQL) == 0:
        st.text_area(label="Output RA : ", value='PLZ ENTER QUERY', height=None)
    else:

        if SQL.find(' in ') != -1:
            op=re.split('\)|\(',SQL)

            l=[]
            for it in op:
                if it.strip(" ") != "":
                    l.append(it)

            # st.write(l)

            p1=l[0];p2=l[1];
            p1from = p1.find("from")
            p1where=p1.find("where")
            p1select=p1.find("select")
            p1in=p1.find("in")

            p2select=p2.find("select")
            p2from = p2.find("from")
            p2where = p2.find("where")

            fnl = f' ({p1[p1from+4:p1where]} X {p2[p2from+4:p2where]}))'
            i2 = f' (σ {p1[p1from+4:p1where]}.{p1[p1where+5:p1in]} = {p2[p2from+4:p2where]}.{p2[p2select+6:p2from]}'
            i1 = f' π {p1[p1select+6:p1from]}'

            #select name,cname from student where rno in ( select rno from enroll )

            st.text_area(label="", value=i1+i2+fnl, height=None)

        else:
            l = convert(SQL)
            # st.write(l)
            while True:
                st.write(l)
                idx = -1
                it = 0

                while it < len(l):
                    if (l[it] == '}'):
                        idx = it
                        break
                    it += 1

                if it == len(l):
                    break

                temp = evaluate(l[idx - 1])
                if (idx - 3 >= 0):
                    l[idx - 3] += temp
                    del l[idx - 2:idx + 1]
                else:
                    l[0] = temp
                    del l[1:3]

            for it in range(1, len(l)):
                l[0] += l[it]

            l[0] = evaluate(l[0])
            l[0] = l[0].replace(' and ', '^')
            l[0] = l[0].replace(' or ', 'v')
            l[0] = l[0].replace(' inner join ', ' |X| ')
            l[0] = l[0].replace(' natural join ', '|X|')
            l[0] = l[0].replace(' join ', '|X|')
            l[0] = l[0].replace(' minus ', '-')
            l[0] = l[0].replace(' union ', 'U')
            l[0] = l[0].replace(' intersect ', '∩')

            # st.write("After Replacing Symbols : ")
            # st.write(l[0])

            st.markdown("""<h3>FINAL ANS</h3>""", unsafe_allow_html=True)
            st.text_area(label="", value=l[0], height=None)