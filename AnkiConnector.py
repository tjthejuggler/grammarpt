import requests
import base64
import os

def notify(text):
    print('text')    
    msg = "notify-send ' ' '"+text+"'"
    os.system(msg)


class AnkiConnector:
    def __init__(self, deck_name='Default', note_type='Basic', allow_duplicate=False, back_image=None):
        self.deck_name = deck_name
        self.note_type = note_type
        self.allow_duplicate = allow_duplicate
        self.back_image = back_image


    def add_card(self, front, back, source):
        # Create the note
        note = {
            'deckName': self.deck_name,
            'modelName': self.note_type,
            'fields': {
                'Front': front,
                'Back': back
            },
            'options': {
                'allowDuplicate': self.allow_duplicate
            },
            'tags': []
        }      
        
        formatted_source = '<br><br>source: <a href="'+source+'">'+source+'</a>' if source else ''
        # Add the back image to the media folder if provided
        if self.back_image:
            filename = os.path.splitext(self.back_image)[0]
            filename = filename.split('/')[-1]
            print(self.back_image)
            with open(self.back_image, 'rb') as f:
                image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            requests.post('http://localhost:8765', json={
                'action': 'storeMediaFile',
                'version': 6,
                'params': {
                    'filename': filename+'.jpg',
                    'data': base64_data
                }
            })
            # Add the image tag to the back field
            note['fields']['Back'] += '<br><img src="'+filename+'.jpg">'+formatted_source
        else:
            note['fields']['Back'] += formatted_source

        # Add the note to the deck
        response = requests.post('http://localhost:8765', json={
            'action': 'addNote',
            'version': 6,
            'params': {
                'note': note
            }
        })
        #get the type 
        # of response.text
        
        noteid = response.text.replace('{"result":','').replace(', "error": null}','')

        #notify("checking!!!", type(response.text))
        with open('/home/lunkwill/projects/grammarpt/response.txt', 'w') as f:
            f.write(response.text)

        #convert response.text to a dict {"result": 1680192958648, "error": null}
        # with open('/home/lunkwill/projects/grammarpt/response.txt', 'r') as f:
        #     response_text = f.read()
        

        
        return(self.verify_card_created(int(noteid)))

        # if response.status_code == 200:
        #     notify('Card added to the deck.', response.result)
        #     print('Card added to the deck.')
        #     #save response to a text file
        #     with open('/home/lunkwill/projects/grammarpt/response.txt', 'w') as f:
        #         f.write(response.text)
            
        #     return(response.result)

        # else:
        #     print('An error occurred:', response.text)


    def verify_card_created(self, note_id):
        #notify('verifying card creation')
        response = requests.post('http://localhost:8765', json={
            'action': 'notesInfo',
            'version': 6,
            'params': {
                'notes': [note_id]
            }
        })
        print(response.text)
        if str(note_id) in response.text:
            notify('Card created successfully.')
            return True
        else:
            notify('An error occurred:'+ response.text)
            print('An error occurred:'+ response.text)
            return False

    # def add_card(self, front, back, back_image=None):
    #     # Create the note
    #     note = {
    #         'deckName': self.deck_name,
    #         'modelName': self.note_type,
    #         'fields': {
    #             'Front': front,
    #             'Back': back
    #         },
    #         'options': {
    #             'allowDuplicate': self.allow_duplicate
    #         },
    #         'tags': []
    #     }

    #     # Add the note to the deck
    #     response = requests.post('http://localhost:8765', json={
    #         'action': 'addNote',
    #         'version': 6,
    #         'params': {
    #             'note': note
    #         }
    #     })

    #     if response.status_code == 200:
    #         print('Card added to the deck.')
    #     else:
    #         print('An error occurred:', response.text)



#FOR TESTING
# deck_name = '...My discoveries'
# note_type = 'Basic'
# connector = AnkiConnector(deck_name=deck_name, note_type=note_type, allow_duplicate=False)
# connector.add_card("1hat ithe colober sinr  ats?", "Polar bears have jet black skin under their white fur coats.", "https://factanimal.com/animal-facts/")