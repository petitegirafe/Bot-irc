#!/usr/bin/env python 
# -*- coding: utf-8 -*-



import socket, time, sys, string, re 

PORT = 	6667
server = "irc.root-me.org" # Ou autres 
channel = "#testBot" # nom du channel ou se connecter
botnick = "hackuza" # nom donné au bot 
# speudo des administrateurs pour pouvoir controler le bot 
adminBot = ["petitegirafe", "AUtreAdmin", "admin"] 

normal, jaune, rouge, vert, magenta = '\033[0m', '\033[33m', '\033[31m', '\033[32m', '\033[35m'

class IrcBot:
	# On Initialise maintenant notre Class :
	def __init__(self):
		# creation du socket
		self.ircsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#connection du socket
		self.ircsocket.connect((server, PORT))
		# Renseignement nom du bot  
		self.ircsocket.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " bot\n"))
		self.ircsocket.send(bytes("NICK " + botnick + "\n"))
		
		self.mainBot() #on lance la fonction principale main bot elle contient notre boucle principal d'événements
		

	# Notre fonction qui sert à joindre le channel.
	def jointChannel(self):
		# fonction pour joindre le channel IRC
		ircmsg = ""
		time.sleep(1) # Time sleep 1 seconde sinon bug à la connection 
		# On joint notre channel
		self.ircsocket.send(bytes("JOIN "+ channel +"\n"))
		print "Connection on {}  ".format(channel)
		# On créer une boucle pour récuperer la liste de toute les perconnes connectés sur le channel 
		while ircmsg.find("End of /NAMES list.") == -1:
			ircmsg = self.ircsocket.recv(2048)
			print(ircmsg).strip('\n\r')# affichage pseudo 
			
	# check la commande pour appeller la fonction adéquat		
	def check_common(self, usr_common,  message, channel):
		message = message[len(usr_common):]
		if usr_common == ":!rot13":
			self.on_rot13(message ,channel)	
		if usr_common == ":!rot47":	
			self.on_rot47(message ,channel)
	
			
	def ping(self):# repond au ping pour ne pas être déconecté
		self.ircsocket.send(bytes("PONG :pong\n"))
		
	def on_rot13(self, message, channel):
		rot13Table = string.maketrans("ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
		                              "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
		message =  message.translate(rot13Table)
		self.ircsocket.send(bytes("PRIVMSG " + channel + " : " + message.strip() + '\n'))
		print(magenta +'['+ botnick +'][rot13]:'+ normal + message)
		
	def on_rot47(self, message, channel):
		rot47Table = string.maketrans('!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~',
		            				'PQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNO')
		message =  message.translate(rot47Table)
		self.ircsocket.send(bytes("PRIVMSG " + channel + " : " + message.strip() + '\n'))
		print(magenta +'['+ botnick +'][rot47]:'+ normal + message)	
		
		
	# Fonction qui va déterminer si le message est privé ou public	
	def mode_message(self, name, message, channel):
		# Si le nom du bot est égale à la premiére partie du message (message privé au bot)
		if botnick == message[1:len(botnick)+1]:
			# Appelle fonction message privé on lui envoie le name de l'envoyeur le message et le channel  
			self.on_privmsg(name, message[len(botnick)+2:], channel)
		# Si le message est envoyé sur le canal public
		if channel == message[1:len(channel)+1].strip():
			# Appelle à la fonction message public 
			self.on_pubmsg(name, message[len(channel)+2:], channel)	
			
			
	# Admin bot administrer le bot 		
	def on_adminBot(self, name, message, channel):
		if re.match(r"^:![a-zA-Z0-9_]+", message):
			adm_common = message.split()[0]
			message = message[len(adm_common):] 
			if adm_common == ":!print":
				# si print in commande le bot j'envoie ce que l'on lui à ecrie dans le canal public
				print(rouge +'[Privé]:'+ normal  + jaune + name + ":"+ normal + "!print --> "+ message.strip()) 
				print(vert +'[Public]:'+ normal  + jaune + botnick + ":"+ normal + message.strip())
				self.ircsocket.send(bytes("PRIVMSG " + channel + " " + message.strip() + '\n'))
			if adm_common == ":!exit":
				# Si la commande est "exit(" le bot dit aurevoir et ce deconnect
				print(rouge +'[Privé]:'+ normal  + jaune + name + ":"+ normal + "!exit ")
				print(vert +'[Public]:'+ normal  + jaune + botnick + ":"+ normal + "Bye all !!!")
				self.ircsocket.send(bytes("PRIVMSG " + channel + " : Bye all !!!\n"))
				self.ircsocket.send(bytes("QUIT \n"))#deconnection
				sys.exit()# fin du programme
		else:# Sinon il recrie se que l'on à écrie dans le terminal
			print(rouge +'[Privé ]:'+ normal + jaune + name +":"+ normal + message)
			
					
	# Fonction appellée quand le bot reçoit un message privé	
	def on_privmsg(self, name, message,channel):
		if name.strip() in adminBot:# Si le nom fait partie de la liste des admin
			# Appel à la fonction admin bot
			self.on_adminBot(name, message, channel)
			pass
		else : # Sinon
			print(rouge +'[Privé]:'+ normal + jaune + name + normal +": " + message)
			# On envoi le message ho je suis un bot à l'envoyeur
			self.ircsocket.send(bytes("PRIVMSG " + name + " :Ho !!! je suis un bot !!! \n"))
			
			
	# Fonction appellée quand le message est public
	def on_pubmsg(self, name, message, channel):
		if re.match(r"^:![a-zA-Z0-9_]+", message): # Si la ligne commence bien par :! 
			usr_common = message.split()[0]
			print(vert +'[Public]:' + normal + jaune + name +normal+ message.strip())
			self.check_common(usr_common, message, channel)
			pass
		else:# Sinon
			print(vert +'[Public]:'+ normal + jaune + name + normal + message.strip())#on affiche seulement le message dans le terminal
						
				
	# Notre fonction principal , elle contiendra notre boucle principal d'événements .
	def mainBot(self):
		self.jointChannel() # On joint le channel 
		# On lance notre boucle d'événements
		while 1 :
			# récuperation message par le socket
			ircmsg = self.ircsocket.recv(2048)
			
			# Si le message comporte PRIVMSG (message privée ou public sur le channel)
			if "PRIVMSG" in ircmsg :
				# On coupe le message pour récuperer le nom de celui qui l'envoi 
				name = ircmsg.split('!')[0][1:].rstrip()#on coupe point d'exclamation et on garde la premiére partie moins le premier caractère(:)
				message = ircmsg.split('PRIVMSG')[1]#on récupère toute la partie aprés le type du message (privée ou pas plus le message)
				# Appel de la fonction qui définie si c'est un message public ou privé
				self.mode_message(name, message.rstrip('\n'), channel)# on lui envoie le name ,le message et le channel

			# Si le message contient PING On appelle la fonction ping pour ne pas être déconnecté  	
			if ircmsg.find("PING :") != -1:
				self.ping()


if __name__ == "__main__":
	IrcBot().start()
	
	
	
