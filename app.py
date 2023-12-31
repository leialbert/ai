# from flask import Flask, request, jsonify,make_response
# import hashlib
# import openai
# from xml.etree import ElementTree
# from xml.etree.ElementTree import Element,tostring
# import os,time
# from dotenv import load_dotenv
# load_dotenv()

# openai.api_key = os.getenv('OPENAI_API_KEY')

# app = Flask(__name__)

# @app.route('/weixin', methods=['GET','POST'])
# def wechat():
#     if request.method == 'GET':
#         token = os.getenv('WECHAT_TOKEN')
#         signature = request.args.get('signature')
#         timestamp = request.args.get('timestamp')
#         nonce = request.args.get('nonce')
#         echostr = request.args.get('echostr')

#         if check_signature(token, signature, timestamp, nonce):
#             return make_response(echostr)
#     elif request.method == 'POST':
#         xml_data = request.data
#         xml_tree = ElementTree.fromstring(xml_data)
#         msg_type = xml_tree.find('MsgType').text
#         if msg_type == 'text':
#             content = xml_tree.find('Content').text
#             user_open_id = xml_tree.find('FromUserName').text
#             public_account_id = xml_tree.find('ToUserName').text
#             reply_content = chat_gpt_response(content)
#             reply = Element('xml')
#             to_user_name = Element('ToUserName')
#             to_user_name.text = user_open_id
#             reply.append(to_user_name)
#             from_user_name = Element('FromUserName')
#             from_user_name.text = public_account_id
#             reply.append(from_user_name)

#             create_time = Element('CreateTime')
#             create_time.text = str(int(time.time()))
#             reply.append(create_time)

#             msg_type = Element('MsgType')
#             msg_type.text = 'text'
#             reply.append(msg_type)

#             content=Element('Content')
#             content.text = reply_content
#             reply.append(content)

#             response_xml = ElementTree.tostring(reply, encoding='utf-8')
#             response = make_response(response_xml)
#             response.content_type = 'application/xml'
#             return response
#     else:
#         return 'error'
# def check_signature(token, signature, timestamp, nonce):
#     try:
#         tmp_list = [token, timestamp, nonce]
#         tmp_list.sort()
#         tmp_str = ''.join(tmp_list)
#         tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
#         if tmp_str == signature:
#             return True
#         else:
#             return False
#     except Exception as e:
#         print(e)
#         return False

# def chat_gpt_response(prompt):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo", 
#         messages=[
#             {"role": "user", "content": prompt},
#         ],
#         max_tokens=200,
#     )
#     return response['choices'][0]['message']['content'].strip()


# if __name__ == '__main__':
#     app.run(host='0.0.0.0',port=8022)
from flask import Flask, request, make_response
import hashlib
import openai
import os
import time
from xml.etree import ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
app = Flask(__name__)

def create_element(parent, tag, text):
    el = ET.Element(tag)
    el.text = text
    parent.append(el)

@app.route('/weixin', methods=['GET','POST'])
def wechat():
    if request.method == 'GET':
        if check_signature(os.getenv('WECHAT_TOKEN'), request.args.get('signature'), request.args.get('timestamp'), request.args.get('nonce')):
            return make_response(request.args.get('echostr'))

    elif request.method == 'POST':
        xml_tree = ET.fromstring(request.data)
        if xml_tree.find('MsgType').text == 'text':
            user_open_id = xml_tree.find('FromUserName').text
            public_account_id = xml_tree.find('ToUserName').text
            reply_content = chat_gpt_response(xml_tree.find('Content').text)

            reply = ET.Element('xml')
            create_element(reply, 'ToUserName', user_open_id)
            create_element(reply, 'FromUserName', public_account_id)
            create_element(reply, 'CreateTime', str(int(time.time())))
            create_element(reply, 'MsgType', 'text')
            create_element(reply, 'Content', reply_content)

            response_xml = ET.tostring(reply, encoding='utf-8')
            response = make_response(response_xml)
            response.content_type = 'application/xml'
            return response
    return 'error'

def check_signature(token, signature, timestamp, nonce):
    try:
        tmp_list = sorted([token, timestamp, nonce])
        tmp_str = hashlib.sha1(''.join(tmp_list).encode('utf-8')).hexdigest()
        return tmp_str == signature
    except Exception as e:
        print(e)
        return False

def chat_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    return response['choices'][0]['message']['content'].strip()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8022)
