# encoding: utf-8
"""
数据库操作
"""

from pymongo import MongoClient

server_address = 'localhost'


def get_db(db_name = 'eds_last'):
    """
    连接数据库
    :return
    """
    client = MongoClient(server_address, 27017)
    db = client[db_name]
    return db


def get_col(col_name='keyinfo',db_name='eds_last'):
    """
    获取collection
    :return: col
    """
    db = get_db(db_name)
    col = db[col_name]
    return col