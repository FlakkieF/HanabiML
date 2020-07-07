# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 13:31:55 2020

@author: Freek
"""
import os
import random



##Ik gebruik 'Speler' als ik praat over de menselijke speler 
#en 'speler' als ik het over een speler heb, dus zowel de AI als de menselijke speler 




#Leest een file en returned een lijst met elke regel van die file
def FiletoList(filenaam):
    lijst = [line.rstrip('\n') for line in open(filenaam)]
    return lijst 

#check of de log van iemands eerste potje is door te kijken of bestand met een O van Old Git begint.
def IsEersteSpel(loglijst):
    if loglijst[0][0] == "O":
        return False
    else:
        return True

##Check of eerste move van AI Discard is, door te kijken naar de eerste MOVE: regel.
##Waar de eerste MOVE regel zit is afhankelijk van of het iemands eerste potje is of niet 
def EersteMoveIsDiscard(loglijst):
    if IsEersteSpel(loglijst):
        i = 2
    else:
        i = 3
    zin = MaakLijstVanZin(loglijst[i])
    if zin[2] == "3":
        return True
    else:
        return False

##Check of 2e move van AI discard is, door te kijken naar de eerste MOVE: regel en of het iemands eerste potje is  
def TweedeMoveIsDiscard(loglijst):
    Eerste = False
    if IsEersteSpel(loglijst):
        i = 5
        Eerste = True
    else:
        i = 6
        
    if Eerste:
        if EersteMoveIsDiscard(loglijst):
            i = 6
        else:
            i = 5
    else: 
        if EersteMoveIsDiscard(loglijst):
            i = 7
        else:
            i = 6
            
    zin = MaakLijstVanZin(loglijst[i])
    if zin[2] == "3":
        return True
    else:
        return False



#Maakt een lijst van kaarten die nog in de stapel zitten. De kaarten zijn tuples. De eerste kaart ligt bovenop de stapel
def maaklijstvantuples(loglijst):
    tupleplaats = 0
    i = 0
    eerste = 0
    tweede = 0
    detuple = ()
    tuplelijst = []
    if IsEersteSpel(loglijst):
        i = 1
    else:
        i = 2
    for x in loglijst[i]:
        if x.isdigit():
            if tupleplaats == 0:
                eerste = int(x)
                tupleplaats = 1
                continue
            if tupleplaats == 1:
                tweede = int(x)
                tupleplaats = 0
                detuple = (eerste, tweede)
            tuplelijst.append(detuple)
    return tuplelijst

#kleurenlijsten
KLeurenlijst1 = [0,1,2,3,4]


#Maak een lijst met 25 tuples, Elke tuples is een kaart: [(0,1),(0,2)....(4,4),(4,5)]
#kleurenlijst is in alle functies (behalve kleurnaargetal) een lijst met de volgorde van kleuren
#Dit had ik bedacht als manier om later de kleuren te kunnen wisselen
def MaakLijstAlleKaarten(kleurenlijst):
    nummers = [1,2,3,4,5]
    allekaarten = []
    for kleur in kleurenlijst:
        for nummer in nummers:
            allekaarten.append((kleur, nummer))
    ##print("allekaarten: ", allekaarten)
    return allekaarten





#Gebruikt lijst van allekaarten en maakt lijst van 25 tuples: eerste element is een kaart, 2e element is hoeveel van
    #die kaart er in het spel zitten.
def MaakMindState(kleurenlijst):
    mind = []
    allekaarten = MaakLijstAlleKaarten(kleurenlijst)
    for kaart in allekaarten:
        if((kaart[1]) == 1):
                mind.append((kaart, 3))
        if((kaart[1]) == 2):
                mind.append((kaart, 2))
        if((kaart[1]) == 3):
                mind.append((kaart, 2))
        if((kaart[1]) == 4):
                mind.append((kaart, 2))
        if((kaart[1]) == 5):
                mind.append((kaart, 1))
    return mind



##Maakt een lijst van 25 tuples, eerste element is een kaart, 2e element een 0,
 #omdat er nog geen kaarten zijn gespeeld aan het begin van een spel. 
def OpTafelRepresentatie(kleurenlijst):
    optafel = []
    allekaarten = MaakLijstAlleKaarten(kleurenlijst)
    for kaart in allekaarten:
       optafel.append((kaart, 0))
    return optafel




#Dit is de map waar alle logs staan
basepath = 'C:\Users\Freek\Documents\AAA uni\Hanabi\pyhanabi-master\log'


#maak file1 aan: 1 van de logs
file1 = os.listdir(basepath)[34]
print("de file: ", file1)

#maak vantextfile een lijst, waarvan de elementen alle regels van de log zijn
loglijst = FiletoList(file1)


#Deze Functie geeft de naam van de AI waartegen wordt gespeeld
def GetNaamAI(loglijst):
    if IsEersteSpel(loglijst):
        zin = loglijst[3]
    else:
        zin = loglijst[4]
    zin = MaakLijstVanZin(zin)
    naam = zin[0]
    
    return naam


#def MindNieuweKaartSpeler(kleurenlijst, Mind, kaartwegplek, nieuwekaart):
#    kaartwegplek = int(kaartwegplek)
#    teller = kaartwegplek + 1
#    for mindkaart in Mind[teller:]:
#        if teller == 5:
#            Mindnieuw = MaakMindSpeler(kleurenlijst)
#            Mindnieuw = UpdateMindSpeler(kleurenlijst, Mindnieuw, nieuwekaart)
#            Mind[teller] = Mindnieuw
#            Mind[0][teller - 1] = nieuwekaart
#        else:
#            Mind[teller] = Mind[(teller+1)]
#            Mind[0][teller - 1] = Mind[0][teller]
#            teller += 1
#    return Mind



#Deze functie maakt van een regel van de log een lijst van de woorden in die regel. De woorden zijn strings
# "MOVE: 1 2 3 1 None None",  wordt ["Move:", "1"..."None", "Nonce"]
def MaakLijstVanZin(zin):
    string = ""
    stringlijst = []
    for x in zin:
        if x == " ":
            stringlijst.append(string)
            string = ""
        elif x == ",":
            continue
        else:
            string = string+x
    stringlijst.append(string)
    return stringlijst
    





#Deze functie wordt gebruikt om de juiste kaart te maken (tuple) van een kaart-string.
##hier was ik nog niet consisten met kleurenlijst: 'dekleuren' is hier de lijst met getallen die kleuren representeren
#kleurenlijst  is hier een lijst met tuples waarvan het eerste element een string is met een kleur 
#Bijvoorbeeld: input, kleurenlijst = [("green","1"), ("red","4")...("white","5")], de kleuren = [0,1,2,3,4]
#             output: [(0,1),(4,4)...(2,5)]
def KleurNaarGetal(kleurenlijst, dekleuren):
    kaartenlijst = []
    for x,y in kleurenlijst:
        if x == "green":
            x = dekleuren[0];
        if x == "yellow":
            x = dekleuren[1];
        if x == "white":
            x = dekleuren[2];
        if x == "blue":
            x = dekleuren[3];
        if x == "red":
            x = dekleuren[4];
        kaartenlijst.append((x,int(y)))
    return kaartenlijst




##functie om aan de hand van 3 regels in log te reconstrueren welke kaarten de speler
##daarvoor in zijn hand had. Dit is nodig om in bepaalde gevallen de eerste 5 kaarten van de speler of de AI te achterhalen
#De regels die deze functie nodig heeft, zijn welke kaart er is gespeeld, de MOVE-zin die beschrijft welke actie er is gedaan
#en de regel die beschrijft welke kaarten de speler die de actie deed erna in zijn hand heeft
def ReconstrueerDeHand(kleurenlijst, kaart, movezin, handenzin):
    handenzin = MaakLijstVanZin(handenzin)
    movezin = MaakLijstVanZin(movezin)
    
    
    #print "move", movezin
    #print "hand", handenzin
    
    tuplelijst = []
    detuple = ()
    eerste = ""
    tweede = 0
    
    #deze forloop wordt gebruikt om van de zin een lijst te maken met tuples die kaarten voorstellen. (kaarten zijn nog strings)
    for y in handenzin:
        if y == "blue" or y == "red" or y == "green" or y == "yellow" or y == "white":
            eerste = y
        if y.isdigit():
            tweede = int(y)
            detuple = (eerste, tweede)
            tuplelijst.append(detuple)
    
            
    HandNaDis = KleurNaarGetal(tuplelijst, kleurenlijst)
    
    #kopieer de hand na de actie
    HandVoorDis = list(HandNaDis)
    
    #plek is welke kaart in de hand is gespeeld
    plek = int(movezin[3])
    HandVoorDis[plek] = kaart
    
    #zet de gespeelde kaart terug in de hand en zet de andere kaarten op de goede plek
    #de vijfde kaart in de hand, gaat hierdoor weg
    teller = plek
    for x in HandNaDis[teller:]:
        if teller == 4:
            break
        else:
            HandVoorDis[teller+1] = x
            teller += 1
    return HandVoorDis
    
    
##Achterhaal wat de 5 beginkaarten zijn van de speler door de juiste regels van de log te lezen.
##De regel met de 5 kaarten van de speler staat niet altijd op dezelfde plek, want het is ook afhankelijk van wat de eerste actie van de AI is.
##Als de eerste actie van een AI is dat hij een kaart discard, en de eerste actie van de speler is dat hij een kaart speelt of discard,
##dan is de enige manier om achter de eerste 5 kaarten te komen, door de hand te reconstrueren.
    
#Deze functie zoekt naar de eerste regel waarvan het eerste woord "YOU" is.
#Van die regel kijkt hij naar het 2e woord. Als dit woord "plays of discards" is, dan wordt de hand gereconstrueerd
#                                           Als dit woord "hints" is, dan gebeurt er niks met de kaarten van YOU, dus 
#                                             dan zoeken we verder
#                                           Als het niet een van bovenstaande is, dan beschrijft deze regel welke kaarten 
#                                             YOU in zijn hand heeft en heeft YOU daarvoor nog niks met zijn kaarten gedaan
def KaartenVanYouGoed(loglijst, kleurenlijst):
    teller = 0
    for zin in loglijst:
        zin = MaakLijstVanZin(zin)
        if zin[0] == "You":
            if zin[1] == "discards":
                #print "you discards is eerst"
                kaartlijst = KleurNaarGetal([(zin[2],zin[3])], kleurenlijst)
                #print "kaart", kaartlijst[0]
                result = ReconstrueerDeHand(kleurenlijst, kaartlijst[0], loglijst[teller - 1], loglijst[teller+2])
                #print "dit moet 'You' zijn ", zin[0]
                #print result
                return result
            elif zin[1] == "hints":
                teller += 1
                continue
            elif zin[1] == "plays":
                kaartlijst = KleurNaarGetal([(zin[2],zin[3])], kleurenlijst)
                result = ReconstrueerDeHand(kleurenlijst, kaartlijst[0], loglijst[teller - 1], loglijst[teller+1])
                return result
            else:
                tuplelijst = []
                detuple = ()
                eerste = ""
                tweede = 0
                for y in zin:
                    if y == "blue" or y == "red" or y == "green" or y == "yellow" or y == "white":
                        eerste = y
                    if y.isdigit():
                        tweede = int(y)
                        detuple = (eerste, tweede)
                        tuplelijst.append(detuple)
                result = KleurNaarGetal(tuplelijst, kleurenlijst)
                #print "dit moet 'You' zijn ", zin[0]
                #print result
                return result
        else:
            teller += 1





##Zie: uitleg KaartenvanSpelerGoed,
# de eerste actie van de AI kan nooit 'plays' zijn, want de AI mag altijd als eerst en de AI speelt geen kaart 
#als hij niet zeker weet dat die kaart gespeeld kan worden
def KaartenvanAIGoed(loglijst, kleurenlijst, naamAI):
    teller = 0
    for zin in loglijst:
        zin = MaakLijstVanZin(zin)
        if zin[0] == naamAI:
            if zin[1] == "discards":
                #print naamAI, "discards eerst"
                kaartlijst = KleurNaarGetal([(zin[2],zin[3])], kleurenlijst)
                #print "kaart", kaartlijst[0]
                result = ReconstrueerDeHand(kleurenlijst, kaartlijst[0], loglijst[teller - 1], loglijst[teller+2])
                #print "dit moet", naamAI, "zijn ", zin[0]
                #print result
                return result
            elif zin[1] == "hints":
                teller += 1
                continue
            else:
                tuplelijst = []
                detuple = ()
                eerste = ""
                tweede = 0
                for y in zin:
                    if y == "blue" or y == "red" or y == "green" or y == "yellow" or y == "white":
                        eerste = y
                    if y.isdigit():
                        tweede = int(y)
                        detuple = (eerste, tweede)
                        tuplelijst.append(detuple)
                result = KleurNaarGetal(tuplelijst, kleurenlijst)
                #print "dit moet", naamAI, "zijn ", zin[0]
                #print result
                return result
        else:
            teller += 1


##
##test om te kijken of de 2 bovenstaande functies goed werken
##            
            
#allefiles = os.listdir(basepath)
#delog = allefiles[24]
#print delog
#delog = FiletoList(delog)

#resultgoed = KaartenVanYouGoed(delog, [0,1,2,3,4])
#resultslecht = KaartenVanYou(delog, [0,1,2,3,4])

#print "KaartenVanYouGoed", resultgoed
#print "KaartenVanYouSlecht", resultslecht
            
#naam = GetNaamAI(delog)
#print naam

#resultgoedAI = KaartenvanAIGoed(delog, [0,1,2,3,4], naam)
#resultslechtAI = KaartenvanAI(delog, [0,1,2,3,4])

#print "resultgoed AI = ", resultgoedAI
#print "resultslecht AI = ", resultslechtAI
            
            
##
##
##
            
            

        


##mindstate behoort bij plek in hand

#Maak ee representatie voor wat de AI of een Speler weet van een bepaalde kaart aan.
#Op het begin is elke kaart nog mogelijk, dus elke kaart krijgt een 1.
def MaakMind(kleurenlijst):
    result = []
    allekaarten = MaakLijstAlleKaarten(kleurenlijst)
    for kaart in allekaarten:
        result.append((kaart, 1))
    return result


#functie die de Mind aanpast aan welke hint er is gegeven.
#Mindkaart is de representatie van de kaart waarover een hint is gegeven.
# als de hint ervoor zorgt dat een kaart-mogelijkheid niet meer kan, dan wordt de 1 een 0.
## returned aangepaste Mind
def UpdateMindHint(kleurenlijst, MindKaart, KleurHint, NummerHint):
    result = []
    #print("MindAI", MindAI)
    if KleurHint != "None":
        for kaart, nogmogelijk in MindKaart:
            if kaart[0] != int(KleurHint):
                nogmogelijk = 0
            result.append((kaart, nogmogelijk)) 
        return result
    teller = 1
    if NummerHint != "None":
        for kaart, nogmogelijk in MindKaart:
            if kaart[1] != int(NummerHint):
                nogmogelijk = 0
                teller += 1
            result.append((kaart, nogmogelijk))
        return result
    


#Maak een lijst die de mindstate van een speler representeert.
#Het eerste element van de lijst is een lijst met wat de speler al weet van de kaarten.
#Bijv: als de speler weet dat zijn derde kaart rood is: [(0,0),(0,0),(4,0),(0,0),(0,0)]
#De volgende 5 elementen zijn elk, representatie voor 1 kaart en wat de speler van die kaart weet
#Deze functie wordt alleen op het begin van elk spel aangeroepen
def InitializeMind(kleurenlijst):
    Kaarten = [(0,0),(0,0),(0,0),(0,0),(0,0)]
    OneMind = []
    FiveMinds= []
    FiveMinds.append(Kaarten)
    for kaart in Kaarten:
        OneMind = MaakMind(kleurenlijst)
        FiveMinds.append(OneMind)
    return FiveMinds

##Deze functie past de mindrespresentatie van een speler aan als deze speler een kaart heeft gespeeld
##Kaarten in de hand worden opgeschoven en er komt een nieuwe kaart bij, dus de minds moeten hetzelfde doen.
def MindNieuweKaart(kleurenlijst, Mind, kaartwegplek):
    kaartwegplek = int(kaartwegplek)
    
    #Deze loop past schuift elke mindrepresentatie, na de gespeelde kaart 1 naar links
    #en zet op de laatste plaats een nieuwe mindrespresentatie, voor de nieuwe kaart in de hand van de speler
    teller = kaartwegplek + 1
    # +1, omdat het eerste element van MIND de lijst van kaarten is
    for mindkaart in Mind[teller:]:
        if teller == 5:
            Mind[teller] = MaakMind(kleurenlijst)
            Mind[0][teller - 1] = (0,0)
        else:
            Mind[teller] = Mind[(teller+1)]
            Mind[0][teller - 1] = Mind[0][teller]
            teller += 1
    return Mind



#Deze functie past de kaarten van een speler aan als deze een kaart heeft gespeeld
###Kaarten in de hand worden opgeschoven en er komt een nieuwe kaart bij
def NieuweKaart(kleurenlijst, kaarten, kaartwegplek, nieuwekaart):
    teller = kaartwegplek
    for kaart in kaarten[kaartwegplek:]:
        if teller == 4:
            kaarten[teller] = nieuwekaart
        else:
            kaarten[teller] = kaarten[teller + 1]
            teller += 1
    return kaarten

#Deze functie past de Knowledge van de AI aan.
#De Knowledge houdt bij welke kaarten er al gespeeld en discard zijn
#Als een kaart is gespeeld dan wordt het nummer dat bij die kaart hoort in knowledge 1 minder.
#Bijv: Eerst ((2,3),2) ....speler speelt (2,3)... nu ((2,3),1)
def UpdateKnowledge(kleurenlijst, Knowledge, dekaart):
    teller = 0
    #if count == 24:
        #print Knowledge
        #print dekaart
    for kaart, hoeveelheid in Knowledge:
        if kaart == dekaart:
            hoeveelheid = hoeveelheid - 1
            break
        else:
            teller += 1
    Knowledge[teller] = (kaart, hoeveelheid)
    return Knowledge



#Test bovenstaande functie
    
#tafel = UpdateTafel(kleuren, loglijst[10], [(0,0),(1,0),(2,0),(3,0),(4,0)])
#print tafel
    


#Deze functie past aan welke kaarten er momenteel op tafel liggen als een kaart succesvol is gespeeld
#Bijv: Eerst [(0,0),(1,1),(2,3),(3,0),(4,2)]...kaart 0,1 wordt succesvol gespeeld....Nu: [(0,1),(1,1),(2,3),(3,0),(4,2)]
def UpdateTafel(kleurenlijst, Playzin, oudetafel):
    kaart = (Playzin[2], int(Playzin[3]))
    kaartlijst = [kaart]
    lijst = KleurNaarGetal(kaartlijst, kleurenlijst)
    plek = 0
    #print "oudetafel", oudetafel
    for x,y in oudetafel:
        if x == lijst[0][0]:
            y += 1
            oudetafel[plek] = (x,y)
            break
        else:
            plek += 1
    return oudetafel

##deze functie past de representatie van de kaarten die succesvol gespeeld zijn bij.
##Als een kaart succesvol is gespeeld dan wordt het nummer bij die kaart 1.
#Bijv: Eerst ((2,3),0) ....speler speelt (2,3) succesvol... nu ((2,3),1)
def UpdateTafelRepresentatie(kleurenlijst, Playzin,tafelrepresentatie, kaart):
    plek = 0
    for x,y in tafelrepresentatie:
        if x == kaart:
            y = 1
            tafelrepresentatie[plek] = (x,y)
            break
        else:
            plek += 1
    return tafelrepresentatie
    



    
          
#Knowledge = MaakMindState([0,1,2,3,4])
#KnowledgeNieuw = UpdateKnowledge(kleuren, Knowledge, (1,3))



#In Deze functie wordt elke beurt gesimuleert.
#Welke actie wordt gedaan staat in MoveZin en in Gevolgenzin staat de situatie nadat die actie is gedaan.
#Met de rest van de argumenten wordt de situatie bijgehouden en deels worden deze gebruikt om uiteindelijk de input te bouwen
#Ik heb in de functie bij alles gezet wat er precies wordt gedaan

#Deze functie returned een lijst genaamd situatie, waarin alle benodigde informatie staat.
#Deze informatie is of nodig om input te maken, of om de status van het spel goed bij te kunnen houden (of allebei)
#Aan het begin van de functie wordt de lijst 'situatie' aangemaakt en in de rest van de functiewordt de lijst steeds aangepast waar nodig

def HandleTurn(kleurenlijst, MoveZin, GevolgenZin, Knowledge, MindAI, MindSpeler, tokens, fuses, aantalkaarten, stapelkaarten, kaartenAI, kaartenSpeler, Tafelsituatie, TafelRep):
    situatie = [Knowledge, MindAI, MindSpeler, tokens, fuses, aantalkaarten, stapelkaarten, kaartenAI, kaartenSpeler,Tafelsituatie, TafelRep]
    

    zin = MaakLijstVanZin(MoveZin)
    GevolgenZin = MaakLijstVanZin(GevolgenZin)
    


    #AI heeft iets gedaan
    if zin[1] == "0":
        
        
        # AI geeft hint
        if zin[2] == "0" or zin[2] == "1":
            
            # -1 token
            tokens -= 1
            situatie[3] = tokens
            
            
            #bepaal over welke kaarten hint gaat
            kaartplekken = []
            plek = 0
            
            ##hint over kleur
            if zin[5] != "None":
                for x,y in kaartenSpeler:
                    if x == zin[5]:
                        kaartplekken.append(plek)
                        plek += 1
                    else:
                        plek += 1
                #pas kaarten aand in mind[0] voor duidelijkheid
                for plek in kaartplekken:
                    teller = 0
                    for x,y in MindSpeler[0]:
                        if teller == plek:
                            MindSpeler[0][teller] = (int( zin[5]),y)
                            teller += 1
                        else:
                            teller += 1
            
            ##hint over nummer
            if zin[6] != "None":
                
                for x,y in kaartenSpeler:
                    if y == int(zin[6]):
                        kaartplekken.append(plek)
                        plek += 1
                    else:
                        plek += 1
                
                #pas kaarten aand in mind[0] voor duidelijkheid
                for plek in kaartplekken:
                    teller = 0
                    for x,y in MindSpeler[0]:
                        if teller == plek:
                            MindSpeler[0][teller] = (x,int(zin[6]))
                            teller += 1
                        else:
                            teller += 1
            
            #info opnemen in mindstate over kaarten AI
            for plek in kaartplekken:
                MindSpeler[plek+1] = UpdateMindHint(kleurenlijst, MindSpeler[plek+1], zin[5], zin[6])
            situatie[2] = MindSpeler
             
            
        
            
        #Ai speelt of discard een kaart
        if zin[2] == "2" or zin[2] == "3":
            #knowledge verandert, want kaart is weg
            kaartplek = zin[3]
            kaartplek = int(kaartplek)
            #if count == 424:
                #print "plek", kaartplek
                #print "AI", kaartenAI
            dekaart = kaartenAI[kaartplek]
            Knowledge = UpdateKnowledge(kleurenlijst, Knowledge, dekaart)
            situatie[0] = Knowledge
            
            #krijg nieuwe kaart
            if len(stapelkaarten) != 0:
                MindAI  = MindNieuweKaart(kleurenlijst, MindAI, kaartplek)
            ##MindAI[0][4] = (0,0)
            situatie[1] = MindAI
            
            #print GevolgenZin
            #was een gespeelde kaart juist?
            if GevolgenZin[1] == "plays":
                if GevolgenZin[5] == "fails.":
                    fuses -= 1
                    situatie[4] = fuses
                #wel succesvol? update tafel
                else:
                    #update tafel
                    #print "oudetafel", Tafelsituatie
                    #print "GevolgenZin", GevolgenZin
                    nieuwetafel = UpdateTafel(kleurenlijst, GevolgenZin, Tafelsituatie)
                    #print "Nieuwetafel", nieuwetafel
                    #print "TafelRep, ", TafelRep
                    #print "de kaart ", dekaart
                    situatie[9] = nieuwetafel
                    TafelRep = UpdateTafelRepresentatie(kleurenlijst, GevolgenZin, TafelRep, dekaart)
                    situatie[10] = TafelRep
                    
                    
                    #als vuurwerk compleet: bonus Hint token
                    if dekaart[1] == 5 and tokens < 8:
                        tokens += 1
                        situatie[3] = tokens
                    
            
            #krijg nieuwe kaart van stapel
            if len(stapelkaarten) != 0:
                kaartenAI = NieuweKaart(kleurenlijst, kaartenAI, kaartplek, stapelkaarten[0])
                situatie[7] = kaartenAI
                aantalkaarten -= 1
                situatie[5] = aantalkaarten
                stapelkaarten.pop(0)
                situatie[6] = stapelkaarten
            
            
        
        #AI discard actie is alleen anders dan speel actie voor tokenaantal
        if zin[2] == "3":
            #token erbij
            if tokens < 8:
                tokens += 1
                situatie[3] = tokens
        
        
        
        
    #speler heeft iets gedaan
    #print(zin[1])
    if zin[1] == "1":
        
        
        
        #print("dit gebeurt?")
        if zin[2] == "0" or zin[2] == "1":
            
            # -1 token
            tokens -= 1
            situatie[3] = tokens
            
            #bepaal over welke kaarten hint gaat
            kaartplekken = []
            plek = 0
            
            ##hint over kleur
            if zin[5] != "None":
                for x,y in kaartenAI:
                    if x == zin[5]:
                        kaartplekken.append(plek)
                        plek += 1
                    else:
                        plek += 1
                #pas kaarten aand in mind[0] voor duidelijkheid
                for plek in kaartplekken:
                    teller = 0
                    for x,y in MindAI[0]:
                        if teller == plek:
                            MindAI[0][teller] = (int( zin[5]),y)
                            teller += 1
                        else:
                            teller += 1
            
            
            ##hint over nummer
            if zin[6] != "None":
                
                for x,y in kaartenAI:
                    if y == int(zin[6]):
                        kaartplekken.append(plek)
                        plek += 1
                    else:
                        plek += 1
                
                #pas kaarten aand in mind[0] voor duidelijkheid
                for plek in kaartplekken:
                    teller = 0
                    for x,y in MindAI[0]:
                        if teller == plek:
                            MindAI[0][teller] = (x,int(zin[6]))
                            teller += 1
                        else:
                            teller += 1
            
            #info opnemen in mindstate over kaarten AI
            for plek in kaartplekken:
                MindAI[plek+1] = UpdateMindHint(kleurenlijst, MindAI[plek+1], zin[5], zin[6])
            situatie[1] = MindAI
            
            

        #speler speelt of discard
        if zin[2] == "2" or zin[2] == "3":
            
            
            kaartplek = zin[3]
            kaartplek = int(kaartplek)
            
            
            #de kaart die is gespeeld of is discard
            oudekaart = kaartenSpeler[kaartplek]
            
            ##update knowledge
            Knowledge = UpdateKnowledge(kleurenlijst, Knowledge, oudekaart)
            situatie[0] = Knowledge
            
            #krijg nieuwe kaart als er nog kaarten in de stapel zitten
            if len(stapelkaarten) != 0:
                MindSpeler = MindNieuweKaart(kleurenlijst, MindSpeler, kaartplek) 
            situatie[2] = MindSpeler
            
            #als er wordt gespeeld, en het is succesvol wordt de tafel aangepast
            if GevolgenZin[1] == "plays":
                if GevolgenZin[5] == "fails.":
                    fuses -= 1
                    situatie[4] = fuses
                else:
                    #update tafel
                    #print "oudetafel", Tafelsituatie
                    #print "GevolgenZin", GevolgenZin
                    nieuwetafel = UpdateTafel(kleurenlijst, GevolgenZin, Tafelsituatie)
                    #print "Nieuwetafel", nieuwetafel
                    #print "TafelRep", TafelRep
                    situatie[9] = nieuwetafel
                    tafelrep = UpdateTafelRepresentatie(kleurenlijst, GevolgenZin, TafelRep, oudekaart)
                    #print "TafelRep", TafelRep
                    situatie[10] = tafelrep
                    
                    #als vuurwerk compleet: bonus Hint token
                    if oudekaart[1] == 5 and tokens < 8:
                        tokens += 1
                        situatie[3] = tokens
            
            
            
            ##kaart van stapel
            if len(stapelkaarten) != 0:    
                kaartenSpeler = NieuweKaart(kleurenlijst, kaartenSpeler, kaartplek, stapelkaarten[0])
                situatie[8] = kaartenSpeler
                aantalkaarten -= 1
                situatie[5] = aantalkaarten
                stapelkaarten.pop(0)
                situatie[6] = stapelkaarten
            
            
        if zin[2] == "3":
            
            #token erbij
            if tokens < 8:
                tokens += 1
                situatie[3] = tokens
        
        
    return situatie


 







Input= []

MindInput = []

#for x,y in mind:
    #MindInput.append(y)



#De volgende functies zijn verschillende manieren om de Input te maken, uiteindelijk gerbuik ik MaakInput
    

#Deze functie gebruikt de argumenten, haalt uit de argumenten de juiste getallen en stopt deze in een lijst met 303 elementen   
def MaakInput(Knowledge, MindAI, MindSpeler,tokens, fuses, aantalkaarten, tafelrep):
    Input = []
    
    for x,y in Knowledge:
        Input.append(y)
    
    for mind in MindAI[1:]:
        for x,y in mind:
            Input.append(y)
            
    for mind in MindSpeler[1:]:
        for x,y in mind:
            Input.append(y)
    
    for x,y in tafelrep:
        Input.append(y)
    
    Input.append(tokens)
    Input.append(fuses)
    Input.append(aantalkaarten)
    
    return Input


#Deze functie gebruikt de argumenten, haalt uit de argumenten de juiste getallen, en stopt die juiste getallen in aparte lijsten.
#Resultaat is een lijst met 4 lijsten (knowledge, MindAI, MindSpeler en Tafelrep) en 3 ints (hints, fuses en aantalkaarten)
def MaakInput2(Knowledge, MindAI, MindSpeler,tokens, fuses, aantalkaarten, tafelrep):
    Input = []
    
    InputK = []
    for x,y in Knowledge:
        InputK.append(y)
    Input.append(InputK)
    
    InputMindAI = []
    for mind in MindAI[1:]:
        for x,y in mind:
            InputMindAI.append(y)
    Input.append(InputMindAI)
    
    InputMindS = []
    for mind in MindSpeler[1:]:
        for x,y in mind:
            InputMindS.append(y)
    Input.append(InputMindS)
    
    InputTR = []
    for x,y in tafelrep:
        InputTR.append(y)
    Input.append(InputTR)
    
    Input.append(tokens)
    Input.append(fuses)
    Input.append(aantalkaarten)
    
    return Input

##Volgende functies zijn verschillende manieren om output in een lijst op te slaan.
##MaakOutput is lijst met 11 elementen
#MaakOutput2 is een getal van 0 tot en met 10
#MaakOutput3 is een lijst 3 elementen
#Ik gebruik uiteindelijk alleen de eerste


#deze functie maakt een lijst van 11 elementen. Elk element is 0 of 1
#Er wordt 1 element een 1 gemaakt, de rest blijft 0
#Als een van de eerste 5 elementen 1 wordt, dan betekent dat de speler een kaart speelt. Welke kaart hij speelt correspondeert
# met welke van de 5 elementen 1 is.
#Als een van de tweede vijf elementen 1 wordt, dan betekent dat dat de speler die kaart discard 
def MaakOutput(MoveZinYou):
    #MoveZinYou = MaakLijstVanZin(MovezinYou)
    
    #print "MoveZinYou", MoveZinYou
    
    actie = MoveZinYou[2]
    if MoveZinYou[3] != "None":
        kaartplek = int(MoveZinYou[3])
    
    outputlijst = [0,0,0,0,0,0,0,0,0,0,0]
    #print len(outputlijst)
    
    #als You een hint geeft, maak de 'hint cel een 1'
    if actie == "0" or actie == "1":
        outputlijst[10] = 1
    
    #als You een kaart speelt, dan wordt er ook voorspelt welke kaart wordt gespeeld
    elif actie == "2":
        outputlijst[kaartplek] = 1
    
    #als You een kaart discard, dan wordt er ook voorspelt welke kaart wordt gespeeld
    else:
        outputlijst[5 + kaartplek] = 1
    
    return outputlijst


#Maakt output van 1 node: 
## 1 = speler speelt plek 1, 
###2 = speler speelt kaart plek 2, 
###6 = discard plek 1, 
###11 = speler geeft hint
def MaakOutput2(MoveZinYou):
    #MoveZinYou = MaakLijstVanZin(MovezinYou)
    
    #print "MoveZinYou", MoveZinYou
    
    actie = MoveZinYou[2]
    if MoveZinYou[3] != "None":
        kaartplek = int(MoveZinYou[3])
    
    output = 0
    #print len(outputlijst)
    
    #als You een hint geeft, maak de 'hint cel een 1'
    if actie == "0" or actie == "1":
        output = 10
    
    #als You een kaart speelt, dan wordt er ook voorspelt welke kaart wordt gespeeld
    elif actie == "2":
        output = 0 + kaartplek
    
    #als You een kaart discard, dan wordt er ook voorspelt welke kaart wordt gespeeld
    else:
        output = 5 + kaartplek
    
    return output



##Verdeelt output alleen in of de speler speelt, discard of hint, zonder bij t houden welke kaart er wordt gespeeld
def MaakOutput3(MoveZinYou):
    
    actie = MoveZinYou[2]
    outputlijst = [0,0,0]

    
    #als You een hint geeft, maak de 'hint cel een 1'
    if actie == "0" or actie == "1":
        outputlijst[2] = 1
    
    #als You een kaart speelt
    elif actie == "2":
        outputlijst[0] = 1
    
    #als You een kaart discard, dan wordt er ook voorspelt welke kaart wordt gespeeld
    else:
        outputlijst[1] = 1
    
    return outputlijst



  
###Deze functie wordt gebruikt om 1 log om te zetten in een lijst met Datapunten
###De datapunten zijn een lijst met daarin: een lijst met input (303 elementen), en 3 verschillende soorten output:
###Output, Output2 en Output 2 in lossen elementen


def DatavanLog(kleuren, loglijst):
    
    ##Eerst wordt alles aangemaakt, om het daarna per peurt aan te kunnen passen
    #en de situatie bij te houden
    
    Knowledge = MaakMindState(kleuren)
    
    MindAlleKaartenAI = InitializeMind(kleuren)
    
    MindAlleKaartenSpeler = InitializeMind(kleuren)
    
    tokens = 8
    fuses = 3
    aantalkaarten = 40 #50 - kaarten AI en kaarten speler
    stapel = maaklijstvantuples(loglijst)
    
    naamAI = GetNaamAI(loglijst)
        
    KaartenSpeler = KaartenVanYouGoed(loglijst, kleuren)
    KaartenAI = KaartenvanAIGoed(loglijst, kleuren, naamAI)
    
    Optafel = []
    for x in kleuren:
        Optafel.append((x,0))
    #print "Optafel", Optafel
    Optafel
    
    TafelRepresentatie = OpTafelRepresentatie(kleuren)
    
    
    #een en twee zijn zijn variabelen die staan voor welke regels van loglijst er gebruikt moeten worden voor HandleTurn 
    
    if IsEersteSpel(loglijst):
        een = 2
        twee = 3
    else:
        een = 3
        twee = 4
    
    
    ##Hier wordt de situatie na elke beurt opgeslagen. Situatie is een lijst met daarin alle informatie
    ##loglijst[een] en loglijst[twee] zijn de regels van de log. Hieruit wordt de informatie gehaald wat er elke beurt gebeurt.
    
    situatie = HandleTurn(kleuren, loglijst[een], loglijst[twee], Knowledge, MindAlleKaartenAI, MindAlleKaartenSpeler, tokens, fuses, aantalkaarten, stapel, KaartenAI, KaartenSpeler, Optafel, TafelRepresentatie)
    
    ##Hierna wordt de datapunten gemaakt en toegeoegd aan een lijst waarin alle datapunten op worden geslagen
    
    ##de verschillende Datasets zijn verschillende manieren waarop ik de data uiteindelijk heb opgeslagen,
    #ik heb uiteinidelijk Dataset3 gebruikt voor mijn NN
    Dataset = []
    Dataset2 = []
    Dataset3 = []
    Dataset4 = []
    
    #de variabele v zorgt ervoor dat we doorgaan tot we bij de laatste Movezin zijn aangekomen
    v = een
    
    while v < len(loglijst) - 4:
        
        #Ik gebruik hier Movezin nog een keer, om alleen datapunten te maken als de AI een hint geeft aan de Speler
        MoveZin = MaakLijstVanZin(loglijst[een])
        #print MoveZin
        
        #Als AI of Speler een hint geeft maak dan de Input
        
        #uiteindelijk gebruik ik voor NN alleen regel 1,3,4 en 8 t/m 14
        
        if MoveZin[2] == "0" or MoveZin[2] == "1":
            #print "Dus dit gebeurt"
            Input = MaakInput(situatie[0], situatie[1], situatie[2], situatie[3], situatie[4], situatie[5], situatie[10])   #1
            Input2 = MaakInput2(situatie[0], situatie[1], situatie[2], situatie[3], situatie[4], situatie[5], situatie[10]) #2
            MoveZinYou = MaakLijstVanZin(loglijst[een+3])                                                                   #3
            Output = MaakOutput(MoveZinYou)                                                                                 #4
            
            #Dataset 1 = Input en Output in aparte lijst
            Dataset.append((Input2,Output))                                                                                 #5
            
            #Dataset 2 = alle verschillende soorten nodes in aparte lijst
            Input2.append(Output)                                                                                           #6
            Dataset2.append(Input2)                                                                                         #7
            
            # Dataset 3 = Input en output bij elkaar in 1 lijst
            OutputNode =  MaakOutput2(MoveZinYou)                                                                           #8
            Input.append(OutputNode)                                                                                        #9
            Input.append(Output)                                                                                            #10
            for x in Output:                                                                                                #11
                Input.append(x)                                                                                             #12
            if len(Input) == 316:                                                                                           #13
                Dataset3.append(Input)                                                                                      #14
                
            # Dataset 4 = input en output bij elkaar in 1 lijst, andere soort output
            Input = MaakInput(situatie[0], situatie[1], situatie[2], situatie[3], situatie[4], situatie[5], situatie[10])   #15
            Output = MaakOutput3(MoveZinYou)                                                                                #16
            Input.append(Output)                                                                                            #17
            Dataset4.append(Input)                                                                                          #18
        
        #Volgende zin, als een speler discard dan is er een regel extra tussen de Movezinnen
        if MoveZin[2] == "3":
            een += 4
            twee += 4
            v += 4
        else: 
            een += 3
            twee += 3
            v += 3
        
        #print "MOVEZIN (zin1): ", loglijst[een]
        #print "ZIN 2 ", loglijst[twee]
        #print "Klaar met zin 2"
        #Simuleer een beurt
        
        
        ##Doe een beurt als we nog niet bij de laatste zin zijn aangekomen
        laatstezinmisschien = MaakLijstVanZin(loglijst[een])
        if laatstezinmisschien[0] != "Score":
            situatie = HandleTurn(kleuren, loglijst[een], loglijst[twee], situatie[0], situatie[1], situatie[2], situatie[3], situatie[4], situatie[5], situatie[6], situatie[7], situatie[8], situatie[9], situatie[10])
        
        
        ##Code die ik kon gebruiken om te debuggen
        ##print de regel waar een fout wordt gevonden en kan kijken of situatie nog wel doet wat het moet doen
        #if count == nr:
            #print "############een: ", een
            
            #for ding in situatie: 
                #if ding == situatie[0]:
                    #print "HIIEEER"
                    #print ding
                    
    
    #poging 1
    #return Dataset
    
    #poging 2
    ##return Dataset2

    #Input + alle soorte 11 delige ouput
    return Dataset3
    
    #input + 3 cellen output
    #return Dataset4




count = 0

#Test of Datalog werkt
#DATA = DatavanLog(kleuren, loglijst)
#
#print "lengte:",len(DATA), "en de rest:", DATA



allefiles = os.listdir(basepath)

#Voordat we door alle logs gaan, maken we eerst een lijst waar we daarna alle datapunten in kunnen stoppen
#Om de data goed te kunnen vervormen als het een dataframe is, geef ik element een naam

ALLEDATA = []

namen = []

for x in range(25):
    namen.append("Knowledge" + str(x))
print namen

for x in range(125):
    namen.append("MindKaartenAI"+ str(x))
    
for x in range(125):
    namen.append("MindKaartenSpeler"+ str(x))
    
for x in range(25):
    namen.append("KaartenOpTafel"+ str(x))
namen.append("Tokens")
namen.append("Fuses")
namen.append("AantalKaarten")
namen.append("Output")
namen.append("OutputLijst")
for x in range(11):
    namen.append("Output"+str(x))

ALLEDATA.append(namen)

print ALLEDATA
print len(ALLEDATA[0])

#ALLEDATA is nu een lijst, met daarin een lijst met namen voor elk element van een datapunt




##Nu gaan we alle logs langs en maken we alle datapunten


##ik wil tellen hoeveel datapunten ik heb en hoeveel logs ik langs ben gegaan
#count kan ook gebruikt worden om te debuggen, door ergens te zeggen if count == ...: print variabele die waarschijnlijk gek doet
count = 0
aantalpunten = 0
teller = 0

kleuren = [0,1,2,3,4]

for File in allefiles[5:]:
    
    ##is de file zelf misschien gek als ik een error krijg?
    #print "count: ", count
    #print "de file: ", File
    
    
    
    filenaam = str(File)
    #print(filenaam)
    
    #alleen de gamelogs, niet de surveys in de log-map, daarom == "g"
    
    if count < 10000:
        if filenaam[0] == "g":
            loglijst = FiletoList(File)
            
            ##filter lege documenten
            if filenaam[1] == "a":
                teller += 1
            
            lengtelog = len(loglijst)
            #print(lengtelog)
            if lengtelog == 0:
                continue
            
            eindzin = loglijst[lengtelog - 1]
            eindzin = MaakLijstVanZin(eindzin)
            
            ##filter de potjes die niet af zijn gemaakt, want anders geet dat een error
            #Als een potje wel een Score heeft, Roep dan datalog aan om het potje om te zetten in datapunten
            #stop daarna alle datapunten in ALLEDATA, de lijst waar alle datapunten worden verzameld
            if eindzin[0] == "Score":
                DataPotje = DatavanLog(kleuren, loglijst)
                aantalpunten += len(DataPotje)
                for punten in DataPotje:
                    ALLEDATA.append(punten)
                
                # print "aantalpunten:", aantalpunten
                count += 1
        
        #als we nij surveys zijn aangekomen hebben we alle gespeelde potjes gehad
        else:
            break
        
print "aantal gechekte files = ", teller
print "klaar, count = ", count
print "aantalpunten:", aantalpunten



#print len(ALLEDATA)
#print len(ALLEDATA[0])
#print ALLEDATA


#Hier maak ik een csv file van ALLEDATA, daarna ben ik klaar

import csv

with open('RESULTTEST5.5.csv', "wb") as fp:
    dingie = csv.writer(fp)
    dingie.writerows(ALLEDATA)


#with open('RESULTAAT.txt', 'w') as f:
#    for item in ALLEDATA:
#        print >> f, item



########
    #########
    #########HIERNA KOMT ALLE CODE DIE IK WEL HEB GESCHREVEN MAAR UITEINDELIJK NIET MEER NODIG HEB


#WORDT NIET MEER GEBRUIKT
#Deze functie is gekopieerd van httpui.py. Deze functie krijgt een seed en maakt een geschud deck (een lijst met 50 kaarten)
def make_deck(seed):
    random.seed(seed)
    deck = []
    for col in ["green", "yellow", "white", "blue", "red"]:
        for num, cnt in enumerate([3,2,2,2,1]):
            for i in xrange(cnt):
                deck.append((col, num+1))
    random.shuffle(deck)
    return deck

#deck = make_deck(zaad)
#q = 0
#for x in deck:
   # q += 1



#class Data():
  #def __init__(self, filename):
    #self.data = []
    #self.loadFile(filename)

  #def loadFile(self,filename):
    #with open(filename) as file:
      #lines = file.readlines()
      #for line in lines:
         # self.data.append(line)
          
  #def printlist(self):
     # for line in self.data:
      #    print(line)
      
      
      ##WORDT NIET MEER GEBRUIKT     
#welke AI speelt er? krijg de naam


##WORDT NIET MEER GEBRUIKT    
##krijg de seed van het potje. Deze is nodig om het deck te kunnnen reconstrueren  
def getseed(loglijst):
    seed = ""
    i = 0
    if IsEersteSpel(loglijst):
        i = 0
    else:
        i = 1
    for c in loglijst[i]:
        if c.isdigit():
                seed = seed + c
    return seed

#test getseed
print(getseed(loglijst))
zaad = getseed(loglijst)      


#WORDT NIET GEBRUIKT
##Doet hetzelfde als MaakMindState, maar dan eleganter
def MaakMindState2(kleurenlijst):
    mind = []
    allekaarten = MaakLijstAlleKaarten(kleurenlijst)
    for c, nr in allekaarten:
        if nr == 1:
                mind.append(((c,nr), 3))
        if nr == 2 or nr == 3 or nr == 4:
                mind.append(((c,nr), 2))
        if nr == 5:
                mind.append(((c,nr), 1))
    return mind

#stacky = list(stack)
#stapeltje = list(stapel)

#print("daar gaan we")
#for x in stapeltje:
    #print(x)
    #for y in stacky:
        #print(y)
        #if x == y:
            #stacky.remove(x)
            #break

##Dit zijn de 10 kaarten die in de handen van de spelers zitten op het begin.
##print("overgebleven stapel: ", len(stacky), stacky)
#EERSTEHANDEN = stacky



###NIET MEER NUTTIG, WAS VOOR TESTEN

##print("decky ", decky)
##print("stack:  ",len(stack)," ",stack)

#Stack is volledig deck van 50 kaarten, stapel is nadat de spelers 10 kaarten hebben gepakt
    
##print(stack, len(stack))
##print(stapel, len(stapel))
    
#print(stack)
#print(loglijst[2])

###
###




#print("MindAlleKaartenAI: ", MindAlleKaartenAI)

#MindAlleKaartenAI[3] = UpdateAIMindHint([0,1,2,3,4], MindAlleKaartenAI[3], None, 2)
#print(MindAlleKaartenAI[0])
#print(MindAlleKaartenAI[0][2])
#MindAlleKaartenAI[0][2] = (0,2)
#print("MindAlleKaartenAI na update: ", MindAlleKaartenAI)

#MindAIanderekaart = MindNieuweKaartAI([0,1,2,3,4], MindAlleKaartenAI, 1)
#print("MindAIanderekaart: ", MindAIanderekaart)

#MindAlleKaartenSpeler[3] = UpdateMindSpeler([0,1,2,3,4], MindAlleKaartenSpeler[3], (0,5))
#print("MindAlleKaartenSpeler na update: ",MindAlleKaartenSpeler)

#MindSpelerNieuweKaart = MindNieuweKaartSpeler([0,1,2,3,4], MindAlleKaartenSpeler, 2, (3,3))
#print("nieuwe kaart", MindSpelerNieuweKaart)



#Knowledge = MaakMindState([0,1,2,3,4])
#print(Knowledge)


####Tests voor MaakMind en Update Minde functies

#MindKaart1 = MaakMindAI([0,1,2,3,4])
#print("MindKaart1 ", MindKaart1)

#MindKaart1 = UpdateAIMindHint([0,1,2,3,4], MindKaart1, 3, None)
#print("MindKaart1 updated ", MindKaart1)

#MindKaart1 = UpdateAIMindHint([0,1,2,3,4], MindKaart1, None, 5)
#print("Mindkaart1 moet nu (3,5) zijn", MindKaart1)

#MindKaart1Speler = MaakMindSpeler([0,1,2,3,4])
#print("MindKaart1Speler", MindKaart1Speler)

#MindKaart1Speler = UpdateMindSpeler([0,1,2,3,4], MindKaart1Speler, Kaartenvanspeler[0])
#print("MindKaart1Speler na update", MindKaart1Speler)

#def UpdateTokennumber(regel):
    
    



##WORDT NIET MEER GEBRUIKT
#Deze functie is gemaakt om de kaarten van de Speler te achterhalen door die in de log te zoeken.
#Hij zoekt naar de eerste regel met You en gaat er dan vanuit dat in die regel alle kaarten van you staan
#Dit klopt echt niet, dus deze functie wordt niet meer gebruikt
def KaartenVanYou(loglijst, kleurenlijst):
    p = 0
    if IsEersteSpel(loglijst):
        p += 0
    else:
        p += 1
        
    if EersteMoveIsDiscard(loglijst):
        p += 1
    else:
        p += 0
    
    if TweedeMoveIsDiscard(loglijst):
        p += 1
    else:
        p += 0
    
    
    EersteZin = loglijst[4 + p]
    EersteZinLijst = MaakLijstVanZin(EersteZin)
    print "dit moet 'You' zijn ", EersteZinLijst[0]
    tuplelijst = []
    detuple = ()
    eerste = ""
    tweede = 0
    for y in EersteZinLijst:
        if y == "blue" or y == "red" or y == "green" or y == "yellow" or y == "white":
            eerste = y
        if y.isdigit():
            tweede = int(y)
            detuple = (eerste, tweede)
            tuplelijst.append(detuple)
    result = KleurNaarGetal(tuplelijst, kleurenlijst)
    return result


##WORDT NIET MEER GEBRUIKT
def KaartenvanAI(loglijst, kleurenlijst):
    if EersteMoveIsDiscard(loglijst):
        p = 1
    else:
        p = 0
    if IsEersteSpel(loglijst):
        i = 7 + p
    else:
        i = 8 + p
    EersteZin = loglijst[i]
    EersteZinLijst = MaakLijstVanZin(EersteZin)
    tuplelijst = []
    detuple = ()
    eerste = ""
    tweede = 0
    for y in EersteZinLijst:
        if y == "blue" or y == "red" or y == "green" or y == "yellow" or y == "white":
            eerste = y
        if y.isdigit():
            tweede = int(y)
            detuple = (eerste, tweede)
            tuplelijst.append(detuple)
    result = KleurNaarGetal(tuplelijst, kleurenlijst)
    return result




    

# deze functie wordt niet meer gebruikt
def UpdateHints(MoveZin, HintEerst):
    Hint = HintEerst
    zin = MaakLijstVanZin(MoveZin)
    #print(zin[2])
    if zin[2] == "1" or zin[2] == "0":
        Hint = HintEerst - 1
    elif zin[2] == "3":
        Hint = HintEerst + 1
    return Hint

#test hierbovenstaande functie
#dit = "MOVE: 1 1 1 1 None None"
#nummerhints = UpdateHints(dit, 5)
#print("nummer nu", nummerhints)


#deze functie wordt niet meer gebruikt
def UpdateFuses(SomeonedoesZin, FusesEerst):
    Fuses = FusesEerst
    zin = MaakLijstVanZin(SomeonedoesZin)
    if zin[1] == "plays":
        if zin[5] == "fails.":
            Fuses = FusesEerst - 1
    return Fuses

#test voor hierbovenstaande functie
#dit = "You plays green 2 and fails. Board was green 0, yellow 1, white 0, blue 2, red 2"
#fusenummer = UpdateFuses(dit, 2)
#print("fusenummer: ", fusenummer)
#dat = "You plays blue 4 successfully! Board is now green 0, yellow 2, white 0, blue 4, red 2"
#fusenummer2 = UpdateFuses(dat, 2)
#print("fusenummer: ", fusenummer2)


#deze functie wordt niet meer gebruikt
def UpdateNumberCards(Movezin, CardsEerst):
    Cards = CardsEerst
    zin = MaakLijstVanZin(Movezin)
    if zin[2] == "2" or zin[2] == "3":
        Cards = CardsEerst - 1 
    return Cards

#test hierbovenstaande functie
#dit = "MOVE: 1 0 1 1 None None"
#nummerhints = UpdateNumberCards(dit, 35)
#print("nummer nu", nummerhints)



#Volgende 4 functies zijn niet meer nodig, omdat ik de representatie van MindSpeler op een bepaald moment
#precies hetzelfde behandelde als die van de AI, eerst niet

#Was eerst anders dan AI, maar nu niet meer
#def MaakMindSpeler(kleurenlijst):
    #result = []
   # allekaarten = MaakLijstAlleKaarten(kleurenlijst)
  #  for kaart in allekaarten:
 #       result.append((kaart, 1))
#    return result
 
 ##Mindstate hoort bij plek in hand
#def UpdateMindSpeler(kleurenlijst, MindSpeler, KaartSpeler):
#    result = []
#    for kaart, welofniet in MindSpeler:
#        if kaart == KaartSpeler:
 #           welofniet = 1
 #       result.append((kaart, welofniet))
 #   return result

#def InitializeMind(kleurenlijst, SpelerKaarten):
#    SpelerKaarten = [(0,0),(0,0),(0,0),(0,0),(0,0)]
#    FiveMinds = []
#    OneMind = []
#    FiveMinds.append(SpelerKaarten)
#    for kaart in SpelerKaarten:
#        OneMind = MaakMind(kleurenlijst)
#        FiveMinds.append(OneMind)
#    return FiveMinds

#def MindNieuweKaartSpeler(kleurenlijst, Mind, kaartwegplek, nieuwekaart):
#    kaartwegplek = int(kaartwegplek)
#    teller = kaartwegplek + 1
#    for mindkaart in Mind[teller:]:
#        if teller == 5:
#            Mindnieuw = MaakMindSpeler(kleurenlijst)
#            Mindnieuw = UpdateMindSpeler(kleurenlijst, Mindnieuw, nieuwekaart)
#            Mind[teller] = Mindnieuw
#            Mind[0][teller - 1] = nieuwekaart
#        else:
#            Mind[teller] = Mind[(teller+1)]
#            Mind[0][teller - 1] = Mind[0][teller]
#            teller += 1
#    return Mind

#
#kleurending = [(0,1,2,3,4)]
#ALLEKLEUREN = permutations([0,1,2,3,4])
#allekleuren = []
#for i in ALLEKLEUREN:
    #combi = []
    #for x in i:
        #combi.append(x)
    #allekleuren.append(combi)

#kleuren = [0,1,2,3,4]

#Mind
#mind = MaakMindState([0,1,2,3,4])
#print("mind: ", mind)
            

#stack = KleurNaarGetal(decky, [0,1,2,3,4])


        

####
####voordat ik DATAVANLOG had, deed ik deze dingen om handleturn te testen
####
    
#Kaartenvanspeler = KaartenVanYou(loglijst)
#print Kaartenvanspeler
#KaartenvanAI = KaartenvanAI(loglijst)



#MindAlleKaartenSpeler = InitializeMindSpeler([0,1,2,3,4], Kaartenvanspeler)
#print(MindAlleKaartenSpeler)

#MindAlleKaartenAI = InitializeMindAI([0,1,2,3,4])

#Knowledge = MaakMindState(kleuren)


#tokens = 8
#fuses = 3
#aantalkaarten = 40
#stapel = maaklijstvantuples(loglijst)

#Optafel = []
#for x in kleuren:
#    Optafel.append((x,0))
#print "Optafel", Optafel
#Optafel

#TafelRepresentatie = OpTafelRepresentatie(kleuren)
###
###  


###HANDLE TURN TESTS

#SITUATIE = HandleTurn(kleuren, loglijst[3], loglijst[4], Knowledge, MindAlleKaartenAI, MindAlleKaartenSpeler, tokens, fuses, aantalkaarten, stapel, KaartenvanAI, Optafel, TafelRepresentatie)

#for ding in SITUATIE:
 #   print(ding)

#print("###########################VOLGENDE#########")


#SITUATIE2 = HandleTurn(kleuren, loglijst[6], loglijst[7], SITUATIE[0], SITUATIE[1], SITUATIE[2], SITUATIE[3], SITUATIE[4], SITUATIE[5], SITUATIE[6], SITUATIE[7], SITUATIE[8], SITUATIE[9])

#for ding in SITUATIE2:
 #   print(ding)
#print("#############################VOLGENDE#########")
#SITUATIE3 = HandleTurn(kleuren, loglijst[9], loglijst[10], SITUATIE2[0], SITUATIE2[1], SITUATIE2[2], SITUATIE2[3], SITUATIE2[4], SITUATIE2[5], SITUATIE2[6], SITUATIE2[7], SITUATIE2[8], SITUATIE2[9])

#print(SITUATIE3[1])
#for ding in SITUATIE3:
 #   print(ding)



### INPUT TEST
 
#InputSituatie3 = MaakInput(SITUATIE3[0], SITUATIE[1], SITUATIE3[2], SITUATIE3[3], SITUATIE3[4], SITUATIE3[5], SITUATIE3[9])
#print("InputSituatie3" ,len(InputSituatie3), InputSituatie3)
 



