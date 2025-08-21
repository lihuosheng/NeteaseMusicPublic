# 网易云无损音乐解析

> **声明**  
> 本项目为开源软件，遵循 MIT 许可证。任何个人或组织均可自由使用、修改和分发本项目的源代码。但本项目及其任何衍生作品**禁止用于任何商业或付费项目**。如有违反，将视为对本项目许可证的侵犯。欢迎大家在遵守开源精神和许可证的前提下积极贡献和分享代码。

---

## 功能简介

- 本项目可解析网易云音乐无损音质下载链接，支持多种音质选择，支持 API 与命令行（GUI）两种模式。

- 能通过 Vercel 部署。

---

## 快速开始

### 1. 安装依赖

#### 开发模式

```bash
pip install -r requirements.txt
```

#### 生产模式

```bash
pip install -r requirements-dev.txt
```

### 2. 配置 Cookie

#### 文件 `cookie.txt` 

请在 `cookie.txt` 文件中填入黑胶会员账号的 Cookie，格式如下：

```bash
MUSIC_U=你的MUSIC_U值;os=pc;appver=8.9.70;
```

> 具体值请参考 `cookie.txt` 示例，替换为你自己的即可。

#### Vercel 中通过环境变量部署 Cookie

可以删除代码库中的 `cookie.txt` 文件

```bash
Key: COOKIES_TXT
Value: MUSIC_U=你的MUSIC_U值;os=pc;appver=8.9.70;
```

### 3. 运行

#### GUI 模式

```bash
python main.py --mode gui --url <网易云音乐地址> --level <音质参数>
```

#### API 启动开发模式

```bash
python main.py --mode api
```

- 访问接口：http://ip:port/类型解析
- 支持 GET 和 POST 请求

#### API 启动生产模式

##### Windows 下用 waitress

```bash
waitress-serve --listen=0.0.0.0:5000 main:app
```

##### Linux / macOS 下用 gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

- 访问接口：http://ip:port/类型解析
- 支持 GET 和 POST 请求

---

## 参数说明

### GUI 模式参数

| 参数         | 说明                         |
| ------------ | ---------------------------- |
| --mode       | 启动模式：api 或 gui         |
| --url        | 需要解析的网易云音乐地址     |
| --level      | 音质参数（见下方音质说明）   |

### API 模式参数

| 参数         | 说明                                         |
| ------------ | -------------------------------------------- |
| url / ids    | 网易云音乐地址或歌曲ID（二选一）             |
| level        | 音质参数（见下方音质说明）                   |
| type         | 解析类型：json / down / text（三选一）       |

| 类型参数         | 说明                                         |
| ------------ | -------------------------------------------- |
| Song_v1    | 单曲解析             |
| search        | 搜索解析                   |
| playlist         | 歌单解析       |
| album         | 专辑解析       |

---

## 音质参数说明（仅限单曲解析）

- `standard`：标准音质
- `exhigh`：极高音质
- `lossless`：无损音质
- `hires`：Hi-Res音质
- `jyeffect`：高清环绕声
- `sky`：沉浸环绕声
- `jymaster`：超清母带

> 黑胶VIP音质：standard, exhigh, lossless, hires, jyeffect  
> 黑胶SVIP音质：sky, jymaster

---

## 注意事项

- 必须使用黑胶会员账号的 Cookie 才能解析高音质资源。
- Cookie 格式请严格按照 `cookie.txt` 示例填写。
- 目前本人账号不是会员。

---

## 致谢

- 本项目在 [Suxiaoqinx](https://github.com/Suxiaoqinx/Netease_url) 提供的核心功能上进行了适当的修改补充，不知道作者是否愿意合并🤔？

---

## 反馈与交流

- 在 Github [Issues](https://github.com/lihuosheng/NeteaseMusic/issues) 提交反馈

---

欢迎 Star、Fork 和 PR！