"""
BONUS — เก็บ SECRET_KEY ไว้ใน .env แทนการ hardcode ในโค้ด
ตรงกับหัวข้อ "BONUS" ในโน้ต The Streaming Playbook

ติดตั้ง: uv add pydantic-settings
ทดสอบ:  uv run python settings.py
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")  # อ่านค่าจากไฟล์นี้อัตโนมัติถ้ามี

    secret_key: str = "dev-only-fallback-change-me"  # ค่า default ไว้เผื่อยังไม่สร้างไฟล์ .env
    algorithm: str = "HS256"


settings = Settings()  # สร้างครั้งเดียว ที่อื่นใน projectก็ import settings ตัวนี้ไปใช้


if __name__ == "__main__":
    print("secret_key:", settings.secret_key)
    print("algorithm:", settings.algorithm)
