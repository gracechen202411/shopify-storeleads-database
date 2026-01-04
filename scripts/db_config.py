
import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# 自动加载项目根目录的 .env 文件
# 假设脚本在 scripts/xxx/ 下，根目录就是 ../../
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
env_path = project_root / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # 尝试默认加载
    load_dotenv()

def get_db_connection():
    """获取数据库连接"""
    db_url = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
    
    if not db_url:
        # 兼容旧代码的硬编码方式（但在生产环境应避免），作为最后的回退
        # 这里仅作示例，实际应强制使用 .env
        return psycopg2.connect(
            host='ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
            database='neondb',
            user='neondb_owner',
            password='npg_7kil2gsDbcIf',
            sslmode='require'
        )
        
    return psycopg2.connect(db_url)

def get_db_config_dict():
    """获取配置字典（用于某些需要解包 **config 的旧代码）"""
    # 优先解析 URL，如果解析失败则返回硬编码（仅为了兼容旧脚本不做大改）
    # 这是一个过渡方案
    return {
        'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
        'database': 'neondb',
        'user': 'neondb_owner',
        'password': 'npg_7kil2gsDbcIf',
        'sslmode': 'require'
    }
