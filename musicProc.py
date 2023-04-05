import os, time, datetime, traceback, urllib, re, subprocess
from datetime import datetime

from .model import ModelMusicItem
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError, APIC, TT2, TPE1, TRCK, TALB, USLT, error, TIT2, TORY, TCON, TYER, USLT
from mutagen.mp3 import EasyMP3 as MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
import mutagen
import asyncio
from shazamio import Shazam
import requests
from lxml import html

class musicProc:
    
    session = requests.Session()
    headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Accept-Language' : 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer' : ''
            }
     
    def __init__(self, P):
        self.P = P
    
    def run(self):
        P = self.P
        try:
            P.logger.debug("음악정리 시작!")
            
            download_path = P.ModelSetting.get('download_path')
            organize_path = P.ModelSetting.get('proc_path')
            err_path = P.ModelSetting.get('err_path')
            interval = P.ModelSetting.get('interval')
            emptyFolderDelete = P.ModelSetting.get('emptyFolderDelete')
            
            P.logger.debug( "download_path :%s"%download_path)
            P.logger.debug( "organize_path :%s"%organize_path)
            P.logger.debug( "err_path :%s"%err_path)
            P.logger.debug( "interval :%s"%interval)
            P.logger.debug( "emptyFolderDelete :%s"%emptyFolderDelete)
            
            dirList = []
            fileList = []
            
            for dir_path, dir_names, file_names in os.walk(download_path):
                rootpath = os.path.join(os.path.abspath(download_path), dir_path)
                
                if os.path.isdir(dir_path):
                    dirList.append(dir_path)

                for file in file_names:

                    try:
                        filepath = os.path.join(rootpath, file)
                        P.logger.debug( filepath )
                        self.mp3FileProc(filepath)
                        time.sleep(int(interval))

                    except Exception as e:
                        try:
                            P.logger.debug('=========오류 문의시 필수 첨부해 주세요 [음악정리 작업중 오류]]].============')
                            P.logger.debug('Exception:%s', e)
                            P.logger.debug(traceback.format_exc())
                            P.logger.debug('=========오류 문의시 필수 첨부해 주세요 [음악정리 작업중 오류]]].============')

                            newFilePath = os.path.join(rootpath, file).replace(download_path, "")
                            newFilePath = os.path.join('%s%s%s%s%s' % (err_path, os.path.sep, 'ERR', os.path.sep, newFilePath)).replace(str(os.path.sep+os.path.sep),str(os.path.sep))
                            newFolderPath = os.path.join(newFilePath.replace(os.path.basename(file),""))
                            realFilePath = self.fileMove(file , newFolderPath, newFilePath)

                            self.procSave("6" , "", "", "", "", "", "", "", realFilePath)
                            
                        except Exception as e:
                            P.logger.debug('Exception:%s', e)
                            P.logger.debug(traceback.format_exc())

            if P.ModelSetting.get_bool('emptyFolderDelete'):
                dirList.reverse()
                for dir_path in dirList:
                    P.logger.debug( "dir_path : " + dir_path)
                    if download_path != dir_path and len(os.listdir(dir_path)) == 0:
                        os.rmdir(dir_path)

            P.logger.debug("===============END=================")
        
        except Exception as e:
            P.logger.error('Exception:%s', e)
            P.logger.error(traceback.format_exc())

    def mp3FileProc(self, file):
        
        P = self.P

        download_path = P.ModelSetting.get('download_path')
        organize_path = P.ModelSetting.get('proc_path')
        err_path = P.ModelSetting.get('err_path')
        maxCost = P.ModelSetting.get('maxCost')
        singleCost = P.ModelSetting.get('singleCost')
        
        notMp3delete = P.ModelSetting.get('notMp3delete')

        folderStructure = P.ModelSetting.get('folderStructure')
        fileRename = P.ModelSetting.get('fileRename')
        fileRenameSet = P.ModelSetting.get('fileRenameSet')

        isEncodingType = P.ModelSetting.get('isEncodingType')
        isTagUpdate = P.ModelSetting.get('isTagUpdate')
        

        ext = file.split(".")[-1]

        if ext.upper() in "MP3|FLAC|M4A":

            #인코딩 변경
            if P.ModelSetting.get_bool('isEncoding') and ext.upper() in isEncodingType:
                P.logger.debug( "인코딩 변경 ")
                subprocess.check_output (['mid3iconv', '-e', 'cp949', os.path.join(file)])
                
            if os.path.isfile(file):
                P.logger.debug("파일존재 확인"  + file)
                
                tags = self.getTagInfo(file)
                
                if tags == {} :
                    
                    shazamTagInfo = None

                    if P.ModelSetting.get_bool('isShazam') :
                        shazamTagInfo = self.findChazam(file)

                    if shazamTagInfo == None:
                        P.logger.debug("NO TAG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        newFilePath = file.replace(download_path, "")
                        newFilePath = os.path.join('%s%s%s%s%s' % (err_path, os.path.sep, 'nonTAG', os.path.sep, newFilePath)).replace(str(os.path.sep+os.path.sep),str(os.path.sep))
                        newFolderPath = os.path.join(newFilePath.replace(os.path.basename(file),""))
                        realFilePath = self.fileMove(file , newFolderPath, newFilePath)

                        self.procSave("4" , "", "", "", "", "", "", "", realFilePath)
                        return
                    else:
                        titlaByTag = shazamTagInfo['title'].upper().strip()
                        artistByTag = shazamTagInfo['artist'].upper().strip()
                        albumByTag = shazamTagInfo['album'].upper().strip()
                    
                else:
                    titlaByTag = tags['titlaByTag']
                    artistByTag = tags['artistByTag']
                    albumByTag = tags['albumByTag']

                P.logger.debug( "titlaByTag : " + titlaByTag)
                P.logger.debug( "artistByTag : " + artistByTag)
                P.logger.debug( "albumByTag : " + albumByTag)

                searchKey = titlaByTag + " " + artistByTag
                searchKey = re.sub('\([\s\S]+\)', '', searchKey).strip()
                
                P.logger.debug("검색어 "  + searchKey )
                
                #목록검색
                url = 'https://m.app.melon.com/search/mobile4web/searchsong_list.htm?cpId=WP10&cpKey=&memberKey=0&keyword='
                url = '%s%s' % (url, urllib.parse.quote(searchKey.encode('utf8')))
                
                P.logger.debug( "url : " + url)

                data = self.get_html(url)
                P.logger.debug( data )
                tree = html.fromstring(data)

                lis = tree.xpath('/html/body/div[1]/form/ul/li')

                match = False
                isGenreExc = False

                title = ""
                artist = ""
                album = ""

                for li in lis:
                    
                    title = li.get('d-songname').strip().upper()
                    artist = re.sub('\([\s\S]+\)', '', li.get('d-artistname')).strip().upper()
                    album = re.sub('\([\s\S]+\)', '', li.get('d-albumname')).strip().upper()

                    titleMaxLength = 0
                    if len(titlaByTag) <= len(title):
                        titleMaxLength = len(title)
                    else:
                        titleMaxLength = len(titlaByTag)
                    
                    artistMaxLength = 0
                    if len(artistByTag) <= len(artist):
                        artistMaxLength = len(artist)
                    else:
                        artistMaxLength = len(artistByTag)

                    albumMaxLength = 0
                    if len(albumByTag) <= len(album):
                        albumMaxLength = len(album)
                    else:
                        albumMaxLength = len(albumByTag)
                    
                    P.logger.debug( "titlaByTag : " + str( titlaByTag )  + "|| title : " + str( title) + " || titleMaxLength : " + str( titleMaxLength) )
                    P.logger.debug( "artistByTag : " + str( artistByTag ) + "|| artist : " + str( artist) + " || artistMaxLength : " + str( artistMaxLength) )
                    P.logger.debug( "albumByTag : " + str( albumByTag ) + "|| album : " + str( album) + "|| albumMaxLength : " + str( albumMaxLength) )
                        
                    titlelcs = self.lcs(titlaByTag, title)
                    artistlcs = self.lcs(artistByTag, artist)
                    albumlcs = self.lcs(albumByTag, album)
                    
                    titleSimilarity = ( float(titlelcs) / float(titleMaxLength) ) * 100
                    artistSimilarity = ( float(artistlcs) / float(artistMaxLength) ) * 100
                    albumSimilarity = ( float(albumlcs) / float(albumMaxLength) ) * 100
                    
                    P.logger.debug( "titlaByTag : " + str( titlaByTag )  + "|| title : " + str( title) + " || titleMaxLength : " + str( titleMaxLength) + " || titlelcs : " + str( titlelcs ) + " || titleSimilarity : " + str( titleSimilarity))
                    P.logger.debug( "artistByTag : " + str( artistByTag ) + "|| artist : " + str( artist) + " || artistMaxLength : " + str( artistMaxLength) + " || artistlcs : " + str( artistlcs ) + " || artistSimilarity : " + str( artistSimilarity))
                    P.logger.debug( "albumByTag : " + str( albumByTag ) + "|| album : " + str( album) + "|| albumMaxLength : " + str( albumMaxLength) + " || albumlcs : " + str( albumlcs ) + " || albumSimilarity : " + str( albumSimilarity))
                    P.logger.debug( "------------------------------------")
                    
                    if ( titleSimilarity + artistSimilarity + albumSimilarity ) > int(maxCost) and ( titleSimilarity > 0 and artistSimilarity > 0 and albumSimilarity > int(singleCost) ) :

                        songId = li.get('d-songid').strip()
                        albumId = li.get('d-albumid').strip()

                        tags = self.getSongTag(songId, albumId)
                        

                        #제목
                        title = tags['title']
                        title = title.replace("/",",")
                        #아티스트
                        artist = tags['artist']
                        artist = artist.replace("/",",")
                        #앨범
                        album = tags['album']
                        album = album.replace("/",",")
                        #트랙
                        track = tags['track']
                        P.logger.debug( "tags['track'] : " + tags['track']  + "|| track : " + track )
                        #발매년도
                        year = tags['year']
                        #장르
                        genre = tags['genre']
                        genre = genre.replace("/",",")

                        P.logger.debug( tags )
                        
                        folderStructure = folderStructure.replace('%title%', title)
                        folderStructure = folderStructure.replace('%artist%', artist)
                        folderStructure = folderStructure.replace('%album%', album)
                        folderStructure = folderStructure.replace('%year%', year)
                        folderStructure = folderStructure.replace('%genre%', genre)
                        
                        if P.ModelSetting.get_bool('fileRename'):
                            fileRenameSet = fileRenameSet.replace('%title%', title)
                            fileRenameSet = fileRenameSet.replace('%artist%', artist)
                            fileRenameSet = fileRenameSet.replace('%album%', album)
                            fileRenameSet = fileRenameSet.replace('%track%', track)
                            fileRenameSet = fileRenameSet.replace('%year%', year)
                            fileRenameSet = fileRenameSet.replace('%genre%', genre)
                            
                            fileRenameSet = os.path.join('%s%s' % (fileRenameSet, os.path.splitext(file)[1]))
                        else:
                            fileRenameSet = os.path.basename(file)
                        
                        extTmp = fileRenameSet.split(".")[-1].lower()
                        fileRenameSet = fileRenameSet.replace(fileRenameSet.split(".")[-1],extTmp)
                        P.logger.debug("folderStructure : %s", folderStructure)
                        P.logger.debug("fileRenameSet : %s", fileRenameSet)
                        P.logger.debug("os.path.sep : %s", os.path.sep)
                        P.logger.debug("organize_path : %s", organize_path)

                        newFilePath = os.path.join('%s%s%s%s%s' % (organize_path, os.path.sep, folderStructure, os.path.sep, fileRenameSet)).replace("//","/")
                        newFolderPath = os.path.join('%s%s%s' % (organize_path, os.path.sep, folderStructure)).replace("//","/")

                        P.logger.debug("newFilePath : %s", newFilePath)
                        P.logger.debug("newFolderPath : %s", newFolderPath)

                        match = True
                        
                        if os.path.isfile(newFilePath):
                            
                            status = ""
                            
                            if P.ModelSetting.get_bool('isDupeDel'):
                                P.logger.debug("중복 삭제 처리")
                                os.remove(file)
                                realFilePath = ""
                                status = "7"
                            else:

                                newFilePath = file.replace(download_path, "")
                                newFilePath = os.path.join('%s%s%s%s%s' % (err_path, os.path.sep, 'fileDupe', os.path.sep, newFilePath)).replace(str(os.path.sep+os.path.sep),str(os.path.sep))
                                newFolderPath = os.path.join(newFilePath.replace(os.path.basename(file),""))
                                realFilePath = self.fileMove(file , newFolderPath, newFilePath)
                                status = "2"
                            
                            self.procSave(status , title, artist, album, titlaByTag, artistByTag, albumByTag, searchKey, realFilePath)
                            return
                            
                        else:

                            if P.ModelSetting.get_bool('isTagUpdate'):
                                P.logger.debug( "테그 정보 업데이트 ")
                                self.tagUpdateAll(file, tags)
                            
                            genreExcs = P.ModelSetting.get('genreExc')

                            for genreExc in genreExcs.split("|"):
                                P.logger.debug( "genreExc to genre : %s to %s", genreExc, genre)
                                if len(genreExc) > 0 and genreExc in genre:
                                    P.logger.debug( "genre Match")
                                    isGenreExc = True
                            
                            if isGenreExc:
                                newFilePath = file.replace(download_path, "")
                                newFilePath = os.path.join('%s%s%s%s%s' % (err_path, os.path.sep, 'genreExc', os.path.sep, newFilePath)).replace(str(os.path.sep+os.path.sep),str(os.path.sep))
                                newFolderPath = os.path.join(newFilePath.replace(os.path.basename(file),""))
                                realFilePath = self.fileMove(file , newFolderPath, newFilePath)
                                self.procSave("8" , title, artist, album, titlaByTag, artistByTag, albumByTag, searchKey, realFilePath)
                            else:
                                realFilePath = self.fileMove(file,  os.path.join(newFolderPath), os.path.join(newFilePath))
                                self.procSave("1" , title, artist, album, titlaByTag, artistByTag, albumByTag, searchKey, realFilePath)
                            return
                    
                if len(lis) < 1 or not match:
                    
                    newFilePath = file.replace(download_path, "")
                    newFilePath = os.path.join('%s%s%s%s%s' % (err_path, os.path.sep, 'nonSearch', os.path.sep, newFilePath)).replace(str(os.path.sep+os.path.sep),str(os.path.sep))
                    newFolderPath = os.path.join(newFilePath.replace(os.path.basename(file),""))
                    realFilePath = self.fileMove(file , newFolderPath, newFilePath)
                    status = ""
                    if len(lis) < 1 :
                        status = "5"
                    else:
                        status = "3"
                    #P.logger.debug(status)
                    self.procSave(status , title, artist, album, titlaByTag, artistByTag, albumByTag, searchKey, realFilePath)
                
            else:
                P.logger.debug("파일존재 미확인")
        else:
            P.logger.debug("MP3 아님 " + file)
            if notMp3delete == "True":
                P.logger.debug("삭제 처리")
                os.remove(file)
            

        P.logger.debug("================================")

    def getTagInfo(self, file):
        P = self.P
        ext = file.split(".")[-1]

        tagsRtn = {}
        try:
            if ext.upper() == "MP3":
                audio = MP3(file)
                if len( audio ) == 0:
                    return tagsRtn
                if "title" not in audio.tags.keys() or "artist" not in audio.tags.keys() or "album" not in audio.tags.keys():
                    return tagsRtn
                else:
                    tagsRtn['titlaByTag'] = audio.tags['title'][0].upper().strip()
                    tagsRtn['artistByTag'] = audio.tags['artist'][0].upper().strip()
                    tagsRtn['albumByTag'] = audio["album"][0].upper().strip()
            if "M4A" == ext.upper() :
                tags = MP4(file)
                tagsRtn['titlaByTag'] = str( tags.get('\xa9nam')[0] ).upper().strip()
                tagsRtn['artistByTag'] = str( tags.get('\xa9ART')[0] ).upper().strip()
                tagsRtn['albumByTag'] = str( tags.get('\xa9alb')[0] ).upper().strip()
            if "FLAC" == ext.upper() :
                tags = FLAC(file)
                tagsRtn['titlaByTag'] = str( tags.get('title')[0] ).upper().strip()
                tagsRtn['artistByTag'] = str( tags.get('artist')[0] ).upper().strip()
                tagsRtn['albumByTag'] = str( tags.get('album')[0] ).upper().strip()
        except Exception as e:
            P.logger.debug('Exception:%s', e)
            P.logger.debug(traceback.format_exc())

        return tagsRtn
    
    def fileMove(self, originPath , newFolderPath, newFilePath):

        P = self.P
        #newFolderPath = re.sub('[\<\>\:\|\*\?\"]', '_', newFolderPath).strip()
        #newFilePath = re.sub('[\<\>\:\|\*\?\"]', '_', newFilePath).strip()
        
        P.logger.debug("파일이동 시작")
        P.logger.debug(originPath + " ===>> " + newFilePath)
        if not os.path.isdir(newFolderPath):
            P.logger.debug("폴더 생성 : " + newFolderPath)
            os.makedirs(newFolderPath)
        
        if os.path.exists(newFilePath):
            os.remove(newFilePath)
        
        import shutil
        shutil.move(originPath, newFilePath)
        P.logger.debug("파일이동 완료")
        
        return newFilePath

    def procSave(self, statusCd , title, artist, album, titleByTag, artistByTag, albumByTag, searchKey, file):

        db_item = ModelMusicItem()
        
        db_item.statusCd = statusCd

        if statusCd == "1":
            db_item.status = "정상"
        elif statusCd == "2":
            db_item.status = "중복"
        elif statusCd == "3":
            db_item.status = "매칭실패"
        elif statusCd == "4":
            db_item.status = "태그정보없음"
        elif statusCd == "5":
            db_item.status = "검색결과없음"
        elif statusCd == "6":
            db_item.status = "오류"
        elif statusCd == "7":
            db_item.status = "중복삭제"
        elif statusCd == "8":
            db_item.status = "장르예외"

        db_item.title = title
        db_item.artist = artist
        db_item.album = album
        db_item.titleByTag = titleByTag
        db_item.artistByTag = artistByTag
        db_item.albumByTag = albumByTag
        db_item.searchKey = searchKey 
        db_item.filePath = file

        db_item.save()

    def findChazam(self, mp3Path=None):
        P = self.P

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            if str(e).startswith('There is no current event loop in thread'):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            else:
                raise

        P.logger.debug( mp3Path )
        
        out = loop.run_until_complete(self.shazamFind(mp3Path))
        if len(out['matches']) > 0 :
            album = ''
            trackInfo = out['track']
            metadata = trackInfo['sections'][0]['metadata']
            for i in metadata:
                if i['title'] == 'Album':
                    album = i['text']
            return {'title':trackInfo['title'], 'artist':trackInfo['subtitle'], 'album':album}
        else:
            return None

    async def shazamFind(self, mp3Path):
        
        shazam = Shazam()
        out = await shazam.recognize_song(mp3Path)
        return out

    def get_html(self, url, referer=None, stream=False):

        P = self.P
        try:
            session = None
            data = ""

            if self.session is None:
                self.session = requests.session()
            #logger.debug('get_html :%s', url)
            self.headers['Referer'] = '' if referer is None else referer
            try:
                page_content = self.session.get(url, headers=self.headers)
            except Exception as e:
                P.logger.debug("Connection aborted!!!!!!!!!!!")
                time.sleep(10) #Connection aborted 시 10초 대기 후 다시 시작
                page_content = self.session.get(url, headers=self.headers)

            data = page_content.text
            # P.logger.debug( "get_html IN data :" + data)
        except Exception as e:
            P.logger.error('Exception:%s', e)
            P.logger.error(traceback.format_exc())
        return data

    def lcs(self, a, b):

        if len(a) == 0 or len(b) == 0:
            return 0
        if a == b :
            if len(a)<len(b):
                return len(b)
            else:
                return len(a)

        if len(a)<len(b):
            c = a
            a = b
            b = c
        prev = [0]*len(a)
        for i,r in enumerate(a):
            current = []
            for j,c in enumerate(b):
                if r==c:
                    e = prev[j-1]+1 if i* j > 0 else 1
                else:
                    e = max(prev[j] if i > 0 else 0, current[-1] if j > 0 else 0)
                current.append(e)
            prev = current
        
        return current[-1]
    

    def getSongTag(self, songId, albumId):
        
        P = self.P
        P.logger.debug("songId : %s" , songId)
        P.logger.debug("albumId : %s" , albumId)
        allTag = {}

        url = 'https://m.app.melon.com/song/detail.htm?songId='
        url = '%s%s' % (url, urllib.parse.quote(songId))
        
        data = self.get_html(url)
        tree = html.fromstring(data)

        #제목
        try:
            h1 = tree.xpath('/html/body/div[1]/main/div[1]/div/div[2]/div[2]/h2')[0]
                             
            title = h1.text.strip()
            allTag['title'] = title
        except Exception as e:
            allTag['title'] = ""
        #logger.debug( "제목 : " + title )

        #아티스트
        try:
            artist = ""
            div = tree.xpath('/html/body/div[1]/main/div[1]/div/div[2]/div[3]/div')[0]
            userName = div.find_class("user-name")
            artist = userName[0].text.strip()
            # logger.debug( userName )
            # logger.debug( userName[0].text.strip() )
            # artist = p.text.strip()
            allTag['artist'] = artist
        except Exception as e:
            allTag['artist'] = ""
        P.logger.debug( "아티스트 : " + artist )

        #장르
        try:
            span = tree.xpath('/html/body/div[1]/main/div[2]/div[2]/div[2]/dl/div[4]/dd/div')[0]
            genre = span.text.strip()
            allTag['genre'] = genre
        except Exception as e:
            allTag['genre'] = ""
        #logger.debug( "장르 : " + genre )


        
        url = 'https://m.app.melon.com/album/music.htm?albumId='
        url = '%s%s' % (url, urllib.parse.quote(albumId))
        
        data = self.get_html(url)
        tree = html.fromstring(data)

        p = tree.xpath('/html/body/div[1]/main/div[2]/div[2]/div[2]/dl/div[3]/dd/div')
        #제작년도
        try:
            year = p[0].text[:4]
            allTag['year'] = year
        except Exception as e:
            allTag['year'] = ""
        #logger.debug( "제작년도 : " + year )
        
        #트랙
        try:
            track = "00"
            divs = tree.xpath( '/html/body/div[1]/main/div[2]/div[1]/div/ul/li/div/div')
            # logger.debug( "debug test : %s" % songId )
            for div in divs:
                for a in list(div):
                    if a.attrib.get('href') != None:
                        if songId in a.attrib.get('href'):
                            for it in div.iter('span'):
                                if 'num-track' in it.attrib.get('class'): 
                                    track = it.text
                                    
            allTag['track'] = track
        except Exception as e:
            allTag['track'] = ""
        #logger.debug( "트랙 : " + track )
        
        #앨범이미지
        try:
            albumImage = ""
            meta = tree.xpath('/html/head/meta[7]')[0]
            albumImage = meta.attrib.get("content")
            allTag['albumImage'] = albumImage
        except Exception as e:
            allTag['albumImage'] = ""
        #logger.debug( "앨범이미지 : " + albumImage )

        #앨범
        try:
            album = ""
            
            p = tree.xpath('/html/body/div[1]/main/div[1]/div[2]/div[1]/div/h2')[0]
            album = p.text.strip()
            allTag['album'] = album
        except Exception as e:
            allTag['album'] = ""
        #logger.debug( "앨범 : " + album )

        #가사
        try:
            url = 'https://m.app.melon.com/song/lyrics.htm?songId='
            url = '%s%s' % (url, urllib.parse.quote(songId))
            
            data = self.get_html(url)
            tree = html.fromstring(data)
            
            div = tree.xpath('/html/body/div[1]/main/div[2]/div[1]/div[2]/div/div[1]/div')[0]
            # logger.debug("가사")
            # logger.debug(div)
            
            lyrics = htmlstring(div, encoding='utf8').decode('utf-8')
            # logger.debug(type(lyrics))
            
            lyrics = lyrics.replace('<div class="lyrics">',"")
            lyrics = lyrics.replace("&#13;","")
            lyrics = lyrics.replace("</div>","")
            lyrics = lyrics.replace("<br/>","\n").strip()
            # logger.debug(lyrics)
            allTag['lyrics'] = lyrics
        except Exception as e:
            allTag['lyrics'] = ""
            # logger.debug( "가사 : " + e )

        return allTag

    def tagUpdateAll(self, filePath, tags):

        P = self.P

        album = tags['album']
        lyrics = tags['lyrics']
        artist = tags['artist']
        track = tags['track']
        title = tags['title']
        albumImage = tags['albumImage']
        year = tags['year']
        genre = tags['genre']

        """
        logger.debug( "album \t: " + album )
        logger.debug( "lyrics \t: " + lyrics )
        logger.debug( "artist \t: " + artist )
        logger.debug( "track \t: " + track )
        logger.debug( "title \t: " + title )
        logger.debug( "albumImage \t: " + albumImage )
        logger.debug( "year \t: " + year )
        logger.debug( "genre \t: " + genre )
        """

        if os.path.isfile(filePath):
            P.logger.debug("파일존재 확인"  + filePath)
            ext = filePath.split(".")[-1]

            if ext.upper() == "MP3":
                try:
                    audio = ID3(filePath)
                    audio.add(TALB(text=[album]))
                    audio.add(TIT2(text=[title]))
                    audio.add(TPE1(text=[artist]))
                    audio.add(TRCK(text=[track]))
                    audio.add(TYER(text=[year]))
                    audio.add(TCON(text=[genre]))
                    audio.add(USLT(text=lyrics, lang="kor", desc=""))
                    
                    from PIL import Image
                    import requests

                    coverFile = os.path.join(os.getcwd(), 'data', 'tmp', 'cover.jpg')
                    if os.path.isfile(coverFile):
                        os.remove(coverFile)

                    P.logger.debug("albumImage : %s " , albumImage)
                    res = requests.get(albumImage, stream=True)
                    
                    if "png".upper() in res.headers['Content-Type'].upper():
                        im = Image.open(res.raw)
                        bg = Image.new("RGB", im.size, (255,255,255))
                        bg.paste(im,im)
                        bg.save(coverFile)
                    else:
                        im = Image.open(res.raw)
                        im.save(coverFile)

                    audio.add(APIC(encoding=3, mime=res.headers['Content-Type'], type=3, desc=u'Cover', data=open(coverFile, 'rb').read()))

                    audio.save()
                except ID3NoHeaderError:
                    P.logger.debug("MP3 except")
                    audio = ID3()
                    audio.add(TALB(text=[album]))
                    audio.add(TIT2(text=[title]))
                    audio.add(TPE1(text=[artist]))
                    audio.add(TRCK(text=[track]))
                    audio.add(TYER(text=[year]))
                    audio.add(TCON(text=[genre]))
                    audio.add(USLT(text=[lyrics], lang="kor", desc=""))
                    from PIL import Image
                    import requests

                    coverFile = os.path.join(os.getcwd(), 'data', 'tmp', 'cover.jpg')
                    im = Image.open(requests.get(albumImage, stream=True).raw)

                    if os.path.isfile(coverFile):
                        os.remove(coverFile)
                    
                    im.save(coverFile)
                    audio.add(APIC(encoding=3, mime='image/jpg', type=3, desc=u'Cover', data=open(coverFile, 'rb').read()))


                    audio.save(filePath)

    def tagUpdate(self, req):

        P = self.P

        id = ""
        title = ""
        artist = ""
        album = ""
        
        if len( req['id'] ) > 0:
            id = int(req['id'])
        if len( req['title'] ) > 0:
            title = str(req['title'])
        if len( req['artist'] ) > 0:
            artist = str(req['artist'])
        if len( req['album'] ) > 0:
            album = str(req['album'])
        
        P.logger.debug('id : ' + str(id))
        P.logger.debug('title : ' + str(title))
        P.logger.debug('artist : ' + str(artist))
        P.logger.debug('album : ' + str(album))
        
        
        # entity = ModelItem.get(id)
        # filePath = entity.filePath
        # logger.debug("filePath : "  + filePath)
        # if os.path.isfile(filePath):
        #     logger.debug("파일존재 확인"  + filePath)
        #     ext = filePath.split(".")[-1]
        #     if ext.upper() == "MP3":
        #         try:
        #             tags = ID3(filePath)
        #             tags.add(TALB(text=[album]))
        #             tags.add(TIT2(text=[title]))
        #             tags.add(TPE1(text=[artist]))
        #             tags.save()
        #         except ID3NoHeaderError:
        #             logger.debug("MP3 except")
        #             tags = ID3()
        #             tags.add(TALB(text=[album]))
        #             tags.add(TIT2(text=[title]))
        #             tags.add(TPE1(text=[artist]))
        #             tags.save(filePath)
        #     if "M4A" == ext.upper() :
                
        #         tags = MP4(filePath)
        #         tags['\xa9nam'][0] = title
        #         tags['\xa9ART'][0] = artist
        #         tags['\xa9alb'][0] = album
        #         tags.save()
                
                
        #     if "FLAC" == ext.upper() :

        #         tags = FLAC(filePath)
        #         tags['title'] = str(title)
        #         tags['artist'] = str(artist)
        #         tags['album'] = str(album)
        #         tags.save()
                
        #     logger.debug("파일처리시작"  + filePath)
        #     LogicNormal.mp3FileProc(filePath)

        #     ModelItem.delete(id)
            
        #     ret = {}
        #     return ret
        # else:
        #     return   