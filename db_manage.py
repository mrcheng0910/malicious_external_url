# encoding: utf-8
"""
数据库操作
"""

from pymongo import MongoClient

server_address = 'localhost'


def get_db():
    """
    连接数据库
    :return
    """
    client = MongoClient(server_address, 27017)
    db = client['eds_last']
    return db


def get_col(col_name='keyinfo'):
    """
    获取collection
    :return: col
    """
    db = get_db()
    col = db[col_name]
    return col