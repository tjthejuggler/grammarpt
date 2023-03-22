import requests
import base64
import os

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
            note['fields']['Back'] += '<br><img src="'+filename+'.jpg"><br><br>source: '+source

        # Add the note to the deck
        response = requests.post('http://localhost:8765', json={
            'action': 'addNote',
            'version': 6,
            'params': {
                'note': note
            }
        })

        if response.status_code == 200:
            print('Card added to the deck.')
        else:
            print('An error occurred:', response.text)


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