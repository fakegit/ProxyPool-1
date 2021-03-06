import pymysql

from ProxyPool.config import DATABASE_CONFIG
from ProxyPool.util.loghelper import LogHelper

# 便与匹配api接收的条件参数
api_columns = ['ip', 'port', 'type', 'protocol', 'country', 'area', 'score', 'speed']


# Mysql辅助类
class MysqlHelper(object):

    # def __init__(self):
    #    #self.__create_conn()
    #    pass
    def __close(self, cursor, conn):
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        # self.__create_conn()

    def __get_conn(self):
        try:
            self.conn = pymysql.connect(host=DATABASE_CONFIG['ip'], port=DATABASE_CONFIG['port'], \
                                        user=DATABASE_CONFIG['username'], passwd=DATABASE_CONFIG['password'],
                                        db=DATABASE_CONFIG['database'], connect_timeout=100)
            return self.conn
        except Exception as e:
            try:
                self.conn = pymysql.connect(host=DATABASE_CONFIG['ip'], port=DATABASE_CONFIG['port'], \
                                            user=DATABASE_CONFIG['username'], passwd=DATABASE_CONFIG['password'],
                                            db=DATABASE_CONFIG['database'], connect_timeout=100)
                return self.conn
            except Exception as e:
                LogHelper.error('获取数据库连接出错:' + str(e))

    def create_db(self):
        #
        pass

    def drop_db(self):
        # BaseModel.metadata.drop_all(engine)
        pass

    def execute(self, sql):
        return self.execute_many([sql])

    def execute_many(self, sqls):
        effect_row = 0
        try:
            conn = self.__get_conn()
            cursor = conn.cursor()
            try:
                for s in sqls:
                    effect_row += cursor.execute(s)
                conn.commit()
            except Exception as e:
                conn.rollback()
                LogHelper.error('执行{0}出错,错误原因:{1}'.format(sqls, str(e)))
            finally:
                self.__close(cursor, conn)
        except:
            pass
        return effect_row

    # 去重复
    def deduplication(self):
        self.execute('DELETE Proxy_Main  \
        FROM \
	        Proxy_Main, \
	        ( SELECT min( id ) id, ip, `port` FROM Proxy_Main GROUP BY ip, `port` HAVING count( * ) > 1 ) t2  \
        WHERE  \
	        Proxy_Main.ip = t2.ip  \
	        AND Proxy_Main.`port` = t2.`port`  \
	        AND Proxy_Main.id > t2.id;')

    def query(self, sql, count=0):
        conn = self.__get_conn()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        result = None
        try:
            if count == 0 or not count:
                cursor.execute(sql)
                result = cursor.fetchall()
            else:
                cursor.execute(sql)
                count = int(count)
                result = cursor.fetchmany(count)
        except Exception as e:
            LogHelper.error('执行{0}出错,错误原因:{1}'.format(sql, str(e)))
        finally:
            self.__close(cursor, conn)
        return result

    def add(self, model):
        effect_row = 0
        # 如果添加的是单个
        if isinstance(model, dict):
            sql = 'insert into Proxy_Main({0}) values({1})'
            columns = ','.join(list(model.keys()))
            values = "'" + ','.join([str(v) for v in model.values()]).replace(',', "','") + "'"
            effect_row = self.execute(sql.format(columns, values))
        # 添加的多个
        elif isinstance(model, list):
            sqllist = []
            sql = 'insert into Proxy_Main({0}) values({1})'
            for item in model:
                columns = ','.join(list(item.keys()))
                values = "'" + ','.join([str(v) for v in item.values()]).replace(',', "','") + "'"
                sqllist.append(sql.format(columns, values))
            effect_row = self.execute_many(sqllist)
        return effect_row

    def get(self, conditions=None, count=0):
        where = '1=1'
        if conditions and isinstance(conditions, dict):
            where = ''
            for key, value in conditions.items():
                if key in api_columns:
                    where += key + '=' + '\'' + value + '\'' + ' and '
            where = where.strip('and ')
            if where == '':
                where = '1=1'
        if count == 0 or not count:
            result = self.query('select * from Proxy_Main where ' + where, count)
        else:
            result = self.query('select * from Proxy_Main where ' + where)
        return result

    def update(self, model, conditions):
        where = ''
        for key, value in conditions.items():
            where += key + '=' + '\'' + str(value) + '\'' + ' and '
        where = where.strip('and ')
        values = ''
        for key, value in model.items():
            values += '{0}=\'{1}\','.format(key, str(value))
        values = values.strip(',')
        effect_row = self.execute('update Proxy_Main set ' + values + ' where ' + where)
        return effect_row

    def delete(self, conditions):
        where = ''
        if not isinstance(conditions, dict) or not conditions:
            return -1
        for key, value in conditions.items():
            if key in api_columns:
                where += key + '=' + '\'' + str(value) + '\'' + ' and '
        where = where.strip('and ')
        effect_row = self.execute('delete from Proxy_Main where ' + where)
        return effect_row


if __name__ == '__main__':
    sql = SqlHelper()

    # a =
    # a =
    # sql.add({'ip':'1.1.1.1','port':'2222','speed':0,'type':0,'protocol':0,'country':'asd','area':'fff','score':'10'})
    # a =
    # sql.add([{'ip':'1.1.1.4','port':'2222','speed':'0','type':'0','protocol':'0','country':'asd','area':'fff','score':'10'},
    #         {'ip':'1.1.1.2','port':'2222','speed':'0','type':'0','protocol':'0','country':'asd','area':'fff','score':'10'},
    #         {'ip':'1.1.1.3','port':'2222','speed':'0','type':'0','protocol':'0','country':'asd','area':'fff','score':'10'}])
    # a = sql.query('select * from Proxy_Main',5)
    # a = sql.update({'score':'333','port':'666'}, {'country':'f','speed':'2'})
    # a = sql.delete({'country':'f','speed':'2'})
    a = sql.get({'country': 'b', 'area': 'b', 'asdasd': 'asda'}, 5)
    # a = sql.get()
    print(a)
