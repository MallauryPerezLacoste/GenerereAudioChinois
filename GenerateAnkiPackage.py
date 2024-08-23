import csv
import sys
import os
from gtts import gTTS
import genanki
import pandas as pd
from datetime import datetime

filePath = "./voc.csv"
rep="./repAudios"
packageName="LanguageReactor_"+datetime.now().strftime('%Y-%m-%d')
OUTPUT_APKG = packageName+'.apkg'
MODEL_ID = 1607392319
DECK_ID = 2059425102

def generateAudio():
    global rep
    
    
    argc = len(sys.argv)
    argv = sys.argv
    
    listWords=""
    if argc<2:             
        listWords=getListWords(filePath)
    else:
        listWords=getListWords(argv[0])
    
    if argv==3:
        rep=argv[1]


    for word in listWords:
        saveSound(word, rep)
        

def getListWords(filePath):
    mots_premiere_colonne = []
    with open(filePath, mode='r', encoding='utf-8') as fichier_csv:
        lecteur_csv = csv.reader(fichier_csv, delimiter='\t')
    
        for ligne in lecteur_csv:

            mots_premiere_colonne.append(ligne[0])
    return mots_premiere_colonne

    
def saveSound(word,rep):
    word=word+".mp3"
    saveHere=os.path.join(rep,word)
    
    if not os.path.exists(rep):
        os.makedirs(rep)
    
    if not os.path.isfile(saveHere):
            
        tts = gTTS(text=word, lang='zh')
        tts.save(saveHere)
        
        print(f"Audio sauvegardé sous : {saveHere}")
    
    return


def generateAPKG():    
    column_names = ['simplifié', 'pinyin', 'traduction']
    df = pd.read_csv(filePath, names=column_names, header=None, delimiter='\t')
    
    
    cardModel=createCardModel()
    deck=createDeck()
    
    addCards(cardModel,deck,df)
    return

def createCardModel():
    my_model = genanki.Model(
    MODEL_ID,
    'LanguageReactorModel',
    fields=[
        {'name': 'Simplifié'},
        {'name': 'Pinyin'},
        {'name': 'Traduction'},
        {'name': 'Audio'}
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '<div class=question>{{Simplifié}}</div>',
            'afmt': '<div class=reponse>{{FrontSide}}<hr id="answer">{{Pinyin}}<br>{{Traduction}}<br>{{Audio}}</div>'
        }
    ],
    css='''
        .card {
            font-size: 24px; /* Taille de police par défaut */
            text-align: center; /* Centrer le texte */
        }
        .question {
            font-size: 48px; /* Augmente la taille de la police pour le champ "simplifié" */
        }
        .reponse {
            font-size: 24px; /* Taille de la police pour le champ "pinyin" */
        }
        '''
    )
    return my_model

def createDeck():
    my_deck = genanki.Deck(
    DECK_ID,
    packageName
    )
    return my_deck

def addCards(cardModel,deck,df):
    # Ajouter des cartes au deck
    for _, row in df.iterrows():
        simplifié = row['simplifié']
        pinyin = row['pinyin']
        traduction = row['traduction']
        audio_file = os.path.join(rep, f'{simplifié}.mp3')
    
        # Construire le contenu de la carte
        audio_tag = f'<audio src="{simplifié}.mp3" autoplay controls></audio>'
        
        my_note = genanki.Note(
            model=cardModel,
            fields=[simplifié, pinyin, traduction, audio_tag],
            tags=[]
        )
        
        deck.add_note(my_note)
    
    # Créer le paquet Anki
    my_package = genanki.Package(deck)
    
    # Ajouter les fichiers audio au paquet
    for filename in os.listdir(rep):
        if filename.endswith('.mp3'):
            my_package.media_files.append(os.path.join(rep, filename))
    
    # Sauvegarder le paquet
    my_package.write_to_file(OUTPUT_APKG)
    
    print(f"Paquet Anki créé avec succès: {OUTPUT_APKG}")
    return




if __name__ == "__main__":
    generateAudio()
    generateAPKG()