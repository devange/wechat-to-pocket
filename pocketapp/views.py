# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from pocketapp.models import Log, User, User2, Saveitem, Chat
from xml.etree import ElementTree as ET
import urllib, urllib2, httplib, cookielib, socket, hashlib, time, re, json

WECHAT_TOKEN = 'rulethebattlefield'
WECHAT_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'
WECHAT_APPID = 'wxff2b22e63886a792'
WECHAT_APPSECRET = '6ffc44556e96897d79efb66494e283da'
POCKET = {
	'consumer_key': '13263-bd933b638f056bc0ec5de525',
	'consumer_key_new': '17299-70dfe8151741c2d67b41ee3b',
	'redirect_uri': 'http://pocket.sinaapp.com/authorizationFinished',
	'get_token_uri': 'https://getpocket.com/v3/oauth/request',
	'request_token': '',
	'authorization_uri': 'https://getpocket.com/auth/authorize?request_token=%s&redirect_uri=%s',
	'access_token_uri': 'https://getpocket.com/v3/oauth/authorize',
	'signup_uri': 'http://getpocket.com/signup',
	'pic_authorization': 'http://pocket.sinaapp.com/statics/640.jpg', # 640x320
	'pic_signup': 'http://pocket.sinaapp.com/statics/80.png', # 80x80
	'add_uri': 'https://getpocket.com/v3/add',
	'get_uri': 'https://getpocket.com/v3/get'
}


def wechat(request):
	global WECHAT_TOKEN, POCKET
	params = request.GET
	mixedstr = ''.join(sorted((WECHAT_TOKEN, params.get('timestamp', ''), params.get('nonce', ''))))
	mixedstr = hashlib.sha1(mixedstr).hexdigest()
	if mixedstr == params.get('signature', ''):
		if params.has_key('echostr'):
			msg = params.get('echostr', '')
		else:
			reply = {
				'text': '''<xml>
						<ToUserName><![CDATA[%s]]></ToUserName>
						<FromUserName><![CDATA[%s]]></FromUserName>
						<CreateTime>%s</CreateTime>
						<MsgType><![CDATA[text]]></MsgType>
						<Content><![CDATA[%s]]></Content>
						<FuncFlag>0</FuncFlag>
					</xml>''',
				'music': '''<xml>
						<ToUserName><![CDATA[%s]]></ToUserName>
						<FromUserName><![CDATA[%s]]></FromUserName>
						<CreateTime>%s</CreateTime>
						<MsgType><![CDATA[music]]></MsgType>
						<Music>
							<Title><![CDATA[TITLE]]></Title>
							<Description><![CDATA[DESCRIPTION]]></Description>
							<MusicUrl><![CDATA[%s]]></MusicUrl>
							<HQMusicUrl><![CDATA[%s]]></HQMusicUrl>
						</Music>
						<FuncFlag>0</FuncFlag>
					</xml>''',
				'news': '''<xml>
						<ToUserName><![CDATA[%s]]></ToUserName>
						<FromUserName><![CDATA[%s]]></FromUserName>
						<CreateTime>%s</CreateTime>
						<MsgType><![CDATA[news]]></MsgType>
						<ArticleCount>%s</ArticleCount>
						<Articles>%s</Articles>
						<FuncFlag>1</FuncFlag>
					</xml>''',
				'item': '''<item>
						<Title><![CDATA[%s]]></Title> 
						<Description><![CDATA[%s]]></Description>
						<PicUrl><![CDATA[%s]]></PicUrl>
						<Url><![CDATA[%s]]></Url>
					</item>'''
			}
			if request.raw_post_data:
				xml = ET.fromstring(request.raw_post_data)
				xml_dict = {}
				for child in xml:  
					xml_dict[child.tag] = child.text
				msgid = xml_dict.get('MsgId', '')
				event = xml_dict.get('Event', '')
				msgtype = xml_dict.get('MsgType', '')
				content = xml_dict.get('Content', '')
				fromUserName = xml_dict.get('ToUserName', '')
				toUserName = xml_dict.get('FromUserName', '')
				title = xml_dict.get('Title', '')
				description = xml_dict.get('Description', '')
				url = xml_dict.get('Url', '')
				postTime = str(int(time.time()))
				uid = hashlib.sha1(toUserName).hexdigest()
				eventkey = xml_dict.get('EventKey', '')

				def reply_text(text):
					return reply['text'] % (toUserName, fromUserName, postTime, text)

				if event == 'subscribe' or content == 'Hello2BizUser':
					msg = reply_text('欢迎来到“我的Pocket”, 点击下方菜单或回复“a”绑定Pocket账号。由于国内访问Pocket速度较慢，如无回应请重新发送。\r\n回复“h”或“?”获取帮助。')
				elif content == 'a' or content == 'A' or content == 'auth' or eventkey == 'V1001_ACCOUNT_AUTH':
					# return HttpResponse(reply_text(get_request_token().replace('code=','')))
					authorization_uri = POCKET['authorization_uri'] % (get_request_token(uid, request), POCKET['redirect_uri'] + '?uid=' + uid)
					item = reply['item'] % ('点击绑定Pocket账号，如果你已有Pocket帐号，请进入后点击右上角的Login', '', POCKET['pic_authorization'], authorization_uri)
					# item += reply['item'] % ('如果你还没有Pocket账号，点击这里注册', '', POCKET['pic_signup'], POCKET['signup_uri'])
					msg = reply['news'] % (toUserName, fromUserName, postTime, '1', item)
				elif content == 'h' or content == 'H' or content == 'help' or content == '?' or content == '？' or eventkey == 'V1001_HELP':
					user_item = User.objects.order_by('id').filter(wechat_user=uid)
					user_item2 = User2.objects.order_by('id').filter(wechat_user=uid)
					if user_item.count() == 0 or user_item2.count() == 0:
						msg = reply_text('使用帮助：\r\n点击下方菜单或回复“a”绑定Pocket账号。由于国内访问Pocket速度较慢，如无回应请重新发送。\r\n\r\n有问题或者建议欢迎留言或者发送邮件到devange@live.com，感谢你的支持！')
					else:
						msg = reply_text('你授权的Pocket账号为：%s\r\n\r\n使用步骤：\r\n1、打开你需要保存的内容，可以是微信公众账号推送或者微信好友发来的文章或链接\r\n2、点击右上角的“...”或者“转发”按钮\r\n3、在弹出的窗口中点击“复制链接”\r\n4、返回消息列表，进入“我的Pocket”公众账号\r\n5、长按消息输入框粘贴链接发送给本账号\r\n6、保存成功！你可以稍后打开Pocket阅读了！\r\n\r\n使用帮助：\r\n- 如果发送后无响应，可能是国内访问Pocket速度比较慢，请重新发送。\r\n- 如果提示“保存失败”，请确认链接的有效性并重试。\r\n- 如果多次重试不行，有可能是账号授权过期，请回复“a”重新绑定Pocket账号。\r\n\r\n有问题或者建议欢迎留言或者发送邮件到devange@live.com，感谢你的支持！' % user_item2[user_item2.count() - 1].pocket_user.encode('utf-8'))
				elif eventkey == 'V1001_SAVED_RECENTLY_5' or eventkey == 'V1001_SAVED_RECENTLY_10':
					user_item = User.objects.order_by('id').filter(wechat_user=uid)
					user_item2 = User2.objects.order_by('id').filter(wechat_user=uid)
					if user_item.count() == 0 or user_item2.count() == 0:
						msg = reply_text('你还没有绑定Pocket账号。\r\n点击下方菜单或回复“a”绑定Pocket账号。由于国内访问Pocket速度较慢，如无回应请重新操作。')
					else:
						count = 5
						if eventkey == 'V1001_SAVED_RECENTLY_5':
							count = 5
						elif eventkey == 'V1001_SAVED_RECENTLY_10':
							count = 10
						access_token = user_item2[user_item2.count() - 1].access_token
						get_data = {
							'count': count,
							'sort': 'newest',
							'detailType': 'complete',
							'consumer_key': POCKET['consumer_key_new'],
							'access_token': access_token
						}
						# for i in range(0, 5):
						try:
							get_data = urllib.urlencode(get_data)
							get_req = urllib2.Request(POCKET['get_uri'], get_data)
							get_response = urllib2.urlopen(get_req, timeout=5)
							response = str(get_response.read())
							response_json = json.loads(response)
							if response_json['status'] == 1:
								if response_json['list']:
									dicts = response_json['list']
									dicts_sorted = sorted(dicts.iteritems(), key=lambda d:d[1]['time_updated'], reverse=True);
									item = ''
									for v in dicts_sorted:
										# msg = reply_text(v['images']['1']['src'])
										image = ''
										v = v[1]
										if v['has_image'] == '1':
											image = v['image']['src']
										item += reply['item'] % (v['resolved_title'], v['excerpt'], image, v['resolved_url'])
									msg = reply['news'] % (toUserName, fromUserName, postTime, str(len(dicts)), item)
								else:
									msg = reply_text('你似乎没有待读的内容。请善加使用：）')
							else:
								msg = reply_text('获取失败，请重试。')
							# break
						except:
							msg = reply_text('获取失败，请重试。如需获取帮助请点下方菜单。')
							response = 'timeout'
						# else:
						# 	msg = reply_text('获取失败，请重试。如需获取帮助请点下方菜单。%s', i)
						# 	response = 'timeout'
				else:
					user_item = User.objects.order_by('id').filter(wechat_user=uid)
					user_item2 = User2.objects.order_by('id').filter(wechat_user=uid)
					if user_item.count() == 0 or user_item2.count() == 0:
						msg = reply_text('点击下方菜单或回复“a”绑定Pocket账号。由于国内访问Pocket速度较慢，如无回应请重新发送。\r\n如需获取帮助请点下方菜单。')
						Chat(wechat_user = uid, pocket_user = '-', chat = content).save()
					else:
						if msgtype == 'link' or content[0:7] == 'http://' or content[0:8] == 'https://':
							if msgtype == 'link':
								url = url
								title = title
							else:
								url = content
								#title = fetchTitle(url)
								title = ''
							access_token = user_item2[user_item2.count() - 1].access_token
							pocket_user = user_item2[user_item2.count() - 1].pocket_user
							add_data = {
								'url': url,
								'title': title,
								'tags': 'wechat',
								'consumer_key': POCKET['consumer_key_new'],
								'access_token': access_token
							}
							try:
								add_req = urllib2.Request(POCKET['add_uri'], urllib.urlencode(add_data))
								add_response = urllib2.urlopen(add_req, timeout=5)
								response = str(add_response.read())
								response_json = json.loads(response)
								if response_json['item']['title'] is None:
									title = 'null'
								else:
									title = response_json['item']['title']
								if (response_json['status'] == 1):
									if title == 'null':
										msg = reply_text('保存成功')
									else:
										msg = reply_text('「%s」 保存成功' % (title.encode('utf-8')))
								else:
									msg = reply_text('保存失败，请重试。\r\n如需获取帮助请点下方菜单。')
								Saveitem(wechat_user = uid, pocket_user = pocket_user, title = title, url = url, status = response_json['status']).save()
							except:
								try:
									add_data = {
										'url': url,
										'title': title,
										'tags': 'wechat',
										'consumer_key': POCKET['consumer_key'],
										'access_token': access_token
									}
									add_req = urllib2.Request(POCKET['add_uri'], urllib.urlencode(add_data))
									add_response = urllib2.urlopen(add_req, timeout=5)
									response = str(add_response.read())
									response_json = json.loads(response)
									if response_json['item']['title'] is None:
										title = 'null'
									else:
										title = response_json['item']['title']
									if (response_json['status'] == 1):
										if title == 'null':
											msg = reply_text('保存成功')
										else:
											msg = reply_text('「%s」 保存成功' % (title.encode('utf-8')))
									else:
										msg = reply_text('保存失败，请重试。\r\n如需获取帮助请点下方菜单。')
									Saveitem(wechat_user = uid, pocket_user = pocket_user, title = title, url = url, status = response_json['status']).save()
								except:
									# msg = reply_text('保存失败或超时，请重试，请确认链接有效。如需获取帮助请点下方菜单。')
									response = 'timeout'
									Saveitem(wechat_user = uid, title = title, log = response, url = url, status = '-1').save()
						elif content[0:5] == 'menu:':
							wechat_access_token = getCredential()
							add_data = {
								"button": [
									{
										"name": "最近待读",
										"sub_button": [
											{
												"type": "click",
												"name": "最近10篇",
												"key": "V1001_SAVED_RECENTLY_10"
											},
											{
												"type": "click",
												"name": "最近5篇",
												"key": "V1001_SAVED_RECENTLY_5"
											}
										]
									},
									{
										"type": "click",
										"name": "使用帮助",
										"key": "V1001_HELP"
									},
									{
										"type": "click",
										"name": "账号绑定",
										"key": "V1001_ACCOUNT_AUTH"
									}
								]
							}
							url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s' % wechat_access_token
							http_header = {
								"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.46 Safari/535.11",
								"Accept" : "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,text/png,*/*;q=0.5",
								"Accept-Language" : "en-us,en;q=0.5",
								"Accept-Charset" : "ISO-8859-1",
								"Content-type": "application/x-www-form-urlencoded"
							}
							timeout = 15
							socket.setdefaulttimeout(timeout)
							cookie_jar = cookielib.LWPCookieJar()
							cookie = urllib2.HTTPCookieProcessor(cookie_jar)
							proxy = {}
							opener = urllib2.build_opener(cookie)
							add_req = urllib2.Request(url, json.dumps(add_data, ensure_ascii=False), http_header)
							response = str(opener.open(add_req).read())
							msg = reply_text(response)
						else:
							msg = reply_text('回复链接即可保存文章到Pocket，只支持链接哦。\r\n如需获取帮助请点下方菜单。')
							pocket_user = user_item2[user_item2.count() - 1].pocket_user
							Chat(wechat_user = uid, pocket_user = pocket_user, chat = content).save()

			else:
				msg = 'Invalid'

			return HttpResponse(msg)
	else:
		return render(request, 'index.html', {})

def test(request):
	txt = ''
	return str(txt)

def fetchTitle(url):
	try:
		fetch_req = urllib2.Request(url)
		fetch_response = urllib2.urlopen(fetch_req, timeout=5)
		re_title = re.compile(r"<title>(.*?)</title>",re.I)
		html = re.sub(r"\n+", "\n", str(fetch_response.read()))
		title = re_title.search(html).group(1)
	except:
		title = '~'
	return title

def get_request_token(uid, request):
	auth_data1 = {
		'consumer_key': POCKET['consumer_key_new'],
		'redirect_uri': POCKET['redirect_uri'] + '?uid=' + uid
	}
	auth_data1 = urllib.urlencode(auth_data1)
	auth_req1 = urllib2.Request(POCKET['get_token_uri'], auth_data1)
	auth_response1 = urllib2.urlopen(auth_req1)
	code = auth_response1.read().replace('code=', '')
	request.session["code"] = code
	User(wechat_user = uid, request_token = code).save()
	return code

def authorize(uid, code):
	auth_data2 = {
		'consumer_key': POCKET['consumer_key_new'],
		'code': code
	}
	auth_data2 = urllib.urlencode(auth_data2)
	auth_req2 = urllib2.Request(POCKET['access_token_uri'], auth_data2)
	try:
		auth_response2 = urllib2.urlopen(auth_req2)
		response = auth_response2.read()
	# except urllib2.HTTPError, e:
	# 	response = '!!! HTTPError = ' + str(e.code)
	# except urllib2.URLError, e:
	# 	response = '!!! URLError = ' + str(e.reason)
	# except httplib.HTTPException, e:
	# 	response = '!!! HTTPException'
	# except Exception:
	# 	import traceback
	# 	response = '!!! generic exception: ' + traceback.format_exc()
	except:
		response = 'error'
	return response

def authorizationFinished(request):
	uid = request.GET.get('uid', '~~~')
	user_item = User.objects.order_by('id').filter(wechat_user=uid)
	user_item2 = User2.objects.order_by('id').filter(wechat_user=uid)
	pocket_user = ''
	# if user_item2.count() == 0:
	if user_item.count() == 0:
		auth_result = 0
	else:
		code = user_item[user_item.count() - 1].request_token
		auth_response = authorize(uid, code)
		if auth_response == 'error':
			if user_item2.count() == 0:
				auth_result = 0
			else:
				auth_result = 2
		elif auth_response[0:3] == '!!!':
			auth_result = 3
		else:
			access_token = auth_response.split('&')[0].replace('access_token=', '')
			pocket_user = auth_response.split('&')[1].replace('username=', '')
			User2(wechat_user = uid, pocket_user = pocket_user, access_token = access_token).save()
			pocket_user = '<em>%s</em>，' % (pocket_user)
			auth_result = 1

	if auth_result == 0:
		title = '绑定失败'
		msg = '账号绑定失败，请返回微信点击下方菜单“帐号绑定”或回复“a”重试。<script>window.location.reload()</script>'
	elif auth_result == 1:
		title = '绑定成功'
		msg = pocket_user + '账号绑定成功。<br>返回微信给我发送链接即可保存到Pocket以便稍后阅读。'
	elif auth_result == 2:
		title = '账号已绑定'
		msg = '你已经绑定过Pocket账号<br>返回微信给我发送链接即可保存到Pocket以便稍后阅读。如有问题请尝试重新绑定帐号。<script>window.location.reload()</script>'
	elif auth_result == 3:
		title = '出现错误'
		msg = auth_response

	return render(request, 'authorize.html', {'title': title, 'result': msg})

def getCredential():
	auth_data2 = {
		'grant_type': 'client_credential',
		'appid': WECHAT_APPID,
		'secret': WECHAT_APPSECRET
	}
	auth_data2 = urllib.urlencode(auth_data2)
	auth_req2 = urllib2.Request(WECHAT_TOKEN_URL, auth_data2)
	try:
		auth_response2 = urllib2.urlopen(auth_req2)
		response = json.loads(auth_response2.read())
	except:
		response = { 'access_token': 'error' }
	return response['access_token']


