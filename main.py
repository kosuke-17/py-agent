import os
from dotenv import load_dotenv
from check_typos import check_typos

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")
    
def main():
    print("Hello from py-agent!")
    
    # check_typos関数を使用
    sample_text = "これはサンプルテキストです。タイオをなおしてください。"
    print(f"\n元のテキスト: {sample_text}")
    
    corrected_text = check_typos(sample_text)
    print(f"修正後: {corrected_text}")


if __name__ == "__main__":
    main()
