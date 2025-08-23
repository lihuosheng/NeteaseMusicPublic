import argparse
import os
from flask import Flask, request, render_template, redirect, jsonify
from music_api import url_v1, name_v1, lyric_v1, artist_top, search_info, playlist_detail, album_detail
from cookie_manager import CookieManager

# ================= 工具函数 =================
cm = CookieManager()

def ids(ids: str) -> str:
    if '163cn.tv' in ids:
        import requests
        response = requests.get(ids, allow_redirects=False)
        ids = response.headers.get('Location')
    if 'music.163.com' in ids:
        index = ids.find('id=') + 3
        ids = ids[index:].split('&')[0]
    return ids

def size(value: float) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size
    return str(value)

def music_level1(value: str) -> str:
    levels = {
        'standard': "标准音质",
        'exhigh': "极高音质",
        'lossless': "无损音质",
        'hires': "Hires音质",
        'sky': "沉浸环绕声",
        'jyeffect': "高清环绕声",
        'jymaster': "超清母带"
    }
    return levels.get(value, "未知音质")

# ================= Flask 应用 =================
app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/Song_V1', methods=['GET', 'POST'])
def Song_v1():
    # 参数获取
    if request.method == 'GET':
        song_ids = request.args.get('ids')
        url = request.args.get('url')
        level = request.args.get('level')
        type_ = request.args.get('type')
    else:
        song_ids = request.form.get('ids')
        url = request.form.get('url')
        level = request.form.get('level')
        type_ = request.form.get('type')

    # 参数校验
    if not song_ids and not url:
        return jsonify({'error': '必须提供 ids 或 url 参数'}), 400
    if not level:
        return jsonify({'error': 'level参数为空'}), 400
    if not type_:
        return jsonify({'error': 'type参数为空'}), 400

    jsondata = song_ids if song_ids else url
    cookies = cm.parse_cookie(cm.read_cookie())
    try:
        song_id = ids(jsondata)
        urlv1 = url_v1(song_id, level, cookies)
        if not urlv1['data'] or urlv1['data'][0]['url'] is None:
            return jsonify({"code": 400, 'msg': '信息获取不完整！'}), 400
        namev1 = name_v1(urlv1['data'][0]['id'])
        lyricv1 = lyric_v1(urlv1['data'][0]['id'], cookies)
        song_data = urlv1['data'][0]
        song_info = namev1['songs'][0] if namev1['songs'] else {}
        song_url = song_data['url']
        song_name = song_info.get('name', '')
        song_picUrl = song_info.get('al', {}).get('picUrl', '')
        song_alname = song_info.get('al', {}).get('name', '')
        song_alid = song_info.get('al', {}).get('id', '')
        # 歌手名拼接
        song_arname = '/'.join(artist['name'] for artist in song_info['ar'])
        song_arid = ', '.join(str(artist['id']) for artist in song_info['ar'])
        # 歌词
        lrc = lyricv1.get('lrc', {}).get('lyric', '')
        tlyric = lyricv1.get('tlyric', {}).get('lyric', '')
        romalrc = lyricv1.get('romalrc', {}).get('lyric', '')
        klyric = lyricv1.get('klyric', {}).get('lyric', '')
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'服务异常: {str(e)}'}), 500

    # 响应类型
    if type_ == 'text':
        data = f'歌曲名称：{song_name}<br>歌曲图片：{song_picUrl}<br>歌手：{song_arname}<br>歌曲专辑：{song_alname}<br>歌曲音质：{music_level1(song_data["level"])}<br>歌曲大小：{size(song_data["size"])}<br>音乐地址：{song_url}'
    elif type_ == 'down':
        data = redirect(song_url)
    elif type_ == 'json':
        data = {
            "code": 200,
            "name": song_name,
            "pic": song_picUrl,
            "ar_name": song_arname,
            "ar_id": song_arid,
            "al_name": song_alname,
            "al_id": song_alid,
            "level": music_level1(song_data["level"]),
            "size": size(song_data["size"]),
            "url": song_url.replace("http://", "https://", 1),
            "lrc": lrc,
            "tlyric": tlyric,
            "romalrc": romalrc,
            "klyric": klyric
        }
        data = jsonify(data)
    else:
        data = jsonify({"code": 400, 'msg': '解析失败！请检查参数是否完整！'}), 400
    return data
    
@app.route('/Artist', methods=['GET', 'POST'])
def artist():
    if request.method == 'GET':
        artist_id = request.args.get('id')
    else:
        artist_id = request.form.get('id')

    # 参数校验
    if not artist_id:
        return jsonify({'error': '必须提供 id 或 url 参数'}), 400
    cookies = cm.parse_cookie(cm.read_cookie())
    
    try:
        artist_id = ids(artist_id)
        info = artist_top(artist_id, cookies)
        return jsonify(info)
    except Exception as e:
        return jsonify({"code": 400, 'msg': '解析失败！请检查参数是否完整！'}), 400

@app.route('/Search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        keywords = request.args.get('s')
        search_type = request.args.get('type', default=1, type=int)
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
    else:
        keywords = request.form.get('s')
        search_type = int(request.form.get('type', 1))
        limit = int(request.form.get('limit', 20))
        offset = int(request.form.get('offset', 0))
    if not keywords:
        return jsonify({'error': '必须提供 keywords 参数'}), 400
    cookies = cm.parse_cookie(cm.read_cookie())
    try:
        info = search_info(cookies, keywords, search_type, limit, offset)
        return jsonify(info)
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'搜索异常: {str(e)}'}), 500

@app.route('/Playlist', methods=['GET', 'POST'])
def playlist():
    if request.method == 'GET':
        playlist_id = request.args.get('id')
    else:
        playlist_id = request.form.get('id')
    if not playlist_id:
        return jsonify({'error': '必须提供歌单id参数'}), 400
    cookies = cm.parse_cookie(cm.read_cookie())
    try:
        playlist_id = ids(playlist_id)
        info = playlist_detail(playlist_id, cookies)
        return jsonify({'code': 200, 'playlist': info})
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'歌单解析异常: {str(e)}'}), 500

@app.route('/Album', methods=['GET', 'POST'])
def album():
    if request.method == 'GET':
        album_id = request.args.get('id')
    else:
        album_id = request.form.get('id')
    if not album_id:
        return jsonify({'error': '必须提供专辑id参数'}), 400
    cookies = cm.parse_cookie(cm.read_cookie())
    try:
        album_id = ids(album_id)
        info = album_detail(album_id, cookies)
        return jsonify({'code': 200, 'album': info})
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'专辑解析异常: {str(e)}'}), 500

# ================= 命令行启动 =================
def start_gui(url: str = None, level: str = 'lossless'):
    if url:
        print(f"正在处理 URL: {url}，音质：{level}")
        cookies = cm.parse_cookie(cm.read_cookie())
        try:
            song_ids = ids(url)
            urlv1 = url_v1(song_ids, level, cookies)
            namev1 = name_v1(urlv1['data'][0]['id'])
            lyricv1 = lyric_v1(urlv1['data'][0]['id'], cookies)
            song_info = namev1['songs'][0]
            song_name = song_info['name']
            song_pic = song_info['al']['picUrl']
            artist_names = ', '.join(artist['name'] for artist in song_info['ar'])
            album_name = song_info['al']['name']
            album_id = song_info['al']['id']
            music_quality = music_level1(urlv1['data'][0]['level'])
            file_size = size(urlv1['data'][0]['size'])
            music_url = urlv1['data'][0]['url']
            lrc = lyricv1.get('lrc', {}).get('lyric', '')
            tlyric = lyricv1.get('tlyric', {}).get('lyric', '')
            romalrc = lyricv1.get('romalrc', {}).get('lyric', '')
            klyric = lyricv1.get('klyric', {}).get('lyric', '')
            output_text = f"""
            歌曲名称: {song_name}
            歌曲图片: {song_pic}
            歌手: {artist_names}
            专辑名称: {album_name}
            专辑 id: {album_id}
            音质: {music_quality}
            大小: {file_size}
            音乐链接: {music_url}
            歌词: {lrc}
            翻译歌词: {tlyric}
            罗马音歌词: {romalrc}
            滚动歌词: {klyric}
            """
            print(output_text)
            print(f"urlv1: {urlv1}\nnamev1: {namev1}")
        except Exception as e:
            print(f"发生错误: {e}")
    else:
        print("没有提供 URL 参数")

def start_api():
    # 开发模式下启动 Flask 内置服务器
    app.run(host='0.0.0.0', port=5000, debug=True)

# ================= 入口 =================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="启动 API 或 GUI")
    parser.add_argument('--mode', choices=['api', 'gui'], help="选择启动模式：api 或 gui")
    parser.add_argument('--url', help="提供 URL 参数供 GUI 模式使用")
    parser.add_argument('--level', default='lossless',
                        choices=['standard', 'exhigh', 'lossless', 'hires', 'sky', 'jyeffect', 'jymaster'],
                        help="选择音质等级，默认是 lossless")
    args = parser.parse_args()

    if args.mode == 'api':
        start_api()
    elif args.mode == 'gui':
        start_gui(args.url, args.level)
