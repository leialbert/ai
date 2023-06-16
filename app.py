from flask import Flask, request, jsonify,make_response
import hashlib
import openai
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

@app.route('/weixin', methods=['GET','POST'])
def wechat():
    if request.method == 'GET':
        token = os.getenv('WECHAT_TOKEN')
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')

        if check_signature(token, signature, timestamp, nonce):
            return make_response(echostr)
    elif request.method == 'POST':
        xml_data = request.get_data()
        xml_tree = ET.fromstring(xml_data)
        msg_type = xml_tree.find('MsgType').text
        if msg_type == 'text':
            content = xml_tree.find('Content').text
            user_openid = xml_tree.find('FromUserName').text
            public_openid = xml_tree.find('ToUserName').text
            if content == '你好':
                reply = '你好呀'
            else:
                reply_content = chat_gpt_response(content)
                reply = ET.Element('xml')
                to_user_name = ET.SubElement(reply, 'ToUserName')
                to_user_name.text = user_openid
                from_user_name = ET.SubElement(reply, 'FromUserName')
                from_user_name.text = public_openid
                create_time = ET.SubElement(reply, 'CreateTime')
                create_time.text = str(int(time.time()))
                msg_type = ET.SubElement(reply, 'MsgType')
                msg_type.text = 'text'
                content = ET.SubElement(reply, 'Content')
                content.text = reply_content
                response_xml = ET.tostring(reply, encoding='utf-8')
                response = make_response(response_xml)
                response.content_type = 'application/xml'
                return response
def check_signature(token, signature, timestamp, nonce):
    try:
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
        if tmp_str == signature:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
def chat_gpt_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        n=1,
        stop=None,
    )
    return response.choices[0].text.strip()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8022)
