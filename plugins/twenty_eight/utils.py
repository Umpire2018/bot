from plugins.tortoise_orm.model import Users
from typing import Union

async def get_user_info(user_id: int):
    """
    Fetch user information from the database.

    :param user_id: The id of the user.
    :return: The user object.
    """
    return await Users.get(tg_id=user_id)

async def parse_bet(bet_input: str) -> Union[dict, str]:
    """
    Parse the user's bet input and return a dictionary containing the bet information.
    If there is an error, return an error message.

    :param bet_input: The user's bet input.
    :return: A dictionary containing the bet information or an error message.
    """
    bet_all: list = ['单', '双', '小', '大']
    user_bet = bet_input.split()

    # Check the input empty or not
    if not user_bet:
        return ' 呀，好像您忘记在命令后输入内容了呢！请您再试一次，记得在命令后输入您想要的内容哦！(っ´ω`c)'
    
    # Check the input length
    if len(user_bet) > 4 :
        return " 啊啊啊，请您注意一下哦，这次输入的值好像有点多了呢！麻烦您再重新输入一下吧！(づ｡◕‿‿◕｡)づ"
    
    # Check the input format
    try:
        for i in range(0, len(user_bet), 2):
            if user_bet[i] not in bet_all or not user_bet[i + 1].isdigit() or int(user_bet[i + 1]) <= 0:
                return " 告诉你一个小秘密哦，您这次输入的格式好像有点问题呢！麻烦您再仔细看看，重新输入一下吧！(っ´∀｀)っ"
    except IndexError:
        return " 告诉你一个小秘密哦，您这次输入的格式好像有点问题呢！麻烦您再仔细看看，重新输入一下吧！(っ´∀｀)っ"
    
    # Check for duplicate bets
    for x in bet_all:
        if user_bet.count(x) > 1:
            return " 噢噢噢，您的输入值中居然有重复的筹码呢！这可不行哦！麻烦您再检查一下，重新输入一下吧！(っ˘･з･˘)っ"

    # Check for conflicting bets
    if set(bet_all[:2]).issubset(set(user_bet)) or set(bet_all[2:]).issubset(set(user_bet)):
        return " 呀~您输入的值中有些筹码是互斥的呢！这可不行不行哦！请您再仔细看看，重新输入一下吧！(ﾉ*>∀<)ﾉ♡"

    # Convert the bet input to a dictionary
    user_bet_dict = {}
    for i in range(0, len(user_bet), 2):
        user_bet_dict.update({user_bet[i]: user_bet[i + 1]})

    return user_bet_dict