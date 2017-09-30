# -*- coding: utf-8 -*-

import time

today = time.strftime('%Y-%m-%dT%H:%M+08:00', time.localtime())

base_template = '''\
<url>
<loc><![CDATA[http://wan123.tv/v/{video.uid}]]></loc>
<lastmod><![CDATA[{date_time}]]></lastmod>
<changefreq>always</changefreq>
<priority>1.0</priority>
</url>
'''
def generate_base_sitemap(videos, file_path):
    
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    xml_str += ''.join(['<url>\n', '<loc>http://wan123.tv</loc>', '<lastmod>%s</lastmod>\n' % today, '<changefreq>hourly</changefreq>\n<priority>1.0</priority>\n', '</url>\n'])

    for each_video in videos:

        xml_str += base_template.format(video=each_video, date_time=today)

    xml_str += '</urlset>'

    with open(file_path, "w+") as out_f:
        out_f.write(xml_str)


google_template = '''\
<url>
<loc><![CDATA[http://wan123.tv/v/{video.uid}]]></loc>
<image:image>
<image:loc><![CDATA[http://tinimage.wan123.tv/{video.video_pic}]]></image:loc>
</image:image>
<lastmod><![CDATA[{date_time}]]></lastmod>
<video:video>
<video:content_loc><![CDATA[http://encode.tinvideo.wan123.tv/{video.encoded_url}]]></video:content_loc>
<video:player_loc allow_embed="yes" autoplay="ap=1"><![CDATA[http://wan123.tv/static/js/jwplayer.flash.swf]]></video:player_loc>
<video:thumbnail_loc><![CDATA[http://tinimage.wan123.tv/{video.video_pic}]]></video:thumbnail_loc>
<video:title><![CDATA[{video.title}]]></video:title>
</video:video>
<changefreq>always</changefreq>
<priority>1.0</priority>
</url>
'''
def generate_google_sitemap(videos, file_path):
    
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n'

    xml_str += ''.join(['<url>\n', '<loc>http://wan123.tv</loc>', '<lastmod>%s</lastmod>\n' % today, '<changefreq>hourly</changefreq>\n<priority>1.0</priority>\n', '</url>\n'])

    for each_video in videos:

        xml_str += google_template.format(video=each_video, date_time=today)

    xml_str += '</urlset>'

    with open(file_path, "w+") as out_f:
        out_f.write(xml_str)


baidu_template = '''\
<item>
    <op>add</op> 
    <title>
        <![CDATA[{video.title}]]> 
    </title>
    <category>
        <![CDATA[原创]]> 
    </category>
    <playLink>
        <![CDATA[http://wan123.tv/v/{video.uid}]]> 
    </playLink>
    <imageLink>
        <![CDATA[http://tinimage.wan123.tv/{video.video_pic}]]> 
    </imageLink>
    <userid>
        <![CDATA[{video.creater.username}]]> 
    </userid>
    <userurl>
        <![CDATA[http://wan123.tv/v/{video.creater.uid}]]> 
    </userurl>
    <playNum>
        <![CDATA[{video.play_count}]]> 
    </playNum>
    <tag>
        <![CDATA[手游视频]]> 
    </tag>
    <tag>
        <![CDATA[{video.game}游戏视频]]> 
    </tag>
    <comment>
        <![CDATA[{video.title}]]> 
    </comment>
    <pubDate>{date_time}</pubDate>
    <duration>{video.time}</duration>
</item>
'''
def generate_baidu_sitemap(videos, file_path):
    
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'

    xml_str += '<document>\n<webSite>wan123.tv</webSite>\n<webMaster>lianxiang@wan123.tv</webMaster>\n<updatePeri>60</updatePeri>\n'

    for each_video in videos:
        xml_str += baidu_template.format(video=each_video, date_time=today)

    xml_str += '</document>'

    with open(file_path, "w+") as out_f:
        out_f.write(xml_str)
