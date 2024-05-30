import pymysql

class MysqlCli:
    # 初始化
    def __init__(self,host,user,password,database,port=3306,charset='utf8',use_unicode=True):
        """
        :param host:主机名
        :param user: 用户
        :param password: 密码
        :param database: 数据库
        :param port: 端口，默认3306
        :param charset: 字符集，默认utf8
        :param use_unicode: 使用unicode，默认True
        """

        self.connect = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset=charset,
            use_unicode=use_unicode
        )
        self.cursor = self.connect.cursor(pymysql.cursors.DictCursor)

    # 关闭连接
    def close(self):
        self.cursor.close()
        self.connect.close()

    # 增删改
    def operate(self,sql,param=None)->int:
        """
        :param sql: sql语句
        :param param: 元组
        :return: 受影响行数 int
        """
        try:
            self.cursor.execute(sql,param)
            self.connect.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.connect.rollback()
            raise Exception(f"operate error: {e}")

    # 批量增删改
    def operate_many(self,sql,params=None)->int:
        """
        :param sql: sql语句
        :param params: params是列表，元素是元组
        :return: 受影响行数 int
        """
        try:
            self.cursor.executemany(sql,params)
            self.connect.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.connect.rollback()
            raise Exception(f"operate_many error: {e}")

    # 查询（结构化）
    def select_one(self,sql,params=None)->dict:
        """
        :param sql: sql语句
        :param params: 元组
        :return: 字典
        """
        try:
          self.cursor.execute(sql,params)
          res = self.cursor.fetchone()
          self.cursor.close()
          return res
        except Exception as e:
            self.connect.rollback()
            raise Exception(f"select_one error: {e}")

    # 批量查询（结构化）
    def select_all(self,sql,params=None)->list:
        """
        :param sql: sql语句
        :param params: 元组
        :return: 列表，元素为字典
        """
        try:
          self.cursor.execute(sql,params)
          res = self.cursor.fetchall()
          self.cursor.close()
          return res
        except Exception as e:
            self.connect.rollback()
            raise Exception(f"select_all error: {e}")

    # 插入一条数据 字典与列名保持一致
    def insert_one(self,table,data:dict)->int:
        """
        :param table: 表名
        :param data: 数据
        :return:
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.operate(query, tuple(data.values()))

    # 插入多条数据
    def insert_many(self,table:str,data_list:list)->int:
        """
        :param table: 表名
        :param data_list: 列表，元素为字典
        :return:
        """
        keys = ','.join(data_list[0].keys())
        placeholders = ','.join(['%s'] * len(data_list[0]))
        query = f'INSERT INTO {table} ({keys}) VALUES ({placeholders})'
        args = [tuple(data.values()) for data in data_list]
        return self.operate_many(query, args)

    # 更新一条数据
    def update_one(self,table:str,data:dict,condition:str):
        """
        :param table: 表名
        :param data: 数据，字典
        :param condition: where后条件
        :return:
        """
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        return self.operate(query,tuple(data.values()))
