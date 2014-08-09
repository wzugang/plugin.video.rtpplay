#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
 Author: enen92 

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
"""

import xbmc,xbmcgui,xbmcaddon,xbmcplugin,sys,os,re
from common_variables import *
from directory import *
from webutils import *
from utilities import *

def list_tv_shows(name,url):
	try:
		page_source = abrir_url(url)
	except:
		page_source = ''
		msgok('RTP Play','Não conseguiu abrir o site / Check your internet connection')
	if page_source:
		match=re.compile('href="(.+?)" title=".+?"><h3>(.+?)</h3>').findall(page_source)
		totalit= len(match)
		for urlsbase,titulo in match:
			titulo = title_clean_up(titulo)
			if selfAddon.getSetting('icon_plot') == 'true':
				try:
					html_source = abrir_url(base_url + urlsbase)
				except: html_source = ''
				if html_source:
					try: thumbnail=img_base_url + re.compile('src=(.+?)&amp').findall(html_source)[0]
					except: thumbnail=''
					sinopse=re.compile('<p class="Sinopse">(.+?)</span></p>').findall(html_source)
					if sinopse: information = { "Title": name,"plot": clean_html(title_clean_up(sinopse[0])) }
					else: information = { "Title": name,"plot":"Informação não disponível." }
				addprograma(titulo,base_url + urlsbase,10,thumbnail,totalit,information)
			else:
				information = { "Title": name,"plot":"Informação não disponível." }
				thumbnail = ''
				addprograma(titulo,base_url + urlsbase,10,thumbnail,totalit,information)
		xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
		setview('show-view')
	else:
		sys.exit(0)
		
def list_episodes(url,plot):
	prog_id=re.compile('http://www.rtp.pt/play/p(.+?)/').findall(url)
	if not prog_id: prog_id=re.compile('http://www.rtp.pt/play/browseprog/(.+?)/.+?/true').findall(url)
	page_num = re.compile('.+?/(\d+)/true').findall(url)
	if not page_num: current_page = '1'
	else: current_page = page_num[0]
	if ('recent.php' not in url) and ('type=popular' not in url) and ('procura?' not in url): url='http://www.rtp.pt/play/browseprog/' + prog_id[0] + '/' + current_page + '/true'
	else: pass
	try:
		source = abrir_url(url)
	except: source=''; msgok('RTP Play','Não conseguiu abrir o site / Check your internet connection')
	if source:
		match=re.compile('href="(.+?)"><img alt="(.+?)" src="(.+?)".+?<i class="date"><b>(.+?)</b>').findall(source)
		print match
		totalit = len(match)
		for urlsbase,titulo,thumbtmp,data in match:
			try:thumbnail=img_base_url + re.compile('src=(.+?)&amp').findall(thumbtmp)[0]
			except: thumbnail=''
			if not plot: plot = "Informação não disponível."
			information = { "Title": title_clean_up(titulo),"plot":plot,"aired":format_data(data) }
			addepisode('[B]' + title_clean_up(titulo) + '[COLOR blue] (' + data +')' + '[/B][/COLOR]',base_url + urlsbase,11,thumbnail,totalit,information)
		pag_num_total=re.compile('.*page:(.+?)}\)\">Fim &raquo').findall(source)
		if pag_num_total:
			try:
				if int(current_page) == int(pag_num_total[0]): pass
				else: 
					url_next='http://www.rtp.pt/play/browseprog/' + prog_id[0] + '/' + str(int(current_page)+1) + '/true'
					addDir('[B][COLOR blue]Pág ('+current_page+'/'+pag_num_total[0]+')[/B][/COLOR] | Próxima >>',url_next,10,'',1,pasta=True)
			except: pass
	xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
	setview('episodes-view')
	
def list_emissoes(urltmp):
	#Block of code to detect current page number
	page_num = re.compile('&page=(\d+)').findall(urltmp)
	if not page_num: page_num = str(1)
	else: page_num=page_num[0]
	url= urltmp + '&page=' + page_num
	try:
		page_source = abrir_url(url)
	except:
		page_source = ''	
		msgok('RTP Play','Não conseguiu abrir o site / Check your internet connection')
	if page_source:
		pag_num_total=re.compile('.*page=(.+?)">Fim &raquo').findall(page_source)
		html_source_trunk = re.findall('<div class="item">(.*?)<p class=', page_source, re.DOTALL)
		if html_source_trunk:
			for trunk in html_source_trunk:
				match=re.compile('<a href="(.+?)" title="(.+?), Ep.+? de (.+?)">\s*<img alt=".+?" src="(.+?)"').findall(trunk)
				totalit = len(match)
 				for urlsbase,titulo,data,thumbtmp in match:
 					try:
						thumbtmp2=re.compile('src=(.+?)&amp').findall(thumbtmp)
						thumbnail=img_base_url + thumbtmp2[0]
						titulo = title_clean_up(titulo)
						plot = re.compile('<p>(.+?)</p').findall(trunk)
						if plot: plot = title_clean_up(plot[0])
						else: plot = "Informação não disponível."
						data = format_data(data)
						information = { "Title": titulo,"Plot":plot,"aired":data }
						addepisode('[B]' + titulo + '[COLOR blue] (' + data +')' + '[/B][/COLOR]',base_url + urlsbase,11,thumbnail,totalit,information)
					except: pass
			if pag_num_total:
				page_next = int(page_num)+1
				match = re.compile('&page=(\d+)').findall(urltmp)
				if match: urltmp = urltmp.replace('&page='+match[0],'')
				url=urltmp + '&page=' + str(page_next)
				addDir('[B]Pag '+ page_num + '/' + pag_num_total[0] + '[/B][B][COLOR blue] | Seguinte >>[/B][/COLOR]',url,19,'',1)
			else: pass
			xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
			setview('episodes-view')
		else: msgok('RTP Play','Não há emissões');sys.exit(0)
	else:
		sys.exit(0)
		
def list_show_search(url):
	try:
		page_source = abrir_url(url)
	except:
		page_source = ''	
		msgok('RTP Play','Não conseguiu abrir o site / Check your internet connection')
	if page_source:
		match = re.compile('<a href="(.+?)" title=".+?"><h3>(.+?)</h3>').findall(page_source)
		for urlsbase,titulo in match:
			pass
	
	
	
		
def pesquisa_emissoes():
	keyb = xbmc.Keyboard('', 'Escreva o parâmetro de pesquisa')
	keyb.doModal()
	if (keyb.isConfirmed()):
		search = keyb.getText()
		encode=urllib.quote(search)
		urltmp = base_url + '/play/procura?p_az=&p_c=&p_t=&p_d=&p_n=' + encode + '&pesquisar=OK'
		list_emissoes(urltmp)
		
def pesquisa_programas():
	keyb = xbmc.Keyboard('', 'Escreva o parâmetro de pesquisa')
	keyb.doModal()
	if (keyb.isConfirmed()):
		search = keyb.getText()
		encode=urllib.quote(search)
		urltmp = base_url + '/play/procura?p_az=&p_c=&p_t=&p_d=&p_n=' + encode + '&pesquisar=OK'
		list_show_search(urltmp) 
		
		
		

