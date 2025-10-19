import os
from dotenv import load_dotenv
from check_typos import check_typos


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")
    
def main():
    # 得られる実行結果
    # 誤字があります。「こんんんちわ」は「こんにちは」に訂正してください。訂正後の文章は以下の通りです。
    # こんにちは、田中太郎です。
    result = check_typos("こんんんちわ、田中太郎です。")
    print(result)

if __name__ == "__main__":
    main()
