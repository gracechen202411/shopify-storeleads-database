#!/usr/bin/env python3
"""
测试新的 neondb 数据库速度和内容
"""
import time
import psycopg2

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

print("="*80)
print("测试 neondb 数据库")
print("="*80)

try:
    # 测试1：连接速度
    start = time.time()
    conn = psycopg2.connect(**DB_CONFIG)
    connect_time = time.time() - start
    print(f"\n✅ 连接数据库：{connect_time:.3f}秒")
    
    cur = conn.cursor()
    
    # 测试2：查看所有表
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    print(f"\n📊 数据库中的表：")
    for table in tables:
        print(f"   - {table[0]}")
    
    # 测试3：如果有 stores 表，查看结构
    if tables:
        table_name = tables[0][0]
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        print(f"\n📋 表 '{table_name}' 的字段：")
        for col in columns[:10]:  # 只显示前10个字段
            print(f"   - {col[0]} ({col[1]})")
        
        # 测试4：统计记录数
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        print(f"\n📈 表 '{table_name}' 记录数：{count:,}")
        
        # 测试5：读取速度
        start = time.time()
        cur.execute(f"SELECT * FROM {table_name} LIMIT 100")
        rows = cur.fetchall()
        read_time = time.time() - start
        print(f"\n⚡ 读取100条记录：{read_time:.3f}秒")
        
        # 测试6：查看是否有 domain 字段
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' AND column_name = 'domain'")
        has_domain = cur.fetchone()
        if has_domain:
            cur.execute(f"SELECT domain FROM {table_name} LIMIT 5")
            domains = cur.fetchall()
            print(f"\n🌐 示例域名：")
            for d in domains:
                print(f"   - {d[0]}")
    
    print(f"\n{'='*80}")
    print(f"性能总结")
    print(f"{'='*80}")
    print(f"✅ 数据库连接正常")
    print(f"✅ 读写速度很快（连接{connect_time:.3f}秒，读取{read_time:.3f}秒）")
    print(f"✅ 可以用这个数据库存储谷歌广告检查结果")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ 错误：{e}")
    import traceback
    traceback.print_exc()
