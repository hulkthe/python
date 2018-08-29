import requests
import re
import sys, getopt 
import tkinter as tk
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator


class Application(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        master.geometry('1024x780+30+30')
        master.configure(background="black")
        self.pack()
        self.create_widgets()
        self.set(0,2,'Hola')
    def create_widgets(self):

        self._widgets = []
        rows=10
        columns = 3

        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = tk.Label(self, text="%s/%s" % (row, column),borderwidth=1, width=10,relief="ridge")
                label.grid(row=row, column=column,sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)


    def say_hi(self):
        print('hi there, everyone!')


def download_mp3(url, name):
    r = requests.get(url, stream=True)
    with open(name.replace("\"","")+".mp3", 'wb') as f:
        total_size = file_size(url)
        print("downloading %s" % name.replace(" ","-"))
        
        if total_size is None:
            f.write(r.content)
        else:
            dl=0
            total_size = int(total_size)
            for data in r.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_size)
                sys.stdout.write("\r[%s%s]%s%%" % ('=' * done, ' '*(50-done),done*2))
                sys.stdout.flush()

def make_mp3_url(str): 
    str = str.replace('https://', 'http://')
    str = str.replace('-audios-mp3_rf', '_mf')
    str = str.replace('1.html', 'feed_1.mp3')
    return str

def sacarItems(soup, fg=None):
    if fg == None:
        channel = []
        for tag in soup.find_all(class_="flipper"):
            for content in tag.find_all('meta'):
                if content.get('itemprop') == 'url':
                    url = content.get('content')
                if content.get('itemprop') == 'name':
                    name = content.get('content')
                if content.get('itemprop') == 'description':
                    descr = content.get('content')
            channel.append({'name':name,'descr':descr,'url':url})
        return channel

    else:
        for tag in soup.find_all(class_="flipper"):
            fe = fg.add_entry(order='append')

            for content in tag.find_all('meta'):

                if content.get('itemprop') == 'url':
                    fe.id(content.get('content'))
                    #file_size(str)
                    fe.enclosure(make_mp3_url(content.get('content')), 0, 'audio/mpeg')

                if (content.get('itemprop') == 'name'):
                    fe.title(content.get('content'))

                if content.get('itemprop') == 'description':
                    fe.content(content.get('content'),type='CDATA')
        return fg

def file_size(url):
    """ Get audio file size """
    resGet = requests.get(url,stream=True)
    return resGet.headers['Content-Length']

def podcast_election(soup, url):

    i = 1
    search_term = soup.find(class_="row").findChildren()

    while len(list(search_term)) > 0:
        channels = sacarItems(soup)
        i = i + 1

        fp = requests.get(url+str(i)+".html")
        soup = BeautifulSoup(fp.content.decode('utf8'), 'html.parser')
        soup = soup.find('div', {"id": "main"})
        search_term = soup.find(class_="row").findChildren()
    j = 0
    for channel in channels:
        j=j+1
        print(j,channel['name'], channel['descr'][0:100]+'...',sep=' - ')
    pod_elegido = input('¿Que canal elige? (0 para ninguno):')
    if pod_elegido =='0' :
        sys.exit()
    else:
        return channels[int(pod_elegido)-1]['url']

def recortar_url(url):
    return url[0:url.find('1.html')]
    
def gen_podcast_feed(url) :
    fg = FeedGenerator()
    fg.load_extension('podcast')

    #url = "https://www.ivoox.com/audios-biblioteca-tizca_s0_f2275262_p2_1.html" #Auto-load 
    #url = "https://www.ivoox.com/podcast-biblioteca-tizca_sq_f1370364_1.html" #formato normal
    #url = 'https://www.ivoox.com/escuchar-lvdh_nq_189868_1.html' # formato canal - Hay que entrar en el podcast
    #url= 'https://www.ivoox.com/biblioteca-de-trantor_bk_list_39874_1.html' #lista
    #url = 'https://www.ivoox.com/escuchar_bk_list_5758_1.html' #lista

    pod_type = ''
    i = 1
    url = recortar_url(url)
    fp = requests.get(url+str(i)+".html")
    soup = BeautifulSoup(fp.content, 'html.parser', from_encoding="utf8")

    #soup = soup.find('div',{"id":"main"})


    if url.find('_bk_list_') >= 0:
        pod_type = 'lista'
        soup = soup.find('div', {"id": "main"})
    elif url.find('-audios-mp3_rf_') >=0:
        pod_type = 'capitulo'
    else:
        pod_type = url[url.find('.com/')+5:url.find('-')]
        soup = soup.find('div', {"id": "main"})
        

    
    if pod_type == 'podcast' or 'lista' or 'escuchar':
       search_term =  soup.find(class_="row").findChildren()
    if pod_type == 'audios':
       search_term = soup.find(id="channelPageAudios").findChildren()

    if pod_type == 'escuchar':
        url = podcast_election(soup, url)
        fp = requests.get(url)
        url = recortar_url(url)
        soup = BeautifulSoup(fp.content, 'html.parser')
        soup = soup.find('div', {"id": "main"})
    
    if pod_type == 'capitulo':
        """ fg.id(soup.find('a', {'itemprop': 'item'}).get('href'))
        fg.logo(soup.find('img', {'class': 'main'}).get('src'))
        fg.title(soup.find('a',{'itemprop': 'item'}).get('title'))
        #fg.id(soup.find('a',{'itemprop':'item'}).get('title'))
        fg.author({'name':soup.find('h1',{'class':'pull-left'}).text.strip()})
        fg.subtitle(soup.find('p', {'class': 'description'}).text.strip())
        fg.link(href=soup.find('a', {'itemprop': 'item'}).get('href'),rel="alternate")

        fe = fg.add_entry(order='append')
        fe.id(url)
        fe.content( soup.find('h1', {'class': 'pull-left'}).text.strip())
        fe.enclosure(make_mp3_url(url+'1.html'), 0, 'audio/mpeg') """

        download_mp3(make_mp3_url(url+'1.html'),soup.find('h1', {'class': 'pull-left'}).text.strip())
    else:
        fg.id(soup.find('div',{"class":"wrapper"}).a.get('href'))
        fg.title(soup.find(id="list_title_new").text)
        fg.author({'name': soup.find(class_="info").a.text})
        fg.link(href=soup.find(class_="wrapper").a.get('href'), rel='alternate')
        fg.logo(soup.find(class_="imagen-ficha").img.get('src'))
        if soup.find(class_="overview").text.strip() :
            fg.subtitle(soup.find(class_="overview").text.strip())
        else:
            fg.subtitle(' ')
            
        fg.language('es')

        while len(list(search_term)) > 0:
            if soup.find(class_="jumbotron"):
                break
            fg = sacarItems(soup, fg)
            i = i + 1
            
            fp = requests.get(url+str(i)+".html")
            soup = BeautifulSoup(fp.content.decode('utf8'), 'html.parser')
            soup = soup.find('div', {"id": "main"})

            if pod_type == 'audios':
                search_term = soup.find(id="channelPageAudios").findChildren()
            if pod_type == 'podcast' or 'lista' or 'escuchar' :
                search_term =  soup.find(class_="row").findChildren()

        fg.rss_file('podcast.rss',pretty=True)

def search_podcast(param):
    url = "https://www.ivoox.com/suggest_sz_"
    search = requests.get(url+param+"_1.html")
    soup = BeautifulSoup(search.content,'html.parser')
    i = 1
    channels = []
    for tag in soup.find_all(class_="text-ellipsis"):
        channels.append({'name': tag.a.get('title'), 'url': tag.a.get('href')})  
        print(i, tag.div.text.strip(), tag.a.get('title'), tag.a.get('href'), sep=" - ")
        i += 1
    pod_elegido = input('¿Que elige? (0 para ninguno):')
    if pod_elegido == '0':
        sys.exit()
    else:
        gen_podcast_feed(channels[int(pod_elegido)-1]['url'])

root = tk.Tk()
#root.overrideredirect(True)
app = Application(master=root)
app.mainloop()

""" def main(self, argv):
    try:
        opts,args = getopt.getopt(argv, "s:p:", ["sstring","pstring"])
    except getopt.GetoptError:
        print("podcast.py -s parametros_de_busqueda -p <url podcast>")
        sys.exit()
    
    for opt,arg  in opts:
        if opt == "-s":
            search_podcast(arg)
        if opt =='-p':
            gen_podcast_feed(arg)

if __name__=="__main__":
    if len(sys.argv) >1:
        main(main, sys.argv[1:])
    else:
        print("podcast.py -s parametros_de_busqueda -p <url podcast>")
        sys.exit() """
