import datetime
from zoneinfo import ZoneInfo

# 强制定义全局标准时区：北京时间
BEIJING_TZ = ZoneInfo("Asia/Shanghai")

def get_current_beijing_time() -> datetime.datetime:
    """获取当前的北京时间（无视运行这行代码的服务器在哪）"""
    return datetime.datetime.now(tz=BEIJING_TZ)

def parse_odds_api_time(utc_time_str: str) -> datetime.datetime:
    """
    将 The Odds API 返回的 UTC 时间字符串转为北京时间对象
    示例输入: "2026-06-30T15:00:00Z"
    """
    # 替换Z为+00:00以便于原生fromisoformat解析
    utc_time_str = utc_time_str.replace("Z", "+00:00")
    dt_utc = datetime.datetime.fromisoformat(utc_time_str)
    dt_beijing = dt_utc.astimezone(BEIJING_TZ)
    return dt_beijing

def parse_jingcai_time(jc_time_str: str) -> datetime.datetime:
    """
    解析国内网站抓取的时间，自动挂载北京时区
    示例输入: "2026-06-30 22:00:00"
    """
    dt_naive = datetime.datetime.strptime(jc_time_str, "%Y-%m-%d %H:%M:%S")
    dt_beijing = dt_naive.replace(tzinfo=BEIJING_TZ)
    return dt_beijing

def is_match_betable(kickoff_time: datetime.datetime, buffer_minutes: int = 15) -> bool:
    """
    判断比赛是否还可以下注（防过期/防开赛）
    kickoff_time: 必须是带 BEIJING_TZ 时区的 datetime
    buffer_minutes: 提前截止的分钟数（竞彩通常提前停售）
    """
    now = get_current_beijing_time()
    cutoff_time = kickoff_time - datetime.timedelta(minutes=buffer_minutes)
    
    # 如果现在的时间已经超过了截止时间，说明快开踢了或者已经踢完了
    if now >= cutoff_time:
        return False
    return True

def is_jc_system_open() -> bool:
    """
    判断当前北京时间是否在体彩官方售卖系统营业时间内。
    营业时间假设：11:00 AM 到 次日凌晨 02:30 AM
    """
    now = get_current_beijing_time()
    current_hour = now.hour
    current_minute = now.minute
    
    # 转换为当日的分钟数以便判断 (0 到 1439)
    minutes_from_midnight = current_hour * 60 + current_minute
    
    # 凌晨 00:00 (0) 到 02:30 (150) 是营业的
    if 0 <= minutes_from_midnight <= 150:
        return True
    
    # 上午 11:00 (660) 到 23:59 (1439) 是营业的
    if 660 <= minutes_from_midnight <= 1439:
        return True
    
    # 凌晨 02:31 到 上午 10:59 是休市时间
    return False

if __name__ == "__main__":
    # 测试打印当前环境的时间
    print(f"当前北京时间: {get_current_beijing_time()}")
    print(f"体彩系统是否营业: {is_jc_system_open()}")
