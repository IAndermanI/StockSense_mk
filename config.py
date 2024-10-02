from dataclasses import dataclass
from environs import Env

@dataclass
class Config:
    bot_token: str
    admin_ids: list

def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        bot_token=env.str("BOT_TOKEN"),
        admin_ids=env.list("ADMIN_IDS", subcast=int)
    )

config = load_config(".env")