import sqlite3
import datetime
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "odds_history.db")

def init_db():
    """初始化本地 SQLite 数据库，用于存储赔率变动时间序列数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 创建存储实时赔率的序列表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS odds_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_name TEXT,
            timestamp DATETIME,
            jc_odds TEXT,
            pin_odds TEXT,
            best_ev REAL,
            best_selection TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_odds_snapshot(match_name, jc_odds, pin_odds, best_ev, best_selection):
    """保存每一轮轮询的实时赔率快照"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    cursor.execute('''
        INSERT INTO odds_history (match_name, timestamp, jc_odds, pin_odds, best_ev, best_selection)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        match_name, 
        timestamp,
        json.dumps(jc_odds), 
        json.dumps(pin_odds), 
        best_ev, 
        best_selection
    ))
    
    conn.commit()
    conn.close()

def get_historical_ev_trend(match_name, limit=10):
    """获取该场比赛最近的 EV 变动趋势，用于判断是否到达阻力位/支撑位"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, best_ev, best_selection 
        FROM odds_history 
        WHERE match_name = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (match_name, limit))
    
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    init_db()
    print("[Storage] 实时赔率时间序列数据库 (SQLite) 初始化完成。")
