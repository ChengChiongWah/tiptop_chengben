import cx_Oracle


def judge(value, zhulh):
    """
    判断所给的料号是否是最后一层料号
    """
    value_list = []  # 主料号的发料明细
    for v in value:
        value_list.append(v[1])
    judge_list = [e for e in value_list if e in zhulh]
    if len(judge_list) == 0:
        return True
    else:
        return False


def calculate(z):
    """
    对所给料号进行成本计算
    """
    con = cx_Oracle.connect('hd_zn/hd_zn@192.168.101.3:1521/topprod')
    cur = con.cursor()
    number_gongd = cur.execute("select distinct(sfb01) from hd_zn.sfb_file where sfb05 = '{}' and sfb02 != '5' and sfb02 !='8'".format(z))  # 料号对应的工单
    value_gongd = cur.fetchall()
    number = 0
    elements = 0.00
    for g in value_gongd:
        number_zhujlh = cur.execute("select sfb08 from hd_zn.sfb_file where sfb01 = '{}'".format(g[0]))
        number = number + number_zhujlh.fetchone()[0]
        element_gongd = cur.execute("select sfb08 主件生产数量, sfa03 发料料号, sfa05 应发数量, cben 发料料号单价, sfa05*cben 发料料号金额  from hd_zn.sfa_file, hd_zn.sfb_file, hd_zn.table_2017 where sfa01=sfb01 and sfa03=zhujlh and sfa01='{}'".format(g[0]))
        value_element_gongd = cur.fetchall()
        for e in value_element_gongd:
#            print (z, g, e)
            elements = elements + e[4]
    print(z, number, elements, round(elements/number, 2))
    cur.execute("insert into hd_zn.table_2017 values('{}', '{}')".format(z, round(elements/number)))
    cur.close()
    con.commit()
    con.close()


def main():
    con = cx_Oracle.connect('hd_zn/hd_zn@192.168.101.3:1521/topprod')
    cur = con.cursor()
    sql1 = '''
              select sfb05 主件料号, sfa03 发料料号
              from hd_zn.sfb_file, hd_zn.sfa_file
              where sfa01 = sfb01
          '''
    sql2 = '''
          select distinct(sfb05)  --查询一般生产工单的主件料号
              from hd_zn.sfb_file
              where   sfb02 != '5' and sfb02 !='8'
          '''

    cur.execute(sql2)
    value_zhulh = cur.fetchall()
    zhulh = []
    for result in value_zhulh:
        zhulh.append(result[0])
    while len(zhulh) >0:
        for z in zhulh:
            cur.execute(sql1 + 'and sfb05=' + "'{}'".format(z))
            value = cur.fetchall()
            if judge(value, zhulh):  # 最后一层料号
                calculate(z)
                zhulh.remove(z)
#    cur.execute("insert into hd_zn.table_2017 values('{}', '{}')".format('aaa', 333))
    cur.close()
    con.commit()
    con.close()

if __name__ == '__main__':
    main()