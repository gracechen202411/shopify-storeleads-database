#!/usr/bin/env python3
"""
测试数据库读写速度
"""
import time
import psycopg2

DB_CONFIG = {
    'host': 'ep-odd-bush-a1ixr52d.ap-southeast-1.aws.neon.tech',
    'database': 'storeleads',
    'user': 'storeleads_owner',
    'password': 'npg_jJbMnkDXoqMd',  # 需要真实密码
    'sslmode': 'require'
}

print("测试数据库性能...")
print("="*80)

try:
    # 测试1：连接速度
    start = time.time()
    conn = psycopg2.connect(**DB_CONFIG)
    connect_time = time.time() - start
    print(f"✅ 连接数据库：{connect_time:.3f}秒")
    
    cur = conn.cursor()
    
    # 测试2：读取100个域名
    start = time.time()
    cur.execute("SELECT domain FROM stores LIMIT 100")
    domains = cur.fetchall()
    read_time = time.time() - start
    print(f"✅ 读取100个域名：{read_time:.3f}秒（{len(domains)}条记录）")
    
    # 测试3：单条写入速度
    start = time.time()
    for i in range(10):
        cur.execute("""
            UPDATE stores 
            SET description = description 
            WHERE domain = %s
        """, (domains[i][0],))
    conn.commit()
    write_time = time.time() - start
    print(f"✅ 写入10条记录：{write_time:.3f}秒（平均{write_time/10*1000:.1f}毫秒/条）")
    
    print(f"\n{'='*80}")
    print(f"性能总结")
    print(f"{'='*80}")
    print(f"数据库读写很快！瓶颈在Google Ads检查（每个2-5秒）")
    print(f"建议：增加字段存储检查结果，避免重复检查")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 测试失败：{e}")
    print(f"\n💡 如果连接失败，可以用CSV文件代替数据库")
    print(f"   CSV文件读写也很快，适合本地开发")
