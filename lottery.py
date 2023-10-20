import telebot
import uuid
from pymongo import MongoClient
import time
from telebot import types
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton
import threading
import random
import asyncio
from datetime import datetime , timedelta
import csv

bot = telebot.TeleBot("6074378866:AAFTSXBqm0zYC2YFgIkbH8br5JeBOMjW3hg")

password = 'VeJ7EH5TK13U4IQg'
cluster_url = 'mongodb+srv://bnslboy:' + \
    password + '@cluster0.avbmi1g.mongodb.net/'

client = MongoClient(cluster_url)

db = client['main']

giveaways = db['giveaways']

invites = db['invites']

roles = db['roles']

owners = db['admins']

queries = db['query']

messages = db['messages']

dices = db['dices']

quizs = db['quizs']

active_quizs = {}

emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

# provide inline markup in main menu /setting --> group 
def add_inline_markup(chat_id):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="📜Roles" , callback_data=f"roles:{chat_id}")
    button2 = InlineKeyboardButton(text="🎉Giveaways",callback_data=f"giveaways:{chat_id}")
    button3 = InlineKeyboardButton(text="👥Invite",callback_data=f"invite:{chat_id}")
    button4 = InlineKeyboardButton(text="🎰 Dice Giveaway",callback_data=f"dice_giveaway:{chat_id}")
    button5 = InlineKeyboardButton(text="Quiz ❓",callback_data=f"quiz:{chat_id}")
    markup.add(button1,button3)
    markup.add(button2,button4)
    markup.add(button5)
    return markup

# provide inline markup in invite section 
def add_inline_invite(chat_id,txt,y):
    markup = InlineKeyboardMarkup()
    button3 = InlineKeyboardButton(f"{txt}", callback_data=f"invite_message:{chat_id}:{y}")
    button4 = InlineKeyboardButton("Active Roles📔", callback_data=f"invite_roles:{chat_id}")
    markup.add(button3, button4)
    button5 = InlineKeyboardButton("Weekly LeaderBoard", callback_data=f"week_invite:{chat_id}")
    button6 = InlineKeyboardButton("Custom LeaderBoard", callback_data=f"custom_invite:{chat_id}")
    markup.add(button5, button6)
    button0 = InlineKeyboardButton("Export All Data 🖨", callback_data=f"export_invite:{chat_id}")
    button1 = InlineKeyboardButton("🗑 Erase All Data", callback_data=f"erase_invite:{chat_id}")
    markup.add(button0, button1)
    button2 = InlineKeyboardButton(text="🔙 Back", callback_data=f"settings:{chat_id}")
    markup.add(button2)
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith(("settings:")):
        chat_id = int(call.data.split(":")[1])
        chat = bot.get_chat(chat_id)
        #Please provide me the name of role 
        msg_text = f"""<b>设置
组： <code>{chat.title}</code></b>

<i>选择要更改的设置之一。</i>"""
        markup = add_inline_markup(chat_id)
        bot.edit_message_text(msg_text,chat_id=call.from_user.id,message_id=call.message.id,parse_mode='HTML',reply_markup=markup)
    elif call.data.startswith(("roles:")):
        chat_id = int(call.data.split(":")[1])
        markup = InlineKeyboardMarkup(row_width=2)
        button1 = InlineKeyboardButton("➕ Create New" , callback_data=f"create_role:{chat_id}")
        markup.add(button1)
        data = roles.find({'chat_id':chat_id})
        if data:
            for da in data:
                if 'role_name' in da:
                    count = da['count']
                    role = da['role_name']
                    button1 = InlineKeyboardButton(f"{role} [{count}]",callback_data=f"role_name:{role}:{chat_id}")
                    markup.add(button1)
        button2 = InlineKeyboardButton(text="🔙Back",callback_data=f"settings:{chat_id}")
        markup.add(button2)
        msg_text = """在此菜单中，您可以创建角色
可用于幸运抽奖。

<i>您也可以从此菜单管理活动角色。</i> """
        bot.edit_message_text(msg_text,call.from_user.id,call.message.id,parse_mode='HTML',reply_markup=markup)
    elif call.data.startswith(("role_name:")):
        role_name = call.data.split(":")[1]
        chat_id = int(call.data.split(":")[2])
        data = roles.find({'chat_id':chat_id , 'roles':role_name})
        msg_text = f"""<b>具有 {role_name} 角色的用户列表\n\n</b>"""
        if data:
            for da in data:
                user_id = da['user_id']
                name = da['first_name']
                msg_text += f"- @{name} "
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton("➕Add User",callback_data=f"adduser:{role_name}:{chat_id}")
        button2 = InlineKeyboardButton("➖Remove User",callback_data=f"removeuser:{role_name}:{chat_id}")
        markup.add(button,button2)
        button4 = InlineKeyboardButton("✏️Edit Role",callback_data=f"edit_role:{role_name}:{chat_id}")
        button5 = InlineKeyboardButton("🗑Delete Role" , callback_data=f"del_role:{role_name}:{chat_id}")
        markup.add(button4,button5)
        msg_text += "\n\n<i>使用以下选项添加/删除用户</i>"
        button3 = InlineKeyboardButton(text="🔙Back",callback_data=f"roles:{chat_id}")
        markup.add(button3)
        bot.edit_message_text(msg_text,call.from_user.id,call.message.id,parse_mode='HTML',reply_markup=markup)
    elif call.data.startswith(("del_role:")):
        role_name = call.data.split(":")[1]
        chat_id = int(call.data.split(":")[2])
        data = roles.find_one({'chat_id':chat_id,'role_name':role_name})
        if data:
            markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
            button1 = KeyboardButton("🚫Cancle")
            button2 = KeyboardButton("🗑Delete")
            markup.add(button1,button2)
            msg2 = bot.send_message(call.message.chat.id,f"Are you sure to Delete {role_name} role ?",reply_markup=markup)
            bot.register_next_step_handler(call.message,delete_role,chat_id,role_name,msg2)
        else:
            bot.answer_callback_query(call.id,f"This {role_name} does not exist anymore !!",show_alert=True,cache_time=3)
    elif call.data.startswith(("create_role:")):
            markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
            button1 = KeyboardButton("🚫Cancle")
            markup.add(button1)
            chat_id = int(call.data.split(":")[1])
            msg2 = bot.send_message(call.message.chat.id,"<b>Send me role name</b> \n\n<i>must be in one word</i>",parse_mode='HTML',reply_markup=markup)
            bot.register_next_step_handler(call.message,create_role,chat_id,msg2)
    elif call.data.startswith(("edit_role:")):
        role_name = call.data.split(":")[1]
        chat_id = int(call.data.split(":")[2])
        data = roles.find_one({'chat_id':chat_id,'role_name':role_name})
        if data:
            role_count = data['count']
            msg_text = f"Role - {role_name}\nCount - {role_count}\n"
            markup = InlineKeyboardMarkup()
            if 'how_to_get' in data:
                how_to_get = data['how_to_get']
                msg_text += f"How to Get - {how_to_get}\n"
            else:
                msg_text+= f"How to Get - None\n"
            button4 = InlineKeyboardButton("✏️Edit How to get",callback_data=f"edit_how_to_get:{role_name}:{chat_id}")
            button5 = InlineKeyboardButton("✏️Change Role Name",callback_data=f"change_role_name:{role_name}:{chat_id}")
            markup.add(button4,button5)
            if "is_auto_invite" in data and data['is_auto_invite'] == True:
                auto_add = data['is_auto_invite']
                count = data['invite_count']
                msg_text += f"Auto Invite - {auto_add}\nInvite Count - {count}\n"
                
                button1 = InlineKeyboardButton("✔️ Auto Invite",callback_data=f'auto_invite_true:{role_name}:{chat_id}')   
            else:
                msg_text += f"Auto Invite - None\n"
                button1 = InlineKeyboardButton("✖️ Auto Invite",callback_data=f'auto_invite_false:{role_name}:{chat_id}')  
            if "is_auto_message" in data and data['is_auto_message'] == True:
                auto_add = data['is_auto_message']
                count = data['message_count']
                msg_text += f"Auto Message - {auto_add}\nMessage Count - {count}\n"
                button2 = InlineKeyboardButton("✔️ Auto Message",callback_data=f'auto_message_true:{role_name}:{chat_id}')
                markup.add(button1,button2)
            else:
                msg_text += f"Auto Message - None\n"
                button2 = InlineKeyboardButton("✖️ Auto Message",callback_data=f'auto_message_false:{role_name}:{chat_id}')
                markup.add(button1,button2)
            button3 = InlineKeyboardButton(text="🔙Back",callback_data=f"role_name:{role_name}:{chat_id}")
            markup.add(button3)
            bot.edit_message_text(msg_text,call.from_user.id,call.message.id,parse_mode='HTML',reply_markup=markup)
        else:
            bot.answer_callback_query(call.id,f"This {role_name} does not exist anymore !!",show_alert=True,cache_time=3)
    elif call.data.startswith(("edit_how_to_get:")):
        role_name = call.data.split(":")[1]
        chat_id = int(call.data.split(":")[2])
        data = roles.find_one({'chat_id':chat_id,'role_name':role_name})
        if data:
            markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
            button1 = KeyboardButton("🚫Cancle")
            markup.add(button1)
            msg2 = bot.send_message(call.message.chat.id,"Send me description how to get this role",reply_markup=markup)
            bot.register_next_step_handler(call.message,add_how_to_get,chat_id,role_name,msg2)
        else:
            bot.answer_callback_query(call.id,"Error in finding this role ")
    elif call.data.startswith(("change_role_name:")):
        role_name = call.data.split(":")[1]
        chat_id = int(call.data.split(":")[2])
        data = roles.find_one({'chat_id':chat_id,'role_name':role_name})
        if data:
            markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
            button1 = KeyboardButton("🚫Cancle")
            markup.add(button1)
            msg2 = bot.send_message(call.message.chat.id,"Send me new name for this role",reply_markup=markup)
            bot.register_next_step_handler(call.message,change_role_name,role_name,chat_id,msg2)
        else:
            bot.answer_callback_query(call.id,"Error in finding this role ")
    elif call.data.startswith(("auto_invite_true:","auto_invite_false:")):
        role_name = call.data.split(":")[1]
        chat_id = int(call.data.split(":")[2])
        data = roles.find_one({'chat_id':chat_id,'role_name':role_name})
        if data:
            if call.data.startswith(("auto_invite_true:")):
                markup = InlineKeyboardMarkup()
                button4 = InlineKeyboardButton("✏️Edit How to get",callback_data=f"edit_how_to_get:{role_name}:{chat_id}")
                button5 = InlineKeyboardButton("✏️Change Role Name",callback_data=f"change_role_name:{role_name}:{chat_id}")
                markup.add(button4,button5)
                button1 = InlineKeyboardButton("✖️ Auto Invite",callback_data=f'auto_invite_false:{role_name}:{chat_id}')
                if "is_auto_message" in data and data['is_auto_message'] == True:
                    button2 = InlineKeyboardButton("✔️ Auto Message",callback_data=f'auto_message_true:{role_name}:{chat_id}')
                    markup.add(button1,button2)
                else:
                    button2 = InlineKeyboardButton("✖️ Auto Message",callback_data=f'auto_message_false:{role_name}:{chat_id}')
                    markup.add(button1,button2)
                button3 = InlineKeyboardButton(text="🔙Back",callback_data=f"role_name:{role_name}:{chat_id}")
                markup.add(button3)
                roles.update_one({'chat_id':chat_id,'role_name':role_name},{'$set':{'is_auto_invite':False}},upsert=True)
                bot.edit_message_reply_markup(call.message.chat.id,call.message.id,reply_markup=markup)
            elif call.data.startswith(("auto_invite_false:")):
                markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
                button1 = KeyboardButton("🚫Cancle")
                markup.add(button1)
                msg2 = bot.send_message(call.message.chat.id,"Send me number how many members user need to add in group to get this role",reply_markup=markup)
                bot.register_next_step_handler(call.message,auto_invite_update,chat_id,role_name,msg2)
    elif call.data.startswith(("auto_message_true:","auto_message_false:")):
        role_name = call.data.split(":")[1]
        chat_id = int(call.data.split(":")[2])
        data = roles.find_one({'chat_id': chat_id, 'role_name': role_name})

        if data:
            if call.data.startswith(("auto_message_true:")):
                markup = InlineKeyboardMarkup()
                button4 = InlineKeyboardButton("✏️Edit How to get", callback_data=f"edit_how_to_get:{role_name}:{chat_id}")
                button5 = InlineKeyboardButton("✏️Change Role Name", callback_data=f"change_role_name:{role_name}:{chat_id}")
                markup.add(button4, button5)

                if "is_auto_invite" in data and data['is_auto_invite'] == True:
                    button1 = InlineKeyboardButton("✔️ Auto Invite", callback_data=f'auto_invite_true:{role_name}:{chat_id}')
                    markup.add(button1)
                else:
                    button1 = InlineKeyboardButton("✖️ Auto Invite", callback_data=f'auto_invite_false:{role_name}:{chat_id}')
                    markup.add(button1)

                button2 = InlineKeyboardButton("✖️ Auto Message", callback_data=f'auto_message_false:{role_name}:{chat_id}')
                markup.add(button2)

                button3 = InlineKeyboardButton("🔙Back", callback_data=f"role_name:{role_name}:{chat_id}")
                markup.add(button3)

                roles.update_one({'chat_id': chat_id, 'role_name': role_name}, {'$set': {'is_auto_message': False}}, upsert=True)
                bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=markup)

            elif call.data.startswith(("auto_message_false:")):
                markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                button1 = KeyboardButton("🚫Cancle")
                markup.add(button1)
                msg2 = bot.send_message(call.message.chat.id, "Send me the number of messages required to send to get this role", reply_markup=markup)
                bot.register_next_step_handler(msg2, auto_message_update, chat_id, role_name, msg2)
    elif call.data.startswith(("giveaways:")):
        chat_id = int(call.data.split(":")[1])
        markup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton("➕ Create New" , callback_data=f"create_giveaway:{chat_id}")
        markup.add(button1)
        data = giveaways.find({'chat_id':chat_id})
        if data:
            button2 = InlineKeyboardButton("⏳History" , callback_data=f"history_giveaway:{chat_id}")
            button3 = InlineKeyboardButton("✅Saved Data",callback_data=f"data_giveaway:{chat_id}")
            markup.add(button2,button3)
        button2 = InlineKeyboardButton(text="🔙Back",callback_data=f"settings:{chat_id}")
        markup.add(button2)
        text = "赠品菜单\n"
        text += "选择一个选项:\n"
        text += "➕ 创建新赠品 - 创建一个新的赠品活动。\n"
        text += "以下按钮尚未开发\n"
        text += "⏳ 历史记录 - 查看以前的赠品活动。\n"
        text += "✅ 保存的数据 - 查看保存的赠品数据。"

        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)
    elif call.data.startswith(("create_giveaway:")):
        chat_id = call.data.split(":")[1]
        markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
        button1 = KeyboardButton("🚫Cancle")
        markup.add(button1)

        msg2 = bot.send_message(call.message.chat.id,"🎉 抽奖时间 🎉\n\n🎁 奖励 - ❓",reply_markup=markup)
        bot.register_next_step_handler(call.message,process_to_add,msg2,chat_id)
    elif call.data.startswith(("groleadd:")):
        title = call.data.split(":")[2]
        chat_id = int(call.data.split(":")[1])
        data = roles.find({'chat_id':chat_id})
        markup = InlineKeyboardMarkup()
        text = call.message.text
        is_role = False
        if data:
            for da in data:
                if 'role_name' in da:
                    count = da['count']
                    role = da['role_name']
                    button1 = InlineKeyboardButton(f"{role} [{count}]",callback_data=f"role_to_giveaway:{role}:{title}")
                    markup.add(button1)
                    is_role = True
            text += "\n\n选择您要添加的角色 👇"
        if is_role:
            bot.edit_message_text(text,call.message.chat.id,call.message.id,reply_markup=markup)    
        else:
            bot.answer_callback_query(call.id,"No Role Found")
    elif call.data.startswith(("role_to_giveaway:")):
        title = call.data.split(":")[2]
        role_name = call.data.split(":")[1]
        updated_results = []
        query_document = queries.find_one({'user_id':call.from_user.id})
        for result in query_document['results']:
        # If the 'title' matches, update the 'message_text' field
            if result['title'] == title:
                result['input_message_content']['message_text'] += f" {role_name}"
            updated_results.append(result)
        queries.update_one({'user_id': call.from_user.id}, {'$set': {'results': updated_results}})
        text = call.message.text
        sub = "\n\n选择您要添加的角色 👇"
        text = text[:-len(sub)]
        text += f"\n\n要参加此幸运抽奖，您需要拥有 {role_name} 角色"
        markup1 = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton("Send Giveaway",switch_inline_query=f"{title}")
        markup1.add(button1)
        bot.edit_message_text(text,call.message.chat.id,call.message.id,reply_markup=markup1)
    elif call.data.startswith(("giveaway_how_to")):
        role_name = call.data.split(":")[1]
        chat_id = int(call.data.split(":")[2])
        data = roles.find_one({'chat_id':chat_id,'role_name':role_name})
        if data:
            if 'how_to_get' in data:
                how_to_get = data['how_to_get']
                bot.answer_callback_query(call.id,how_to_get,show_alert=True)
    elif call.data.startswith(("join_giveaway:", "leave_giveaway:","Refresh:")):
        giveaway_id = call.data.split(":")[1]
        is_how_to = False
        giveaway = giveaways.find_one({'giveaway_id':giveaway_id})
        if giveaway is None:
            bot.answer_callback_query(call.id, "抱歉，此赠品活动已不再有效。",show_alert=True)
            return
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        role = giveaway["role"]
        if role == None:
            pass
        else:
            chat_id = call.message.chat.id
            role_user = roles.find_one({'chat_id':chat_id,'user_id':user_id,'roles':role})
            if role_user is None:
                bot.answer_callback_query(call.id, f"要参加此抽奖，您必须拥有 {role} 角色。",show_alert=True)
                return
            data = roles.find_one({'chat_id':call.message.chat.id,'role_name':role})
            if data:
                if 'how_to_get' in data:
                    is_how_to = True
                    button12 = InlineKeyboardButton(f"如何获得 {role}", callback_data=f"giveaway_how_to:{role}:{chat_id}")
        

        if call.data.startswith(("leave_giveaway:")):
            giveaway_id = call.data.split(":")[1]
            if user_id not in giveaway["participants"]:
                bot.answer_callback_query(call.id, "您尚未参加此赠品活动。",show_alert=True)
                return
            current_time = time.time()
            giveaway["last_refresh_time"] = current_time
            giveaways.update_one({"giveaway_id": giveaway_id}, {"$set": {"last_refresh_time": giveaway["last_refresh_time"]}})
            giveaway["participants"].remove(user_id)
            giveaways.update_one({"giveaway_id": giveaway_id}, {"$set": {"participants": giveaway["participants"],'is_edit':True}})
            
            bot.answer_callback_query(call.id, "您已成功离开了赠品活动。",show_alert=True)
        elif call.data.startswith(("Refresh:")):
            current_time = time.time()
            last_refresh_time = giveaway["last_refresh_time"]
            defd = current_time - last_refresh_time
            if defd < 20:
                bot.answer_callback_query(call.id, f"Please wait for {20-defd:.2f} sec before refreshing again.")
                return
            giveaway["last_refresh_time"] = current_time
            giveaways.update_one({"giveaway_id": giveaway_id}, {"$set": {"last_refresh_time": giveaway["last_refresh_time"]}})
            giveaway_id = call.data.split(":")[1]
            if user_id not in giveaway["participants"]:
                bot.answer_callback_query(call.id, "You have not joined this giveaway.",show_alert=True)
                return
            time_left = giveaway["duration"]
            join_text = f"参加抽奖"
            url = f"https://t.me/Academy_lottery_assistant_bot?start={giveaway_id}"
            
            leave_call = f"leave_giveaway:{giveaway_id}"
            refresh_test = f"刷新时间 ({time_left//86400}d:{time_left%86400//3600}h:{time_left%3600//60}m:{time_left%60}s)"
            refresh_call = f"Refresh:{giveaway_id}"
            reply_markup = telebot.types.InlineKeyboardMarkup()
            reply_markup.add(telebot.types.InlineKeyboardButton(join_text, url=url))
            reply_markup.add(telebot.types.InlineKeyboardButton("退出抽奖", callback_data=leave_call))
            reply_markup.add(telebot.types.InlineKeyboardButton(refresh_test, callback_data=refresh_call))
            if is_how_to:
                reply_markup.add(button12)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=reply_markup)
        
    elif call.data.startswith(("history_giveaway:")):
        bot.answer_callback_query(call.id,"working on it")
        # chat_id = int(call.data.split(":")[1])
        # data = giveaways.find({'chat_id': chat_id})
        # if data:
        #     for da in data:
        #         if 'is_done' in da:
        #             giveaway_id = da['giveaway_id']
        #             amount = da[amount]
    elif call.data.startswith(("data_giveaway:")):
        bot.answer_callback_query(call.id,"working on it")
    elif call.data.startswith(("invite:")):
        chat_id = int(call.data.split(":")[1])
        bot_member = bot.get_chat_member(chat_id, 6074378866)
        if bot_member.can_invite_users is False:
            bot.answer_callback_query(call.id,"❌ 机器人权限不足，请至少授予以下管理员权限：\n\n⚜️通过链接邀请成员",show_alert=True)
            return

        msg_text = """<b>邀请管理</b>
<i>群组成员可使用 /link 命令自动生成链接。
成员可使用 /invites 命令检查他们的邀请。
成员可使用 /topinvites 命令检查群组的前10名邀请。</i>

<b>统计信息</b>\n"""
        data = owners.find_one({'chat_id':chat_id})
        add_count = data.get('add_count',0)
        invite_count = data.get('invite_count',0)
        num_count = data.get('user_count',0)
        link_count = data.get('link_count',0)
        
        msg_text += f"<i>邀请总数 = {num_count}（通过添加按钮增加的次数：{add_count}次，通过邀请链接增加的次数：{invite_count}次）</i>\n"
        msg_text += f"<i>生成的链接总数 =</i> {link_count}\n\n"
        
        if 'send_msg' in data and data['send_msg'] is True:
            txt = "Send Message ✅"
            y = "y"
            # msg_text += f"<b>{txt} </b>- <i>Bot will send message when a user join via a invite link. Message contain who invites new member and his invite count. </i>\n"
        else:
            txt = "Send Message ❌"
            y = "n"
            # msg_text += f"<b>{txt} </b>- <i>Bot will not send message when a user join via a invite link. Message contain who invites new member and his invite count. </i>\n"
        
        
        markup = add_inline_invite(chat_id,txt,y)
        try:
            bot.edit_message_text(msg_text, call.message.chat.id, call.message.id,parse_mode='HTML',reply_markup=markup)
        except Exception:
            pass
    elif call.data.startswith(("invite_message:")):
   
        chat_id = int(call.data.split(":")[1])
        y = call.data.split(":")[2]
        if y == "y":
            owners.update_one({'chat_id':chat_id},{'$set':{'send_msg':False}})
            txt = "Send Message ❌"
            y = "n"
        elif y == "n":
            owners.update_one({'chat_id':chat_id},{'$set':{'send_msg':True}})
            txt = "Send Message ✅"
            y = "y"
            bot.answer_callback_query(call.id,text="当有人通过邀请链接加入时，\n机器人发送的消息会是这样的：\n\nPerson1 邀请了 Person2",show_alert=True)
        markup = add_inline_invite(chat_id,txt,y)
        try:
            bot.edit_message_reply_markup(call.message.chat.id,call.message.id,reply_markup=markup)
        except Exception:
            pass
    elif call.data.startswith(("invite_roles:")):
        chat_id = int(call.data.split(":")[1])
        data = roles.find({'chat_id': chat_id, 'role_name': {'$exists': True}})
        msg_txt = "活跃角色 || 获取邀请计数\n\n"
        i = 1
        for da in data:
            if 'is_auto_invite' in da and da['is_auto_invite'] is True:
                count = da['invite_count']
                role_name = da['role_name']
                msg_txt += f"{i}. {role_name} -- {count}"
                i = i + 1
        if i == 1:
            bot.answer_callback_query(call.id,"没有找到自动授予用户邀请其他用户时的角色。",show_alert=True)
        else:
            bot.answer_callback_query(call.id,msg_txt,show_alert=True)        
    elif call.data.startswith(("week_invite:")):
        chat_id = int(call.data.split(":")[1])
        leaderboard_invite(chat_id,604800,call.from_user.id)
    elif call.data.startswith(("custom_invite:")):
        chat_id = int(call.data.split(":")[1])
        markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
        button1 = KeyboardButton("🚫Cancle")
        markup.add(button1)
        bot.send_message(call.from_user.id,"1天，1小时，1分钟，1秒 的时间格式为：1d，1h，1m，1s。",reply_markup=markup)
        bot.register_next_step_handler(call.message,invite_time,chat_id)
    elif call.data.startswith(("export_invite:")):
        chat_id = int(call.data.split(":")[1])
        bot.send_message(call.from_user.id,"This Process may takes few seconds in collecting data from database")
        
        invi_data = owners.find_one({'chat_id':chat_id})
        if invi_data:
            link_count = invi_data.get('link_count',0)
            user_count = invi_data.get('user_count',0)
            
            data = invites.find({'chat_id': chat_id, 'first_name': {'$exists': True}}).sort('regular_count',-1)

            selected_fields = ['first_name', 'username', 'regular_count', 'user_id','invite_link']

            # Create a BytesIO object to store CSV content
            with open('invitation_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Total Link Count', 'Total Users Count'])
                csv_writer.writerow([link_count, user_count])
                csv_dict_writer = csv.DictWriter(csvfile, fieldnames=selected_fields)
                csv_dict_writer.writeheader()
                for row in data:
                    selected_row = {field: row.get(field, '') for field in selected_fields}
                    csv_dict_writer.writerow(selected_row)
            with open('invitation_data.csv', 'rb') as file:
                bot.send_document(call.message.chat.id, file)
            
            data = invites.find({'chat_id': chat_id, 'first_name': {'$exists': True}}).sort('regular_count',-1)

            data2 = []
            empty_row = {'sr no.': '', 'invited_by': '', 'first_name': '', 'username': '', 'join_time': '','message count':''}
            last_invite_by = ""
            i = 1
            for daa in data:
                for user_id, user_data in daa['users'].items():
                    dat = messages.find_one({'chat_id':chat_id,'user_id':int(user_id)})
                    if dat:
                        message_count = dat['message_count']
                    else:
                        message_count = 0
                    invited_by = daa['username']
                    first_name = user_data['first_name']
                    username = user_data['username']
                    join_time = user_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                    
                    userdata = {'sr no.':i,'invited_by': invited_by, 'first_name': first_name, 'username': username, 'join_time': join_time,'message count':message_count}
                    data2.append(userdata)
                    i += 1
                i = 1
            selected_fields = ['sr no.','invited_by','first_name', 'username', 'join_time','message count']
            with open('invitees_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
                csv_dict_writer = csv.DictWriter(csvfile, fieldnames=selected_fields)
                csv_dict_writer.writeheader()
                for row in data2:
                    if last_invite_by != row['invited_by']:
                        csv_dict_writer.writerow(empty_row)
                        last_invite_by = row['invited_by']
                    selected_row = {field: row.get(field, '') for field in selected_fields}
                    csv_dict_writer.writerow(selected_row)
                    

            with open('invitees_data.csv', 'rb') as file:
                bot.send_document(call.message.chat.id, file)
    elif call.data.startswith(("erase_invite:")):
        chat_id = int(call.data.split(":")[1])
        msg_text = """🚨🚨 请注意，所有邀请链接和邀请数据将很快被清除，此操作无法恢复，是否继续？"""
        markup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton("确认删除所有邀请数据吗",callback_data=f"erase_invite1:{chat_id}")
        button2 = InlineKeyboardButton(text="🔙 Back", callback_data=f"invite:{chat_id}")
        markup.add(button1)
        markup.add(button2)
        bot.edit_message_text(msg_text,call.message.chat.id,call.message.id,reply_markup=markup)
    elif call.data.startswith(("erase_invite1:")):
        chat_id = int(call.data.split(":")[1])
        data = invites.find({'chat_id':chat_id,'invite_link':{'$exists':True}})
        for da in data:
            invite_link = da['invite_link']
            bot.revoke_chat_invite_link(chat_id,invite_link)
        invites.delete_many({'chat_id':chat_id})
        owners.update_one({'chat_id':chat_id},{'$set':{'add_count':0,'invite_count':0,'user_count':0}},upsert=True)
        bot.send_message(call.from_user.id,"所有邀请数据已成功删除。")

    elif call.data.startswith(("dice_giveaway:")):
        chat_id = int(call.data.split(":")[1])
        markup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton("➕ Create New" , callback_data=f"create_dice:{chat_id}")
        markup.add(button1)
        data = dices.find({'chat_id':chat_id})
        if data:
            button2 = InlineKeyboardButton("⏳History" , callback_data=f"history_dice:{chat_id}")
            button3 = InlineKeyboardButton("✅Saved Data",callback_data=f"data_dice:{chat_id}")
            markup.add(button2,button3)
        button2 = InlineKeyboardButton(text="🔙Back",callback_data=f"settings:{chat_id}")
        markup.add(button2)
        text = """骰子抽奖菜单

选择一个选项：
➕ Create New - 创建一个新的骰子活动。
以下按钮正在开发中：
⏳ History - 查看以前的骰子活动。
✅ Saved Data - 查看保存的骰子数据。"""
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)
    elif call.data.startswith(("create_dice:")):
        chat_id = int(call.data.split(":")[1])
        markup = InlineKeyboardMarkup(row_width=5)
        button1 = InlineKeyboardButton("🎲" , callback_data=f"emoji:🎲:{chat_id}")
        button2 = InlineKeyboardButton("🎯" , callback_data=f"emoji:🎯:{chat_id}")
        button3 = InlineKeyboardButton("🏀" , callback_data=f"emoji:🏀:{chat_id}")
        button4 = InlineKeyboardButton("⚽️" , callback_data=f"emoji:⚽️:{chat_id}")
        button5 = InlineKeyboardButton("🎳" , callback_data=f"emoji:🎳:{chat_id}")
        markup.add(button1,button2,button3,button4,button5)
        button6 = InlineKeyboardButton(text="🔙Back",callback_data=f"dice_giveaway:{chat_id}")
        markup.add(button6)
        text = """🎁 骰子赠品抽奖

选择其中一个 🎲、🎯、🏀、⚽️、🎳 来创建抽奖。
设定每个人可以参与的次数以及抽奖结束时间。
群成员可以发送选择的表情来获得积分。
当抽奖结束时，拥有最高积分的参与者获胜。"""
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)
    elif call.data.startswith(("emoji:")):
        chat_id = int(call.data.split(":")[2])
        emoji = call.data.split(":")[1]
        text = f"🎉 表情幸运抽奖 🎉\n\n🍀 发送 {emoji} 表情参与抽奖，获得积分 🍀\n\n🎁 加入 ❓"
        markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
        button1 = KeyboardButton("🚫Cancle")
        markup.add(button1)
        msg2 = bot.send_message(call.message.chat.id,text,reply_markup=markup)
        bot.register_next_step_handler(call.message,dice_event_1,emoji,chat_id,msg2)
    elif call.data.startswith(("diceroleadd:")):
        title = call.data.split(":")[2]
        chat_id = int(call.data.split(":")[1])
        data = roles.find({'chat_id':chat_id})
        markup = InlineKeyboardMarkup()
        text = call.message.text
        is_role = False
        if data:
            for da in data:
                if 'role_name' in da:
                    count = da['count']
                    role = da['role_name']
                    button1 = InlineKeyboardButton(f"{role} [{count}]",callback_data=f"role_dicegiveaway:{role}:{title}")
                    markup.add(button1)
                    is_role = True
            text += "\n\n选择您要添加的角色 👇"
        if is_role:
            bot.edit_message_text(text,call.message.chat.id,call.message.id,reply_markup=markup)    
        else:
            bot.answer_callback_query(call.id,"No Role Found")
    elif call.data.startswith(("role_dicegiveaway:")):
        title = call.data.split(":")[2]
        role_name = call.data.split(":")[1]
        updated_results = []
        query_document = queries.find_one({'user_id':call.from_user.id})
        for result in query_document['results']:
        # If the 'title' matches, update the 'message_text' field
            if result['title'] == title:
                result['input_message_content']['message_text'] += f" role:{role_name}"
            updated_results.append(result)
        queries.update_one({'user_id': call.from_user.id}, {'$set': {'results': updated_results}})
        text = call.message.text
        sub = "\n\n选择您要添加的角色 👇"
        text = text[:-len(sub)]
        text += f"\n\n🌟要参加此幸运抽奖，您需要拥有 {role_name} 角色"
        markup1 = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton("Send Dice Giveaway",switch_inline_query=f"{title}")
        markup1.add(button1)
        bot.edit_message_text(text,call.message.chat.id,call.message.id,reply_markup=markup1)
    elif call.data.startswith(("history_dice:")):
        bot.answer_callback_query(call.id,"working on it")
        # chat_id = int(call.data.split(":")[1])
        # data = giveaways.find({'chat_id': chat_id})
        # if data:
        #     for da in data:
        #         if 'is_done' in da:
        #             giveaway_id = da['giveaway_id']
        #             amount = da[amount]
    elif call.data.startswith(("data_dice:")):
        bot.answer_callback_query(call.id,"working on it")
    elif call.data.startswith(('next_quiz:')):
        chat_id = int(call.data.split(":")[1])
        i = int(call.data.split(":")[2])
        start = 1
        markup = InlineKeyboardMarkup()
        is_change = False
        user_id = call.from_user.id
        data = quizs.find({'user_id':user_id})
        msg_txt = "Your quizs\n\n"
        for dat in data:
            if i < 0:
                break
            if start <= i :
                start += 1
                continue
            is_change = True
            quiz_id = dat['quiz_id']
            title = dat['title']
            time_left = dat.get('time_limit',"Not Set")
            questions = dat.get('questions',{})
            button = InlineKeyboardButton(title,callback_data=f"edit_quiz:{quiz_id}")
            markup.add(button)
            msg_txt += f"{start}. {title}\n❓{len(questions)} questions ▪️ ⏱ {time_left} sec\n\n"
            if start == i + 3:
                break
            start += 1
        button = InlineKeyboardButton("Next ▶️",callback_data=f"next_quiz:{chat_id}:{i+3}")
        button1 = InlineKeyboardButton("◀️ Previous",callback_data=f"next_quiz:{chat_id}:{i-3}")
        markup.add(button1,button)
        button = InlineKeyboardButton("🔙 Back",callback_data=f"settings:{chat_id}")
        markup.add(button)
        if is_change:
            bot.edit_message_text(msg_txt,call.message.chat.id,call.message.id,reply_markup=markup)
        else:
            bot.answer_callback_query(call.id,"No More quiz found **")
    elif call.data.startswith(("quiz:")):
        chat_id = int(call.data.split(":")[1])
        user_id = call.from_user.id
        data = quizs.find({'user_id':user_id})
        
        msg_txt = "Your quizs\n\n"
        i = 1
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton("Create New ➕",callback_data=f"create_quiz")
        markup.add(button)
        if data:
            for dat in data:
                quiz_id = dat['quiz_id']
                title = dat['title']
                time_left = dat.get('time_limit',"Not Set")
                questions = dat.get('questions',{})
                button = InlineKeyboardButton(title,callback_data=f"edit_quiz:{quiz_id}")
                markup.add(button)
                msg_txt += f"{i}. {title}\n❓{len(questions)} questions ▪️ ⏱ {time_left} sec\n\n"
                if i == 3:
                    button = InlineKeyboardButton("Next ▶️",callback_data=f"next_quiz:{chat_id}:{i}")
                    markup.add(button)
                    break
                i = i + 1
        button = InlineKeyboardButton("🔙 Back",callback_data=f"settings:{chat_id}")
        markup.add(button)
        bot.edit_message_text(msg_txt,call.message.chat.id,call.message.id,reply_markup=markup)
    elif call.data == "create_quiz":
        create_quiz(call.message,call.from_user.id)
    elif call.data == "ended":
        bot.answer_callback_query(call.id,"This quiz question already ended. ")
    elif call.data.startswith(("quiz_answer:")):
        try:
            chat_id = call.message.chat.id
            call_ans = call.data.split(":")[1]
            q , correct_an = active_quizs[str(chat_id)]['current_ques']
            correct_ans = correct_an['correct_option2']
            if str(call.from_user.id)in active_quizs[str(chat_id)]['joiners']:
                bot.answer_callback_query(call.id,"Your answer already submited")
                return
            data = active_quizs[str(chat_id)]
            if call_ans == correct_ans:
                time_gap = data['time_gap']
                current_time = datetime.now()
                last_time = data['last_time']
                sc = current_time - last_time
                sec1 = timedelta(seconds=1)
                sco = 500 + time_gap - int(sc/sec1)
                if 'users' in data:
                    if str(call.from_user.id) in data['users'].keys():
                        score = data['users'][str(call.from_user.id)]['score']
                        data['users'][str(call.from_user.id)]['score'] = score + sco
                    else:
                        data['users'][str(call.from_user.id)] = {'score':sco,'username':call.from_user.username,'first_name':call.from_user.first_name}
                else :
                    active_quizs[str(chat_id)]['users'] = {}
                    data['users'][str(call.from_user.id)] = {'score': sco ,'username':call.from_user.username,'first_name':call.from_user.first_name}
            bot.answer_callback_query(call.id,"Answer sucessfully submited ")
            active_quizs[str(chat_id)]['joiners'].append(str(call.from_user.id))
        except Exception as e:
            print(e)
            bot.answer_callback_query(call.id,'Intreaction Failed')
            pass
    elif call.data.startswith(("edit_quiz:")):
        quiz_id = call.data.split(":")[1]
        data = quizs.find_one({'quiz_id':quiz_id})
        if data:
            markup = InlineKeyboardMarkup()
            quiz_id = data['quiz_id']
            title = data['title']
            time_left = data.get('time_limit',"Not Set")
            questions = data.get('questions',{})
            button = InlineKeyboardButton("Add More Questions",callback_data=f"add_quiz:{quiz_id}")
            button1 = InlineKeyboardButton("Edit Question",callback_data=f"edit_ques:{quiz_id}")
            button2 = InlineKeyboardButton("Delete",callback_data=f"delete_quiz:{quiz_id}")
            button3 = InlineKeyboardButton("Edit time limit",callback_data=f"time_quiz:{quiz_id}")
            button4 = InlineKeyboardButton('Share quiz',switch_inline_query=f"{title}")
            markup.add(button,button1)
            markup.add(button2,button3)
            markup.add(button4)
            msg_txt = f"{title}\n❓{len(questions)} questions ▪️ ⏱ {time_left} sec"
            bot.edit_message_text(msg_txt,call.message.chat.id,call.message.id,reply_markup=markup)
        else:
            bot.answer_callback_query(call.id,"Quiz Not Found")
    elif call.data.startswith(("add_quiz:")):
        quiz_id = call.data.split(":")[1]
        data = quizs.find_one({'quiz_id':quiz_id})
        if data:
            bot.answer_callback_query(call.id,"Send me a question")
            markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
            button1 = KeyboardButton("🚫Cancle")
            button2 = KeyboardButton("Create a question",request_poll=telebot.types.KeyboardButtonPollType(type="quiz"))
            markup.add(button2,button1)
            msg2 = bot.send_message(call.from_user.id,"Send Me a question ",reply_markup=markup)
            bot.register_next_step_handler(call.message,create_quiz3,msg2,quiz_id)
    elif call.data.startswith(("edit_ques:")):
        bot.answer_callback_query(call.id,"working on it")
    elif call.data.startswith(("delete_quiz:")):
        quiz_id = call.data.split(":")[1]
        data = quizs.find_one({'quiz_id':quiz_id})
        if data:
            markup = InlineKeyboardMarkup()
            btn = InlineKeyboardButton("Delete Quiz",callback_data=f"del_quiz:{quiz_id}")
            btn2 = InlineKeyboardButton("Delete a Question",callback_data=f"del_ques:{quiz_id}")
            markup.add(btn)
            markup.add(btn2)
            button = InlineKeyboardButton("🔙 Back",callback_data=f"edit_quiz:{quiz_id}")
            markup.add(button)
            bot.edit_message_reply_markup(call.message.chat.id,call.message.id,reply_markup=markup)
        else:
            bot.answer_callback_query(call.id,"Quiz Not Found")
    elif call.data.startswith(("del_ques:")):
        bot.answer_callback_query(call.id,"Working on it")
    elif call.data.startswith(("del_quiz:")):
        quiz_id = call.data.split(":")[1]
        data = quizs.find_one({'quiz_id':quiz_id})
        if data:
            quizs.delete_one({'quiz_id':quiz_id})
            bot.edit_message_text("Quiz Deleted !!!",call.message.chat.id,call.message.id)
        else:
            bot.answer_callback_query(call.id,"Quiz Not Found")
    elif call.data.startswith(("time_quiz:")):
        quiz_id = call.data.split(":")[1]
        data = quizs.find_one({'quiz_id':quiz_id})
        if data:
            markup = quiz_time_keyboard()
            bot.send_message(call.message.chat.id,"Please set a time limit for questions. In groups, the bot will send the next question as soon as this time is up.\n\nWe recommend using longer timers only if your quiz involves complex problems (like math, etc.). For most trivia-like quizzes, 10-30 seconds are more than enough.\n\nLike 10s,20s,30s make sure that time will be round off 10s",reply_markup=markup)
            bot.register_next_step_handler(call.message,quiz_time,quiz_id)
        else:
            bot.answer_callback_query(call.id,"Quiz not found")

def quiz_time(message,quiz_id):
    duration = message.text
    try:
        duration = int(duration[:-1]) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[duration[-1]]
    except Exception as e:
        try:
            bot.delete_message(message.chat.id, message.id)
        except Exception:
            pass
        bot.send_message(message.chat.id,"Error : Time limit should be in the format 1d, 1h, 1m, or 1s.")
        bot.register_next_step_handler(message,quiz_time,quiz_id)
        return
    data = quizs.find_one({'quiz_id':quiz_id})
    if data:
        markup = types.ReplyKeyboardRemove()
        quizs.update_one({'quiz_id':quiz_id},{'$set':{'time_limit':duration}})
        bot.send_message(message.chat.id,f"New time limit is set to {duration} second .",reply_markup=markup)

def quiz_time_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=3)
    button1 = KeyboardButton("10s")
    button2 = KeyboardButton("20s")
    button3 = KeyboardButton("30s")
    button4 = KeyboardButton("1m")
    button5 = KeyboardButton("2m")
    button6 = KeyboardButton("3m")
    button7 = KeyboardButton("5m")
    button8 = KeyboardButton("10m")
    button9 = KeyboardButton("30m")
    markup.add(button1,button2,button3)
    markup.add(button4,button5,button6)
    markup.add(button7,button8,button9)
    return markup

def create_quiz(message,user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button1 = KeyboardButton("🚫Cancle")
    markup.add(button1)
    msg2 = bot.send_message(user_id,"Send me the title of your quiz (e.g., ‘Quiz 1’)",reply_markup=markup)
    bot.register_next_step_handler(message,create_quiz2,user_id,msg2)

def create_quiz2(message,user_id,msg2):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button1 = KeyboardButton("🚫Cancle")
    button2 = KeyboardButton("Create a question",request_poll=telebot.types.KeyboardButtonPollType(type="quiz"))
    markup.add(button2,button1)
    if message.text == "🚫Cancle":
        try:
            bot.delete_message(msg2.chat.id, msg2.id)
            bot.delete_message(message.chat.id, message.id)
            return
        except Exception:
            pass
    quiz_id = str((uuid.uuid4()))
    document = {
        'user_id':message.from_user.id,
        'quiz_id':quiz_id,
        'title':message.text,
        'questions':{}
    }
    quizs.insert_one(document)
    try:
        bot.delete_message(msg2.chat.id, msg2.id)
    except Exception:
        pass
    msg2 = bot.send_message(user_id,"Send Me a quiz ",reply_markup=markup)
    bot.register_next_step_handler(message,create_quiz3,msg2,quiz_id)

def create_quiz3(message,msg2,quiz_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button1 = KeyboardButton("☑️Done")
    button2 = KeyboardButton("Create a question",request_poll=telebot.types.KeyboardButtonPollType(type="quiz"))
    markup.add(button2,button1)
    if message.text == "🚫Cancle":
        bot.delete_message(msg2.chat.id, msg2.id)
        bot.delete_message(message.chat.id, message.id)
        return
    elif message.text == "☑️Done":
        markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=3)
        button1 = KeyboardButton("10s")
        button2 = KeyboardButton("20s")
        button3 = KeyboardButton("30s")
        button4 = KeyboardButton("1m")
        button5 = KeyboardButton("2m")
        button6 = KeyboardButton("3m")
        button7 = KeyboardButton("5m")
        button8 = KeyboardButton("10m")
        button9 = KeyboardButton("30m")
        markup.add(button1,button2,button3)
        markup.add(button4,button5,button6)
        markup.add(button7,button8,button9)
        try:
            bot.delete_message(msg2.chat.id, msg2.id)
            bot.delete_message(message.chat.id, message.id)
        except Exception:
            pass
        msg2 = bot.send_message(message.chat.id,"Please set a time limit for questions. In groups, the bot will send the next question as soon as this time is up.\n\nWe recommend using longer timers only if your quiz involves complex problems (like math, etc.). For most trivia-like quizzes, 10-30 seconds are more than enough.\n\nLike 10s,20s,30s make sure that time will be round off 10s",reply_markup=markup)
        bot.register_next_step_handler(message,create_quiz4,msg2,quiz_id)
        return
    if message.content_type == 'poll':
        data = quizs.find_one({'quiz_id':quiz_id})
        if data:
            try:
                bot.delete_message(msg2.chat.id, msg2.id)
            except Exception:
                pass

            question = message.poll.question
            options = []
            for option in message.poll.options:
                options.append(option.text)
            correct_index = message.poll.correct_option_id
            correct_answer = options[correct_index]
            daa = data['questions']
            title = data['title']
            daa[question] = {'options':options,'correct_option':correct_answer}
            msg2 = bot.send_message(message.chat.id,f"Now your quiz '{title}' have {len(daa)} questions.\n\nNow send the next question\n\nWhen done, simply send ☑️Done to finish creating the quiz.",reply_markup=markup)
            quizs.update_one({'quiz_id':quiz_id},{'$set':{'questions':daa}})
            bot.register_next_step_handler(message,create_quiz3,msg2,quiz_id)
            return
    else:
        bot.send_message(message.chat.id,"Please send a question . Using create a option button")
        bot.register_next_step_handler(message,create_quiz3,msg2,quiz_id)

def create_quiz4(message,msg2,quiz_id):
    duration = message.text
    try:
        duration = int(duration[:-1]) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[duration[-1]]
    except Exception as e:
        try:
            bot.delete_message(message.chat.id, message.id)
        except Exception:
            pass
        bot.send_message(message.chat.id,"Error : Time limit should be in the format 1d, 1h, 1m, or 1s.")
        bot.register_next_step_handler(message,create_quiz4,msg2,quiz_id)
        return
    data = quizs.find_one({'quiz_id':quiz_id})
    if data:
        title = data['title']
        quizs.update_one({'quiz_id':quiz_id},{'$set':{'time_limit':duration}})
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton("Share quiz in Group",url=f"https://t.me/Tic4techgamebot?startgroup=quiz:{quiz_id}")
        button1 = InlineKeyboardButton('Share quiz',switch_inline_query=f"{title}")
        markup.add(button1)
        markup.add(button)
        id = str((uuid.uuid4()))
        result = {
            "id": id,
            "title": title,
            "input_message_content": {
                "message_text": f"/quies {quiz_id}"
            }
        }
        queries.update_one(
            {'user_id': message.from_user.id},
            {'$addToSet': {'results': result}},
            upsert=True
        )
        ques = data['questions']
        markup2 = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,"👍 Quiz created.",reply_markup=markup2)
        bot.send_message(message.chat.id,f"<b>{title}</b>\n❓{len(ques)} ▪️ ⏱ {duration} sec",reply_markup=markup,parse_mode='HTML')


def time_check2():
    with lock:
        time.sleep(10)
        while True:
            i= 1
            try:
                for chat_id , data in active_quizs.items():
                    current_time = datetime.now()
                    last_time = data['last_time']
                    time_gap = timedelta(seconds=data['time_gap'])
                    i = i + 1
                    if last_time + time_gap <= current_time:
                        ques = data['questions']
                        if data['edit_msg']:
                            msg_id = data['msg_id']
                            markup = InlineKeyboardMarkup()
                            button = InlineKeyboardButton("Ended",callback_data="ended")
                            markup.add(button)
                            bot.edit_message_reply_markup(chat_id,msg_id,reply_markup=markup)
                            data['edit_msg'] = False
                            ques2 = data['current_ques']
                            que , data4 = ques2
                            correct_answer2 = data4['correct_option']
                            bot.send_message(chat_id,f"<b>{que}</b>\nTime's up!\n\ncorrect ans - {correct_answer2}",parse_mode='HTML')
                        if data['send_leader']:
                            if 'users' in data:
                                msg_txt = "<b>Leaderboard</b>\n\n"
                                sorted_participant = sorted(data["users"].items(), key=lambda x: x[1]['score'], reverse=True)
                                if int(data['total_ques']) == (int(data['done_ques'])-1):
                                    msg_txt = "<b>Final Leaderboard</b>\n\n"
                                    end = 20
                                    for j, (user_id, data3) in enumerate(sorted_participant,start=1):
                                        if j == end:
                                            end += 20
                                            bot.send_message(chat_id,msg_txt,parse_mode='HTML')
                                            msg_txt = "----------------\n"
                                        username = data3['username']
                                        if username is None:
                                            username = data3['first_name']
                                        score = data3['score']
                                        msg_txt += f"#{j}. {username} - {score}"
                                        if j <= 10:
                                            data10 = roles.find_one({'chat_id': chat_id, 'user_id': user_id,'roles': "top-10"})
                                            if data10 is None:
                                                roles.update_one({'chat_id': int(chat_id), 'user_id': int(user_id)},
                                                    {'$addToSet': {'roles': "top-10"},
                                                    '$set': {'first_name': username}}, upsert=True)
                                                roles.update_one({'chat_id':int(chat_id),'role_name':"top-10"},
                                                    {'$inc':{'count':1}},upsert=True)
                                            msg_txt += "- 'top-10'\n"
                                        else:
                                            msg_txt += "\n"
                                    bot.send_message(chat_id,msg_txt,parse_mode='HTML')
                                else:
                                    for j, (user_id, data3) in enumerate(sorted_participant,start=1):
                                        if j > 10:
                                            break
                                        username = data3['username']
                                        if username is None:
                                            username = data3['first_name']
                                        score = data3['score']
                                        msg_txt += f"#{j}. {username} - {score}\n"
                                    bot.send_message(chat_id,msg_txt,parse_mode='HTML')
                                    pass
                            else:
                                bot.send_message(chat_id,"No one participate yet\n\nQuiz will continue in 10 sec")
                            data['send_leader'] = False
                            continue
                        data['last_time'] = current_time
                        if len(ques) == 0:
                            del active_quizs[str(chat_id)]
                            continue
                        for q ,data2 in ques.items():
                            correct_answer = data2['correct_option']
                            total = data['total_ques']
                            if 'done_ques' in data:
                                done = data['done_ques']
                            else:
                                done = 1
                            data['current_ques'] = q , data2
                            del active_quizs[str(chat_id)]['questions'][q]
                            msg_text = f"<b>[{done}/{total}] {q} </b>\n\n"
                            active_quizs[str(chat_id)]['done_ques'] = done + 1
                            buttons = []
                            but = []
                            for start , option in enumerate(data2['options'],start=1):
                                if start == 6:
                                    buttons.append(but)
                                    but = []
                                emoji = emojis[start - 1]
                                msg_text += f"{emoji} {option}\n"
                                if correct_answer == option:
                                    data2['correct_option2'] = str(start)
                                button1 = InlineKeyboardButton(f"{emoji}",callback_data=f"quiz_answer:{start}")
                                but.append(button1)
                            buttons.append(but)
                            markup = InlineKeyboardMarkup(buttons,row_width=5) 
                            msg = bot.send_message(chat_id,msg_text,reply_markup=markup,parse_mode='HTML')
                            data['edit_msg'] = True
                            data['send_leader'] = True
                            data['msg_id'] = msg.id
                            active_quizs[str(chat_id)]['joiners'] = []
                            break
            except Exception as e:      
                time_thread = threading.Thread(target=time_check2)
                time_thread.start()
                print(e)
                pass
            if i == 1:
                return False
            time.sleep(10)

def start_quiz(quiz_id,chat_id,msg_id):
    
    data = quizs.find_one({'quiz_id':quiz_id})
    if data:
        questions = data['questions']
        time_gap = data['time_limit']
        current_time = datetime.now() - timedelta(seconds=time_gap)
        length = len(questions)
        active_quizs[str(chat_id)] = {'questions':questions,'time_gap':time_gap,'last_time':current_time,'quiz_id':quiz_id,'total_ques':length,
                                      'edit_msg':False,'send_leader':False}
        msg_text = f"🏁 Get Ready For Quiz '{data['title']}'\n\n❓{len(questions)} questions\n⏱{time_gap} seconds per question."
        msg_text+=f"\n🔹A correct answer awards 500-{500 + time_gap} points."
        bot.send_message(chat_id,msg_text)
        try:
            if msg_id:
                bot.delete_message(chat_id,msg_id)
        except Exception:
            pass
        time_thread = threading.Thread(target=time_check2)
        time_thread.start()
    else:
        bot.send_message(chat_id,"Quiz not found")



def dice_event_1(message,emoji,chat_id,msg2):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button1 = KeyboardButton("🚫Cancle")
    markup.add(button1)
    if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id, msg2.id)
            bot.delete_message(message.chat.id, message.id)
            return
    reward = message.text
    bot.delete_message(msg2.chat.id, msg2.id)
    msg2 = bot.send_message(message.chat.id,f"🎉 表情幸运抽奖 🎉\n\n🍀 发送 {emoji} 表情参与抽奖，获得积分 🍀\n\n🎁 加入 {reward} \n\n🏆 ❓ 次机会参与！🌟",reply_markup=markup)
    bot.register_next_step_handler(message,dice_event_2,emoji,chat_id,reward,msg2)

def dice_event_2(message,emoji,chat_id,reward,msg2):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button1 = KeyboardButton("🚫Cancle")
    markup.add(button1)
    if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id, msg2.id)
            bot.delete_message(message.chat.id, message.id)
            return
    try:
        chances = int(message.text)
    except Exception:
        bot.delete_message(msg2.chat.id, msg2.id)
        bot.send_message(message.chat.id,"Send me no. of chances like 3,5,7",reply_markup=markup)
        bot.register_next_step_handler(message,dice_event_2,emoji,chat_id,reward,msg2)
        return
    bot.delete_message(msg2.chat.id, msg2.id)
    msg2 = bot.send_message(message.chat.id,f"🎉 表情幸运抽奖 🎉\n\n🍀 发送 {emoji} 表情参与抽奖，获得积分 🍀\n\n🎁 加入 {reward} \n\n🏆 {chances} 次机会参与！🌟\n\n⏰ 倒计时 - ❓ 🔥",reply_markup=markup)
    bot.register_next_step_handler(message,dice_event_3,emoji,chat_id,reward,chances,msg2)

def dice_event_3(message,emoji,chat_id,reward,chances,msg2):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button1 = KeyboardButton("🚫Cancle")
    markup.add(button1)
    if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id, msg2.id)
            bot.delete_message(message.chat.id, message.id)
            return
    duration = message.text
    try:
        duration = int(duration[:-1]) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[duration[-1]]
    except Exception as e:
        bot.delete_message(message.chat.id, message.id)
        bot.send_message(message.chat.id,"Error : Duration should be in the format 1d, 1h, 1m, or 1s.",reply_markup=markup)
        bot.register_next_step_handler(message,dice_event_3,emoji,chat_id,reward,chances,msg2)
        return
    time_left = duration
    time_left_str = f"{time_left // 86400}d:{(time_left % 86400) // 3600}h:{(time_left % 3600) // 60}m:{time_left % 60}s"
    id = str(uuid.uuid4())
    reward = reward.replace(" ", "_")
    message_text = f"/dices {emoji} {chances} {reward} {duration}s"
    title = str(uuid.uuid4())
    result = {
            "id": id,
            "title": title,
            "input_message_content": {
                "message_text": message_text
            }
        }
    queries.update_one(
            {'user_id': message.from_user.id},
            {'$addToSet': {'results': result}},
            upsert=True
        )
    markup1= InlineKeyboardMarkup()
    bot.delete_message(msg2.chat.id, msg2.id)
    button1 = InlineKeyboardButton("Send Dice Giveaway",switch_inline_query=f"{title}")
    markup1.add(button1)
    button2 = InlineKeyboardButton("Add Role Required",callback_data=f"diceroleadd:{chat_id}:{title}")
    markup1.add(button2)
    bot.send_message(message.chat.id,f"🎉 表情幸运抽奖 🎉\n\n🍀 发送 {emoji} 表情参与抽奖，获得积分 🍀\n\n🎁 加入 {reward} \n\n🏆 {chances} 次机会参与！🌟\n\n⏰ 倒计时 - {time_left_str} 🔥\n\n🎊 取得高分 & 赢得大奖！🎁\n\n💥 不要错过！🎉" , reply_markup=markup1)

def process_to_add(message,msg2,chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button1 = KeyboardButton("🚫Cancle")
    markup.add(button1)
    if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id, msg2.id)
            bot.delete_message(message.chat.id, message.id)
            return
    reward = message.text
    bot.delete_message(msg2.chat.id, msg2.id)
    msg2 = bot.send_message(message.chat.id,f"🎉 抽奖时间 🎉\n\n🎁 奖励 - {reward}\n\n🏆 获奖人数 - ❓",reply_markup=markup)
    bot.register_next_step_handler(message,process_to_add_2 , msg2,chat_id,reward)

def process_to_add_2(message ,msg2,chat_id,reward):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button1 = KeyboardButton("🚫Cancle")
    markup.add(button1)
    if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id, msg2.id)
            bot.delete_message(message.chat.id, message.id)
            return
    try:
        num_winners = int(message.text)
    except Exception:
        bot.send_message(message.chat.id,"Number of winners should in integer value . Enter again ! ")
        bot.register_next_step_handler(message , process_to_add_2 , msg2 ,chat_id,reward)
        return
    bot.delete_message(msg2.chat.id, msg2.id)
    msg2 = bot.send_message(message.chat.id,f"🎉 抽奖时间 🎉\n\n🎁 奖励 - {reward}\n\n🏆 获奖人数 - {num_winners}\n\n⏱ 剩余时间 - ❓",reply_markup=markup)

    bot.register_next_step_handler(message , process_to_add_3 , msg2 ,chat_id,reward, num_winners)

def process_to_add_3(message,msg2 ,chat_id,reward, num_winners):
    markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button1 = KeyboardButton("🚫Cancle")
    markup.add(button1)
    if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id, msg2.id)
            bot.delete_message(message.chat.id, message.id)
            return
    duration = message.text
    try:
        duration = int(duration[:-1]) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[duration[-1]]
    except Exception as e:
        bot.delete_message(message.chat.id, message.id)
        bot.send_message(message.chat.id,"Error : Duration should be in the format 1d, 1h, 1m, or 1s.",reply_markup=markup)
        bot.register_next_step_handler(message , process_to_add_3 , msg2 ,chat_id,reward, num_winners)
        return
    
    time_left = duration
    time_left_str = f"{time_left // 86400}d:{(time_left % 86400) // 3600}h:{(time_left % 3600) // 60}m:{time_left % 60}s"
    id = str(uuid.uuid4())
    description = f"Giveaway of {reward} in {num_winners} winners \n which ends in {time_left_str} duration"
    reward = reward.replace(" ", "_")
    message_text = f"/giveaway {reward} {num_winners} {duration}s"
    title = str(uuid.uuid4())
    result = {
            "id": id,
            "title": title,
            "description":description,
            "input_message_content": {
                "message_text": message_text
            }
        }
    queries.update_one(
            {'user_id': message.from_user.id},
            {'$addToSet': {'results': result}},
            upsert=True
        )
    # bot.edit_message_reply_markup(message.chat.id,msg2.id,reply_markup=markup)
    markup1= InlineKeyboardMarkup()
    bot.delete_message(msg2.chat.id, msg2.id)
    button1 = InlineKeyboardButton("Send Giveaway",switch_inline_query=f"{title}")
    markup1.add(button1)
    button2 = InlineKeyboardButton("Add Role Required",callback_data=f"groleadd:{chat_id}:{title}")
    markup1.add(button2)
    bot.send_message(message.chat.id,f"🎉 抽奖时间 🎉\n\n🎁 奖励 - {reward}\n\n🏆 获奖人数 - {num_winners}\n\n⏱ 剩余时间 - {time_left_str}" , reply_markup=markup1)
    
def auto_message_update(message, chat_id, role_name, msg2):
    markup = telebot.types.ReplyKeyboardRemove()
    try:
        if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id, msg2.id)
            bot.delete_message(message.chat.id, message.id)
            return

        count = int(message.text)

        roles.update_one(
            {'chat_id': chat_id, 'role_name': role_name},
            {'$set': {'message_count': count, 'is_auto_message': True}},
            upsert=True
        )

        bot.send_message(message.chat.id, "Auto Message has been updated.",reply_markup=markup)
        bot.delete_message(msg2.chat.id, msg2.id)
        bot.delete_message(message.chat.id, message.id)

    except Exception as e:
        print(f"Error updating auto_message for role: {e}")
        bot.send_message(message.chat.id, "发生错误。请稍后再试。", reply_markup=markup)

def auto_invite_update(message,chat_id,role_name,msg2):
    markup = telebot.types.ReplyKeyboardRemove()
    try:
        if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id,msg2.id)
            bot.delete_message(message.chat.id,message.id)
            return
        count = int(message.text)

        roles.update_one(
            {'chat_id': chat_id, 'role_name': role_name},
            {'$set': {'invite_count': count , 'is_auto_invite':True }},
            upsert=True
        )
        data = invites.find({'chat_id':chat_id})
        if data:
            for da in data:
                user_id = da['user_id']
                regular_count = da['regular_count']
                if regular_count >= count :
                    roles.update_one({'chat_id': chat_id, 'user_id': user_id}, {'$addToSet': {'roles': role_name}}, upsert=True)
                    roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':1}},upsert=True)
        bot.send_message(message.chat.id,"Auto Invite has been added",reply_markup=markup)
        bot.delete_message(msg2.chat.id,msg2.id)
        bot.delete_message(message.chat.id,message.id)
    except Exception as e:
        print(f"Error creating role: {e}")
        bot.send_message(message.chat.id, "发生错误。请稍后再试。", reply_markup=markup)

def create_role(message,chat_id,msg2):
    markup = telebot.types.ReplyKeyboardRemove()
    try:
        if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id,msg2.id)
            bot.delete_message(message.chat.id,message.id)
            return
        role_name = message.text.split(' ')[0].lower()
        find = roles.find_one({'chat_id': chat_id, 'role_name': role_name})
        if find:
            bot.delete_message(msg2.chat.id,msg2.id)
            bot.delete_message(message.chat.id,message.id)
            bot.send_message(message.chat.id, f"角色 '{role_name}' 已存在。", reply_markup=markup)
            return
        role_id = str(uuid.uuid4())
        roles.update_one({'chat_id': chat_id,'role_id':role_id}, {'$set': {'role_name': role_name}, '$inc': {'count': 0}}, upsert=True)
        bot.send_message(message.chat.id, f"角色 '{role_name}' 已创建成功。", reply_markup=markup)
        bot.delete_message(msg2.chat.id,msg2.id)
        bot.delete_message(message.chat.id,message.id)
    except Exception as e:
        print(f"Error creating role: {e}")
        bot.send_message(message.chat.id, "发生错误。请稍后再试。", reply_markup=markup)

def delete_role(message,chat_id, role_name,msg2):
    markup = telebot.types.ReplyKeyboardRemove()
    try:
        if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id, msg2.id)
            bot.delete_message(message.chat.id, message.id)
            return
        elif message.text == "🗑Delete":
            role_deleted = False
            users_with_role = roles.find({'chat_id': chat_id, 'roles': role_name})

            for user in users_with_role:
                user_id = user['user_id']

                roles.update_one({'chat_id': chat_id, 'user_id': user_id}, {'$pull': {'roles': role_name}})
                role_deleted = True

            roles.delete_one({'chat_id':chat_id,'role_name':role_name})
            if role_deleted:
                bot.send_message(msg2.chat.id, f"已从所有用户中移除 {role_name} 角色。", reply_markup=markup)
                bot.delete_message(msg2.chat.id, msg2.id)
                bot.delete_message(message.chat.id, message.id)
            else:
                bot.send_message(msg2.chat.id, f"没有用户拥有 {role_name} 角色。", reply_markup=markup)
                bot.delete_message(msg2.chat.id, msg2.id)
                bot.delete_message(message.chat.id, message.id)
    except Exception as e:
        print(f"Error deleting role: {e}")
        bot.send_message(message.chat.id, "发生错误。请稍后再试。", reply_markup=markup)

def add_how_to_get(message,chat_id,role_name,msg2):
    markup = telebot.types.ReplyKeyboardRemove()
    try:
        if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id,msg2.id)
            bot.delete_message(message.chat.id,message.id)
            return
        find = roles.find_one({'chat_id': chat_id, 'role_name': role_name})
        how_to_get = message.text
        if find:
            bot.delete_message(msg2.chat.id,msg2.id)
            bot.delete_message(message.chat.id,message.id)
            roles.update_one({'chat_id': chat_id, 'role_name': role_name},{'$set':{'how_to_get':how_to_get}},upsert=True)
            bot.send_message(message.chat.id, f" How to get is now set for {role_name} ", reply_markup=markup)
    except Exception as e:
        print(f"Error creating role: {e}")
        bot.send_message(message.chat.id, "Error in setting how to get ion role", reply_markup=markup)

def change_role_name(message,old_role_name, chat_id,msg2):
    markup = telebot.types.ReplyKeyboardRemove()
    try:
        if message.text == "🚫Cancle":
            bot.delete_message(msg2.chat.id,msg2.id)
            bot.delete_message(message.chat.id,message.id)
            return
        role = roles.find_one({'chat_id': chat_id, 'role_name': old_role_name})
        new_role_name = message.text.split(" ")[0]
        if not role:
            bot.delete_message(msg2.chat.id,msg2.id)
            bot.delete_message(message.chat.id,message.id)
            bot.send_message(message.chat.id, f"角色 '{old_role_name}' 不存在。",reply_markup=markup)
            return

        existing_role = roles.find_one({'chat_id': chat_id, 'role_name': new_role_name})
        if existing_role:
            bot.send_message(message.chat.id, f"角色 '{new_role_name}' 已存在，请选择另一个名称。",reply_markup=markup)
            bot.delete_message(msg2.chat.id,msg2.id)
            bot.delete_message(message.chat.id,message.id)
            return
        data = roles.find({'chat_id':chat_id,'roles':old_role_name})
        if data:
            for da in data:
                roles.update_one({'chat_id': chat_id, 'roles': old_role_name}, {'$set': {'roles': new_role_name}})
        roles.update_one({'chat_id': chat_id, 'role_name': old_role_name}, {'$set': {'role_name': new_role_name}})
        bot.send_message(message.chat.id, f"角色 '{old_role_name}' 已成功更名为 '{new_role_name}'。",reply_markup=markup)
        bot.delete_message(msg2.chat.id,msg2.id)
        bot.delete_message(message.chat.id,message.id)
    except Exception as e:
        print(f"Error changing role name: {e}")
        bot.send_message(message.chat.id,"发生错误。请稍后再试。",reply_markup=markup)


def leaderboard_invite(chat_id,sec,from_user):
    seven_days_ago = datetime.now() - timedelta(seconds=sec)
    data = invites.find({'chat_id':chat_id,'timestamp': {'$gte': seven_days_ago}})
    bot.send_message(from_user,"这个过程可能需要几秒钟的时间来从数据库中收集数据。")
    users = {}
    i = 0
    for da in data:
        if 'users' in da:
            for (user_id,daa) in da['users'].items():
                user_timestamp = daa['timestamp']
                if user_timestamp and user_timestamp >= seven_days_ago:
                    i = i + 1
        if i == 0:
            continue
        first_name = da['first_name']
        user_id = da['user_id']
        username = da['username']
        users[user_id] = {'first_name':first_name,'invites':i,'username':username}
        i = 0
    sorted_participants = sorted(users.items(), key=lambda x: x[1]['invites'], reverse=True)
    msg_text = "请求的邀请排行榜如下：：\n\n"
    for (user_id,data) in sorted_participants:
        i = i + 1
        msg_text += f"{i}. @{data['username']} - {data['invites']} invites\n"
        if i >= 10:
            break
    if i == 0:
        bot.send_message(from_user,"未找到数据。")
        return
    bot.send_message(from_user ,msg_text , parse_mode='HTML')

def invite_time(message,chat_id):
    markup = types.ReplyKeyboardRemove()
    if message.text == "🚫Cancle":
        bot.send_message(message.chat.id,"Action Cancled 🚫",reply_markup=markup)
        return
    duration = message.text
    duration_units = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    try:
        duration = int(duration[:-1]) * duration_units[duration[-1]]
    except Exception:
        bot.send_message(message.from_user.id,"转换时间时出现错误，请再试一次，使用格式：1d，1h，1m，1s。")
        bot.register_next_step_handler(message,invite_time,chat_id)
        return
    leaderboard_invite(chat_id,duration,message.from_user.id)


def end_giveaway(giveaway_id):
    giveaway = giveaways.find_one({"giveaway_id": giveaway_id})
    if giveaway:
        chat_id = giveaway["chat_id"]
        if len(giveaway["participants"]) < int(giveaway["num_winners"]):
            message_text = "没有足够的参与者来选择获胜者。赠品活动已被取消。"
            giveaway_id2 = str(uuid.uuid4())
            giveaways.update_one({'giveaway_id':giveaway_id},{'$set': {'giveaway_id': giveaway_id2 ,'is_done':True}},upsert=True)
            bot.send_message(chat_id, message_text)
            return
        winners = []
        for i in range(int(giveaway["num_winners"])):
            winner = random.choice(giveaway["participants"])
            winners.append(winner)
            giveaway["participants"].remove(winner)
        message_text = f"价值 {giveaway['amount']} 的幸运抽奖已经结束。获奖者名单如下："
        giveaways.update_one({'giveaway_id':giveaway_id},{'$set': {'winners': winners }},upsert=True)
        for winner in winners:
            member = bot.get_chat_member(chat_id, winner)
            first_name = member.user.first_name
            message_text += f"\n🔹<a href='tg://user?id={member.user.id}'>{first_name}</a> - @{member.user.username}"
        bot.send_message(chat_id, message_text , parse_mode='HTML')

        giveaway_id2 = str(uuid.uuid4())
        giveaways.update_one({'giveaway_id':giveaway_id},{'$set': {'giveaway_id': giveaway_id2 ,'is_done':True}},upsert=True)


lock = threading.Lock()

def time_check():
    with lock:
        time.sleep(10)
        while True:
            i = 1
            giveawayes = giveaways.find()
            for giveaway in giveawayes:
                try:
                    if 'is_done' in giveaway:
                        continue
                    if 'duration' not in giveaway:
                        continue
                    giveaway["duration"] -= 10
                    i += 1
                    time_left = giveaway["duration"]
                    giveaway_id = giveaway['giveaway_id']
                    giveaways.update_one({'giveaway_id': giveaway_id}, {'$set': {'duration': giveaway["duration"]}}) 
                    if time_left <= 0:
                        end_giveaway(giveaway_id)
                    if 'is_edit' in giveaway and giveaway['is_edit'] is True:
                        chat_id = giveaway['chat_id']
                        msg_id = int(giveaway['message_id'])
                        num_win = len(giveaway['participants'])
                        message_text = f"加入的用户数量 - {num_win} "
                        if 'del_id' in giveaway:
                            bot.delete_message(chat_id,giveaway['del_id'])
                        msg = bot.send_message(chat_id,message_text,reply_to_message_id=msg_id)
                        giveaways.update_one({'giveaway_id':giveaway_id},{'$set':{'is_edit':False,'del_id':msg.id}},upsert=True)
                except Exception as e:
                    print("error in giveaway time check : " , e)
                    continue
            if i == 1:
                return False
            time.sleep(10)


time_thread = threading.Thread(target=time_check)
time_thread.start()


@bot.message_handler(commands=['quiz'])
def quiz_handler(message):
    create_quiz(message,message.from_user.id)

@bot.message_handler(commands=['quies'])
def starts_handler(message):
    if message.text == "/quies":
        return
    id = message.text.split(" ")[1]
    start_quiz(id,message.chat.id,message.id)


@bot.message_handler(commands=['quiz_all','quizall'])
def edit_quiz(message):
    user_id = message.from_user.id
    data = quizs.find({'user_id':user_id})
    if data:
        msg_txt = "Your all quizs\n\n"
        i = 1
        markup = InlineKeyboardMarkup()
        for dat in data:
            quiz_id = dat['quiz_id']
            title = dat['title']
            time_left = dat.get('time_limit',"Not Set")
            questions = dat.get('questions',{})
            button = InlineKeyboardButton(title,callback_data=f"edit_quiz:{quiz_id}")
            markup.add(button)
            msg_txt += f"{i}. {title}\n❓{len(questions)} questions ▪️ ⏱ {time_left} sec\n\n"
            i = i + 1
    bot.send_message(message.chat.id,msg_txt,reply_markup=markup)

@bot.message_handler(commands=['giveaway'])
def giveaway_handler(message):
    chat_id = message.chat.id
    chat_members = bot.get_chat_administrators(chat_id)
    user_id = message.from_user.id
    is_admin = any(member.user.id == user_id and member.status in ['creator', 'administrator'] for member in chat_members)

    if not is_admin:
        bot.reply_to(message, "您必须是管理员才能使用此命令。")
        return

    args = message.text.split()[1:]

    # Define a dictionary to map duration units to seconds
    duration_units = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    is_how_to = False
    if len(args) >= 3:
        try:
            amount, num_winners, duration = args[:3]
            role = None
            amount = amount.replace("_"," ")
            duration = int(duration[:-1]) * duration_units[duration[-1]]
            num_winners = int(num_winners)
        except (ValueError, KeyError, IndexError):
            bot.reply_to(message, "命令格式无效。用法：/giveaway <奖励金额> <货币> <获奖人数> <持续时间> <*邀请人数> <*描述>")
            return
    
    if len(args) == 4:
        role = args[3]
        data = roles.find_one({'chat_id':message.chat.id,'role_name':role})
        if data:
            if 'how_to_get' in data:
                is_how_to = True
                button12 = InlineKeyboardButton(f"如何获得 {role}", callback_data=f"giveaway_how_to:{role}:{chat_id}")
        else:
            bot.reply_to(message,f"{role} 在此聊天中不存在。")
            return
    # Generate a unique identifier for the giveaway
    giveaway_id = str(uuid.uuid4())

    # Store the giveaway data using the unique identifier
    document = {
        "giveaway_id": giveaway_id,
        "chat_id": chat_id,
        "amount": amount,
        "num_winners": num_winners,
        "duration": duration,
        "role": role,
        "participants": [],
        "last_refresh_time": time.time(),
        "winners":[],
        "message_id": message.message_id + 1,
        "is_edit":False
    }

    giveaways.insert_one(document)

    time_left = duration
    time_left_str = f"{time_left // 86400}d:{(time_left % 86400) // 3600}h:{(time_left % 3600) // 60}m:{time_left % 60}s"
    message_text = f"🎉 抽奖时间 🎉\n\n🎁 奖励 - {amount}\n\n🏆 获奖人数 - {num_winners}\n\n⏱ 剩余时间 - {time_left_str}"

    if role :
        message_text += f"\n\n要参加此幸运抽奖，您需要拥有 {role} 角色"

    url = f"https://t.me/Academy_lottery_assistant_bot?start={giveaway_id}"
    
    text = f"参加抽奖"
    leave_call = f"leave_giveaway:{giveaway_id}"
    refresh_text = f"刷新时间 ({time_left_str})"
    refresh_call = f"Refresh:{giveaway_id}"
    reply_markup = telebot.types.InlineKeyboardMarkup()
    reply_markup.add(telebot.types.InlineKeyboardButton(text,url=url))
    reply_markup.add(telebot.types.InlineKeyboardButton("退出抽奖", callback_data=leave_call))
    reply_markup.add(telebot.types.InlineKeyboardButton(refresh_text, callback_data=refresh_call))

    if is_how_to:
        reply_markup.add(button12)
    msg = bot.send_message(chat_id, message_text, reply_markup=reply_markup)
    bot.delete_message(message.chat.id, message.id)
    giveaways.update_one({'giveaway_id': giveaway_id},{'$set':{'message_id':msg.id}},upsert=True)
    time_thread = threading.Thread(target=time_check)
    time_thread.start()


@bot.inline_handler(lambda query: True)
def handle_inline_query(query):
    try:
        # Process the inline query and provide a list of results
        results = []
        user_id = query.from_user.id
        data = queries.find_one({'user_id': user_id})

        if query.query and data and 'results' in data:
            for result in data['results']:
                if query.query in result['title']:
                    results.append(
                        types.InlineQueryResultArticle(
                            id=result['id'],
                            title=result['title'],
                            input_message_content=types.InputTextMessageContent(
                                message_text=result['input_message_content']['message_text']
                            )
                        )
                    )

        bot.answer_inline_query(query.id, results)

    except Exception as e:
        print(f"Error processing inline query: {e}")
        pass
    


@bot.message_handler(func=lambda message: True)
def count_messages(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        messages.update_one({'user_id': user_id, 'chat_id': chat_id},
                            {'$inc': {'message_count': 1}},
                            upsert=True)
    except Exception:
        print("Error processing message count. ")

async def main():
    try:
        bot.polling()
    except Exception:
        print("Error in bot restarting bot again.")
        asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
