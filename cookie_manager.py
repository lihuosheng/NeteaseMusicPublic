import os
from typing import Dict

class CookieManager:
    def __init__(self, cookie_file: str = None, env_var: str = "COOKIES_TXT"):
        """
        :param cookie_file: 备用 cookies 文件路径
        :param env_var: 存放 cookie 的环境变量名
        """
        if cookie_file is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cookie_file = os.path.join(script_dir, 'cookie.txt')

        self.cookie_file = cookie_file
        self.env_var = env_var

    def read_cookie(self) -> str:
        # 先读环境变量
        cookies_env = os.environ.get(self.env_var)
        if cookies_env:
            return cookies_env

        # 环境变量没有，再读文件
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                return f.read()

        raise FileNotFoundError(
            f"环境变量 {self.env_var} 未设置，且文件 {self.cookie_file} 不存在"
        )

    @staticmethod
    def parse_cookie(text: str) -> Dict[str, str]:
        cookie_ = [item.strip().split('=', 1) for item in text.strip().split(';') if item]
        cookie_ = {k.strip(): v.strip() for k, v in cookie_}
        return cookie_
