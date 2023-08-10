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

bot = telebot.TeleBot("6074378866:AAFTSXBqm0zYC2YFgIkbH8br5JeBOMjW3hg")

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

dices = db['dices']

app = "not_set"



def add_inline_markup(chat_id):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="📜Roles" , callback_data=f"roles:{chat_id}")
    button2 = InlineKeyboardButton(text="🎉Giveaways",callback_data=f"giveaways:{chat_id}")
    button3 = InlineKeyboardButton(text="👥Invite",callback_data=f"invite:{chat_id}")
    button4 = InlineKeyboardButton(text="🎰 Dice Giveaway",callback_data=f"dice_giveaway:{chat_id}")
    markup.add(button1,button3)
    markup.add(button2,button4)
    return markup


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
        bot_member = bot.get_chat_member(chat_id, 5967390922)
        if bot_member.can_invite_users is False:
            bot.answer_callback_query(call.id,"❌ Insufficient permissions for the robot, please grant at least the following admin permissions:\n- Invite members via link",show_alert=True)
            return

        msg_text = "<b>Invitation Management </b>\n<i>Members in the group use the /link to automatically generate links.\nMember can use /invites to check their invites .\nMember can use /topinvites to check top 10 of group</i>\n\n<b>Statistics</b>\n"
        data = owners.find_one({'chat_id':chat_id})
        add_count = data.get('add_count',0)
        invite_count = data.get('invite_count',0)
        num_count = data.get('user_count',0)
        
        if 'link_count' in data:
            link_count = data['user_count']
        else:
            link_count = 0
        msg_text += f"<i>Total number of invitations = {num_count} ({add_count} by add button , {invite_count} by invite link) </i>\n"
        msg_text += f"<i>Total number of links generated =</i> {link_count}\n\n"
        
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
            bot.answer_callback_query(call.id,text="When someone join via invite link \nBot send message be like -:\n\nPerson1 invites Person2",show_alert=True)
        markup = add_inline_invite(chat_id,txt,y)
        try:
            bot.edit_message_reply_markup(call.message.chat.id,call.message.id,reply_markup=markup)
        except Exception:
            pass
    elif call.data.startswith(("invite_roles:")):
        chat_id = int(call.data.split(":")[1])
        data = roles.find({'chat_id': chat_id, 'role_name': {'$exists': True}})
        msg_txt = "Active roles || Invite count To Get\n\n"
        i = 1
        for da in data:
            if 'is_auto_invite' in da and da['is_auto_invite'] is True:
                count = da['invite_count']
                role_name = da['role_name']
                msg_txt += f"{i}. {role_name} -- {count}"
                i = i + 1
        if i == 1:
            bot.answer_callback_query(call.id,"No role found which will auto given when user invites user.",show_alert=True)
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
        bot.send_message(call.from_user.id,"Send me the time in the format of 1d,1h,1m,1s",reply_markup=markup)
        bot.register_next_step_handler(call.message,invite_time,chat_id)
    elif call.data.startswith(("export_invite:")):
        bot.answer_callback_query(call.id,"Working on it")
    elif call.data.startswith(("erase_invite:")):
        chat_id = int(call.data.split(":")[1])
        msg_text = """🚨🚨 Please note that all invitation links and invitation data will be cleared soon, the operation cannot be recovered, whether to continue:"""
        markup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton("Confim Delete All Invitation Data",callback_data=f"erase_invite1:{chat_id}")
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
        bot.send_message(call.from_user.id,"All Invitation Data Deleted Sucessfully")

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


def leaderboard_invite(chat_id,sec,from_user):
    seven_days_ago = datetime.now() - timedelta(seconds=sec)
    data = invites.find({'chat_id':chat_id,'timestamp': {'$gte': seven_days_ago}})
    bot.send_message(from_user,"This Process may takes few seconds in collecting data from database")
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
    msg_text = "Requested invite leaderboad --:\n\n"
    for (user_id,data) in sorted_participants:
        i = i + 1
        msg_text += f"{i}. @{data['username']} - {data['invites']} invites\n"
        if i >= 10:
            break
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
        bot.send_message(message.from_user.id,"Error occur when convering time\ntry again use format: 1d,1h,1m,1s")
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
                if 'is_done' in giveaway:
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
                    msg_id = giveaway['message_id']
                    num_win = len(giveaway['participants'])
                    message_text = f"加入的用户数量 - {num_win} "
                    if 'del_id' in giveaway:
                        bot.delete_message(chat_id,giveaway['del_id'])
                    msg = bot.send_message(chat_id,message_text,reply_to_message_id=msg_id)
                    giveaways.update_one({'giveaway_id':giveaway_id},{'$set':{'is_edit':False,'del_id':msg.id}},upsert=True)
            if i == 1:
                return False
            time.sleep(10)


time_thread = threading.Thread(target=time_check)
time_thread.start()


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
        # Log the error for debugging purposes (you can use your preferred logging mechanism)
        print(f"Error processing inline query: {e}")
        pass
    


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
