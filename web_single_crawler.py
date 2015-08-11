from scrapy.http import HtmlResponse

import gtk
import webkit
import jswebkit
import logging
import sys
import getopt
from lxml import etree
import lxml.html as HTML

reload(sys)
sys.setdefaultencoding("utf-8")
class WebkitDownloader( object ):

    def stop_gtk(self, v, f):
        gtk.main_quit()

    def _get_webview(self):
        webview = webkit.WebView()
        props = webview.get_settings()
        props.set_property('enable-java-applet', False)
        props.set_property('enable-plugins', False)
        props.set_property('enable-page-cache', False)
        return webview

    def process_request( self, url, xpath ):
        webview = self._get_webview()
        webview.connect('load-finished', self.stop_gtk)
        webview.load_uri(url)
        gtk.main()
        ctx = jswebkit.JSContext(webview.get_main_frame().get_global_context())
        url = ctx.EvaluateScript('window.location.href')
        html = ctx.EvaluateScript('document.documentElement.innerHTML')
        html = '<html>'+html+'</html>'

        doc = HTML.fromstring(html)
        
        news_list = doc.xpath(xpath+'//a')
        items = []
        for news in news_list:
            item = {'text':'','href':''}
            text = news.text_content()
            link = news.attrib['href']
            item['text'] = text
            item['href'] = link

            items.append(item)
        return self.transJson(items)

    def transJson(self,items):
        str = '['
        for i in items:
            str += '{\"text\":\"'+i['text']+'\",\"href\":\"'+i['href']+'\"},'
        str = str[0:-1]
        str += ']'
        return str

shortargs = ''
longargs = ['url=','xpath=']
opts, args = getopt.getopt( sys.argv[1:], shortargs, longargs)

url = None
xpath = None
for t in opts:
    if t[0]=="--url":
        url = t[1]
    if t[0]=="--xpath":
        xpath = t[1]

if (url is not None and xpath is not None):
    sys.stdout.write('hello world1!\n')
    crawler = WebkitDownloader()
    res = crawler.process_request(url, xpath)
    print res.encode('utf-8')
    sys.stdout.write(res.encode('utf-8'))
    sys.stdout.write('hello world2!\n')