import telebot
import uuid
from pymongo import MongoClient
import time
from telebot import types
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton
import threading
from pyrogram import Client 
import random
import asyncio
bot = telebot.TeleBot("6074378866:AAFTSXBqm0zYC2YFgIkbH8br5JeBOMjW3hg")

API_ID = '13537456'

API_HASH = '3f6b781f6a730e8f76e7cb1f863727c5'

bot2 = Client("my_eszsvxxt", api_id=API_ID, api_hash=API_HASH,bot_token="6074378866:AAFTSXBqm0zYC2YFgIkbH8br5JeBOMjW3hg")

password = 'VeJ7EH5TK13U4IQg'
cluster_url = 'mongodb+srv://bnslboy:' + \
    password + '@cluster0.avbmi1g.mongodb.net/'

# Create a MongoDB client
client = MongoClient(cluster_url)

# Access the desired database
db = client['main']

giveaways = db['giveaways']

invites = db['invites']

roles = db['roles']

owners = db['admins']

queries = db['query']

messages = db['messages']

app = "not_set"



def add_inline_markup(chat_id):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="📜Roles" , callback_data=f"roles:{chat_id}")
    button2 = InlineKeyboardButton(text="🎉Giveaways",callback_data=f"giveaways:{chat_id}")
    button3 = InlineKeyboardButton(text="👥Invite",callback_data=f"invite:{chat_id}")
    markup.add(button1)
    markup.add(button2)
    markup.add(button3)
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
        # if user_id in blacklist:
        #     bot.answer_callback_query(call.id, "You are blacklisted and cannot join this giveaway.",show_alert=True)
        #     return
        try:
            bot.get_chat_member(chat_id,user_id)
        except Exception as e:
            bot.answer_callback_query(call.id, "您必须是该群组的成员才能参加赠品活动。",show_alert=True)
            return
        if call.data.startswith(("join_giveaway:")):
            giveaway_id = call.data.split(":")[1]
            user_id = call.from_user.id
            if user_id in giveaway["participants"]:
                bot.answer_callback_query(call.id, "您已经参加过了此赠品活动。",show_alert=True)
                return
            current_time = time.time()
            giveaway["last_refresh_time"] = current_time
            giveaways.update_one({"giveaway_id": giveaway_id}, {"$set": {"last_refresh_time": giveaway["last_refresh_time"]}})
            giveaway["participants"].append(user_id)
            giveaways.update_one({"giveaway_id": giveaway_id}, {"$set": {"participants": giveaway["participants"]}})
            time_left = giveaway["duration"]
            num_participants = len(giveaway["participants"])
            join_text = f"参加抽奖 [{num_participants}]"
            join_call = f"join_giveaway:{giveaway_id}"
            leave_call = f"leave_giveaway:{giveaway_id}"
            refresh_test = f"刷新时间 ({time_left//86400}d:{time_left%86400//3600}h:{time_left%3600//60}m:{time_left%60}s)"
            refresh_call = f"Refresh:{giveaway_id}"
            reply_markup = telebot.types.InlineKeyboardMarkup()
            reply_markup.add(telebot.types.InlineKeyboardButton(join_text, callback_data=join_call))
            reply_markup.add(telebot.types.InlineKeyboardButton("退出抽奖", callback_data=leave_call))
            reply_markup.add(telebot.types.InlineKeyboardButton(refresh_test, callback_data=refresh_call))
            if is_how_to:
                reply_markup.add(button12)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=reply_markup)
            bot.answer_callback_query(call.id, "您已成功参加了赠品活动。",show_alert=True)
        elif call.data.startswith(("leave_giveaway:")):
            giveaway_id = call.data.split(":")[1]
            if user_id not in giveaway["participants"]:
                bot.answer_callback_query(call.id, "您尚未参加此赠品活动。",show_alert=True)
                return
            current_time = time.time()
            giveaway["last_refresh_time"] = current_time
            giveaways.update_one({"giveaway_id": giveaway_id}, {"$set": {"last_refresh_time": giveaway["last_refresh_time"]}})
            giveaway["participants"].remove(user_id)
            giveaways.update_one({"giveaway_id": giveaway_id}, {"$set": {"participants": giveaway["participants"]}})
            num_participants = len(giveaway["participants"])
            time_left = giveaway["duration"]
            join_text = f"参加抽奖 [{num_participants}]"
            join_call = f"join_giveaway:{giveaway_id}"
            leave_call = f"leave_giveaway:{giveaway_id}"
            refresh_test = f"刷新时间 ({time_left//86400}d:{time_left%86400//3600}h:{time_left%3600//60}m:{time_left%60}s)"
            refresh_call = f"Refresh:{giveaway_id}"
            reply_markup = telebot.types.InlineKeyboardMarkup()
            reply_markup.add(telebot.types.InlineKeyboardButton(join_text, callback_data=join_call))
            reply_markup.add(telebot.types.InlineKeyboardButton("退出抽奖", callback_data=leave_call))
            reply_markup.add(telebot.types.InlineKeyboardButton(refresh_test, callback_data=refresh_call))
            if is_how_to:
                reply_markup.add(button12)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=reply_markup)
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
            num_participants = len(giveaway["participants"])
            join_text = f"参加抽奖 [{num_participants}]"
            join_call = f"join_giveaway:{giveaway_id}"
            leave_call = f"leave_giveaway:{giveaway_id}"
            refresh_test = f"刷新时间 ({time_left//86400}d:{time_left%86400//3600}h:{time_left%3600//60}m:{time_left%60}s)"
            refresh_call = f"Refresh:{giveaway_id}"
            reply_markup = telebot.types.InlineKeyboardMarkup()
            reply_markup.add(telebot.types.InlineKeyboardButton(join_text, callback_data=join_call))
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
        bot.answer_callback_query(call.id,"working on it")
         
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
    num_winners = message.text
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

def role_giver(chat_id , user_id):
    data = roles.find({"chat_id":chat_id})
    is_give_role = False
    for da in data:
        if 'role_name' in da:
            role_name = da['role_name']
            if 'is_auto_invite' in da and da['is_auto_invite'] == True:
                
                count = da['invite_count']
                da2 = invites.find_one({'chat_id':chat_id,'user_id':user_id})
                if da2:
                    invite_count = da2['regular_count']
                    if invite_count >= count :
                        is_give_role = True
                    else:
                        is_give_role = False
                else:
                    is_give_role = False
            if 'is_auto_message' in da and da['is_auto_message'] == True:
                count = da['message_count']
                da2 = messages.find_one({'chat_id':chat_id,'user_id':user_id})
                if da2:
                    messages_count = da2['msg_count']
                    if messages_count >= count:
                        is_give_role = True
                    else:
                        is_give_role = False
                else:
                    is_give_role = False
            if is_give_role == True:
                data = roles.find_one({'chat_id': chat_id, 'user_id': user_id,'roles': role_name})
                if data:
                    return
                try:
                    bot2.start()
                    usser = bot2.get_users(user_id)
                    usser_name = usser.username
                    roles.update_one({'chat_id': chat_id, 'user_id': user_id}, {'$addToSet': {'roles': role_name},'$set': {'first_name': usser_name}}, upsert=True)
                    roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':1}},upsert=True)
                    is_give_role = False
                    bot2.stop()
                except Exception:
                    pass

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

def time_check(giveaway_id):
        time.sleep(10)
        while True:
            giveaway = giveaways.find_one({'giveaway_id':giveaway_id})
            giveaway["duration"] -= 10
            time_left = giveaway["duration"]
            giveaways.update_one({'giveaway_id': giveaway_id}, {'$set': {'duration': giveaway["duration"]}}) 
            if time_left <= 0:
                end_giveaway(giveaway_id)
                return False
            time.sleep(10)

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
    try:
        amount, num_winners, duration = args[:3]
        role = None
        amount = amount.replace("_"," ")
        duration = int(duration[:-1]) * duration_units[duration[-1]]
    except (ValueError, KeyError, IndexError):
        bot.reply_to(message, "命令格式无效。用法：/giveaway <奖励金额> <货币> <获奖人数> <持续时间> <*邀请人数> <*描述>")
    
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
        "message_id": message.message_id + 1
    }

    giveaways.insert_one(document)

    time_left = duration
    time_left_str = f"{time_left // 86400}d:{(time_left % 86400) // 3600}h:{(time_left % 3600) // 60}m:{time_left % 60}s"
    message_text = f"🎉 抽奖时间 🎉\n\n🎁 奖励 - {amount}\n\n🏆 获奖人数 - {num_winners}\n\n⏱ 剩余时间 - {time_left_str}"

    if role :
        message_text += f"\n\n要参加此幸运抽奖，您需要拥有 {role} 角色"

    # Add the unique identifier as a callback data to the inline keyboard button
    text = f"参加抽奖 [0]"
    join_call = f"join_giveaway:{giveaway_id}"
    reply_markup = telebot.types.InlineKeyboardMarkup()
    reply_markup.add(telebot.types.InlineKeyboardButton(text, callback_data=join_call))
    if is_how_to:
        reply_markup.add(button12)
    bot.send_message(chat_id, message_text, reply_markup=reply_markup)
    bot.delete_message(message.chat.id, message.id)
    time_thread = threading.Thread(target=time_check,args=(giveaway_id,))
    time_thread.start()


@bot.inline_handler(lambda query: True)
def handle_inline_query(query):
    # Process the inline query and provide a list of results
    results = []
    user_id = query.from_user.id
    data = queries.find_one({'user_id': user_id})
    if query.query:
        if data and 'results' in data:
            for result in data['results']:
                if query.query in result['title']:
                    results.append(
                        telebot.types.InlineQueryResultArticle(
                            id=result['id'],
                            title= result['title'],
                            input_message_content=telebot.types.InputTextMessageContent(
                                message_text=result['input_message_content']['message_text']
                            )
                        )
                    )
    
    bot.answer_inline_query(query.id, results)


@bot.message_handler(func=lambda message: True)
def count_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Increment the message count for the user in the chat
    messages.update_one({'user_id': user_id, 'chat_id': chat_id},
                          {'$inc': {'message_count': 1}},
                          upsert=True)

async def main():
    # Start the Pyrogram client
    # Start the telebot polling (within the same event loop)
    bot.polling()

if __name__ == "__main__":
    # Run the main function within the asyncio event loop
    asyncio.run(main())
