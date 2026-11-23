"""Isolated synthetic SQLite reporting harness. No external database."""
import sqlite3
from pathlib import Path
DEFAULT_SQL = Path(__file__).with_name('report.sql')

def run_report(assets, start, end, observations, sql=None):
    if type(assets) is not list or len(assets)>100 or any(type(a) is not str or not a or len(a)>100 for a in assets) or len(set(assets)) != len(assets):
        raise ValueError('assets must be unique nonempty exact strings, max 100')
    if type(start) is not int or type(end) is not int or not (0 <= start <= end <= 2_000_000_000) or start%60 or end%60 or end-start>1440*60:
        raise ValueError('window must be aligned, ordered, nonnegative and at most 1440 minutes')
    if type(observations) is not list or len(observations)>100_000:
        raise ValueError('observations must be a list of at most 100000 rows')
    for row in observations:
        if type(row) is not tuple or len(row)!=3:
            raise ValueError('observation must be (asset, second, valid) tuple')
        a,t,v=row
        if a is not None and (type(a) is not str or len(a)>100): raise ValueError('bad asset')
        if t is not None and (type(t) is not int or not -2_000_000_000<=t<=2_000_000_000): raise ValueError('bad second')
        if v is not None and (type(v) is not int or v not in (0,1)): raise ValueError('bad validity')
    statement=DEFAULT_SQL.read_text() if sql is None else sql
    with sqlite3.connect(':memory:') as db:
        db.executescript('CREATE TABLE expected_assets(asset TEXT PRIMARY KEY COLLATE BINARY); CREATE TABLE report_window(start_second INTEGER, end_second INTEGER); CREATE TABLE observations(asset TEXT, observed_second INTEGER, valid INTEGER); CREATE INDEX by_asset_second ON observations(asset, observed_second);')
        db.executemany('INSERT INTO expected_assets VALUES (?)',[(a,) for a in assets])
        db.execute('INSERT INTO report_window VALUES (?,?)',(start,end))
        db.executemany('INSERT INTO observations VALUES (?,?,?)',observations)
        db.execute('PRAGMA query_only=ON')
        steps=0
        def budget():
            nonlocal steps
            steps+=1
            return steps>100_000
        db.set_progress_handler(budget,1000)
        cursor=db.execute(statement)
        names=[c[0] for c in cursor.description]
        expected=['asset','minute_start','covered_seconds','expected_seconds','status']
        if names!=expected: raise ValueError('wrong output columns')
        return [dict(zip(names,row)) for row in cursor.fetchall()]
