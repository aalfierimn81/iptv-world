import os
class IPTVGenerator:

    tv_country_codes = []

    def __getConutryCodesList(self):
        import csv
        COUNTRY_CODES = 'contry_codes.csv'
        country_codes = []
        with open(COUNTRY_CODES, mode ='r') as file:
            csvFile = csv.reader(file, delimiter=';')
            for lines in csvFile:
                country_dict = dict()
                country_dict['code']=lines[0]
                country_dict['name']=lines[1]
                country_codes.append(country_dict)
        return country_codes

    def __getConutryCodesChannelList(self):
        file_list=os.listdir('iptv-master/streams')
        for i in range (0, len(file_list)):
            cc = str(file_list[i])[:2]
            if(cc not in self.tv_country_codes):
                self.tv_country_codes.append(cc)
        self.tv_country_codes.sort()
        return self.tv_country_codes
    
    def __getChannelId (self, line):
        TVGID = "tvg-id="
        id=line.find(TVGID)
        id=id+8
        line=line[id:]
        tvid = line[0:line.find('"')]
        return tvid

    def __getChannelName (self, desc):
        d1 = desc.find('(')
        d2 = desc.find('[')
        channel_name = desc
        if (d1==-1 and d2>-1):
            channel_name = desc[:d2]
        if (d1>-1 and d2==-1):
            channel_name = desc[:d1]
        if (d1>-1 and d2>-1):
            d=0
            if (d1>d2):
                d=d2
            else:
                d=d1
            channel_name = desc[:d]
        channel_name.strip()
        return (channel_name)

    def __createFile(self, id, link):
        name = id+".m3u"
        stream = open("channels/"+name, "w")
        FILE_HDR1 = "#EXTM3U\n"
        FILE_HDR2 = "#EXTVLCOPT:http-user-agent=HbbTV/1.6.1\n"
        file_string = FILE_HDR1+FILE_HDR2+link 
        stream.write(file_string)
        stream.close()
        return name

    def createIndex(self):
        ccl = self.__getConutryCodesList()
        tvccl = self.__getConutryCodesChannelList()     
        HTML_HEADER = "<!DOCTYPE html> <html> <head> <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"> <link rel=\"stylesheet\" href=\"style.css\"></head>"
        HTML_BODY = "<body> <div class=\"header\"> <h1>Lista canali</h1> </div>"
        HTML_TABLE = "<table border=\"1\">" 
        for i in range (0, len(tvccl)):
            for j in range (0, len (ccl)):
                if (ccl[j]['code']==tvccl[i].upper()):
                    country_name = ccl[j]['name']
                    HTML_TABLE = HTML_TABLE+"<tr> <td> <a href=\"pages/"+ccl[j]['code'].lower()+".html\">"+country_name+"</a></td> <td> <img src=\"https://flagsapi.com/"+tvccl[i].upper()+"/flat/64.png\"> </td> </tr>"
                    break

        HTML_TABLE = HTML_TABLE + "</table>"
        HTML_SPEGNI = "<div class=\"row\">  <div class=\"col-12 col-s-3 menu\"> <ul> </ul>  <li><form id = \"spegniForm\" action=\"spegni.php\" method=\"post\"> <button class=\"button\" type=\"submit\" class=\"button\"  name=\"submit\">Spegni</button> </form></li> </div> </div>"     
        HTML_END = "</body> </html>"
        html_string = HTML_HEADER+HTML_BODY+HTML_SPEGNI+HTML_TABLE+HTML_END
        fhtml = open("index.html", "w")
        fhtml.write(html_string)
        fhtml.close()
    
    def __checkStream(self, url):
        ok = 0
        from urllib.request import Request, urlopen
        from urllib.error import URLError, HTTPError
        req = Request(url)
        try:
            response = urlopen(req, timeout=10)
        except HTTPError as e:
            print(url, " Error code: ", e.code)
        except URLError as e:
            print(url, " Reason: ", e.reason)
        except TimeoutError as e:
            print (url, " Timeout")
        except ConnectionResetError as e:
            print (url, " Connection reset")
        except UnicodeEncodeError as e:
            print (e.reason, " UnicodeEncodeError")
        else:
            ok = 1
            print (url, "---> OK")
        return ok

    def __getChannelIcon(self, channel_name):
        import wikipedia
        import requests
        import json

        WIKI_REQUEST = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='
        try:
            result = wikipedia.search(channel_name, results = 1)
            wkpage = wikipedia.WikipediaPage(title = result[0])
            title = wkpage.title
            response  = requests.get(WIKI_REQUEST+title)
            json_data = json.loads(response.text)
            img_link = list(json_data['query']['pages'].values())[0]['original']['source']
            print (channel_name, "---> ICON OK!")
            return img_link        
        except:
            return 0

    def createChannelFiles (self):
        HTML_HEADER = "<!DOCTYPE html> <html> <head> <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"> <link rel=\"stylesheet\" href=\"../style.css\"></head>"
        HTML_BODY = "<body> <div class=\"header\"> <h1>Lista canali</h1> </div>"
        HTML_SPEGNI = "<div class=\"row\">  <div class=\"col-12 col-s-3 menu\"> <ul> </ul>  <li><form id = \"spegniForm\" action=\"../spegni.php\" method=\"post\"> <button class=\"button\" type=\"submit\" class=\"button\"  name=\"submit\">Spegni</button> </form></li> </div> </div>"
        for i in range (0, len(self.tv_country_codes)):
            print (self.tv_country_codes[i])
            HTML_TABLE = "<table border=\"1\">"
            tv_country=self.tv_country_codes[i]
            file_list=os.listdir('iptv-master/streams')
            work_files = []
            for i in range (0, len(file_list)):
                if (file_list[i][0:2]==tv_country):
                    work_files.append(file_list[i])

            file_string = ""
            for i in range (0, len(work_files)):
                f = open("iptv-master/streams/"+work_files[i], "r")
                file_string = file_string + f.read()
            lines = []
            lines = file_string.split('\n')
            
            html_string = HTML_HEADER+HTML_BODY+HTML_SPEGNI
            
            i=0
            while (i<len (lines)):
                if (lines[i][0:7]=='#EXTM3U'):
                    i=i+1
                    continue
                if (lines[i][0:7]=='#EXTINF' and lines[i+1][0:4]=="http"):
                    tvid=self.__getChannelId(lines[i])
                    channel_desc = lines[i][lines[i].find(',')+1:]
                    channel_name=self.__getChannelName (channel_desc)
                    i=i+1
                    link = lines[i]
                    i=i+1
                    stream_filename = self.__createFile (tvid,link)
                    icon = self.__getChannelIcon(channel_name+" Television")
                    available = self.__checkStream(link)
                    if (available==1):
                        HTML_TABLE = HTML_TABLE + "<tr> <td>"+channel_name+"</td>"
                    else:
                        HTML_TABLE = HTML_TABLE + "<tr> <td style=\"color: red; font size: 5px;\"><b>"+channel_name+"</b></td>"
                    if (icon==0):
                        HTML_TABLE = HTML_TABLE + "<td> no icon </td> <td><form id = \"submitForm\" action=\"../cambia_canale.php\" method=\"post\"><input type=\"hidden\" name=\"canale\" value=\""+stream_filename+"\"> <button type=\"submit\" class=\"button\"  name=\"submit\">Guarda</button> </form> </td> </tr>"
                    else:
                        HTML_TABLE = HTML_TABLE + "<td> <img src=\"" + icon + "\" class=\"responsive\"> </td> <td><form id = \"submitForm\" action=\"../cambia_canale.php\" method=\"post\"><input type=\"hidden\" name=\"canale\" value=\"../channels/"+stream_filename+"\"> <button type=\"submit\" class=\"button\"  name=\"submit\">Guarda</button> </form> </td> </tr>"
                    continue
                i=i+1
            html_string = html_string + HTML_TABLE
            html_string = html_string + "</table></body></html>"
            fhtml = open("pages/"+tv_country+".html", "w")
            fhtml.write(html_string)
            fhtml.close()

    def __init__(self):
         print("Generating channels...")

iptv = IPTVGenerator()
iptv.createIndex()
iptv.createChannelFiles()

    




