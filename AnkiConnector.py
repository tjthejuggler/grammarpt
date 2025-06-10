import requests
import base64
import os

def notify(text): # This notify is within AnkiConnector, may differ from the main script's
    print(f"AnkiConnector Notify: {text}") # Changed to print for less dependency during testing
    # msg = "notify-send ' ' '"+text+"'" # Original line, can be restored later
    # os.system(msg)

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
        
        try:
            response_json = response.json()
        except ValueError: # JSONDecodeError in Python 3.5+
            notify(f"AnkiConnect returned non-JSON response: {response.text}")
            print(f"AnkiConnect returned non-JSON response: {response.text}")
            with open('response.txt', 'w') as f:
                f.write(f"Non-JSON response: {response.text}")
            return False

        with open('response.txt', 'w') as f: # Log the full JSON response
            f.write(response.text) # response.text is already a string

        api_error = response_json.get('error')
        if api_error:
            error_message = f"AnkiConnect API error: {api_error}"
            notify(error_message)
            print(error_message)
            return False # Card creation failed due to API error

        noteid = response_json.get('result')
        if noteid is None:
            error_message = f"AnkiConnect response missing 'result' (noteId): {response.text}"
            notify(error_message)
            print(error_message)
            return False # Card creation failed, no noteId

        try:
            return self.verify_card_created(int(noteid))
        except ValueError:
            error_message = f"AnkiConnect returned non-integer noteId: {noteid}"
            notify(error_message)
            print(error_message)
            return False

    def verify_card_created(self, note_id):
        #notify('verifying card creation')
        response = requests.post('http://localhost:8765', json={
            'action': 'notesInfo',
            'version': 6,
            'params': {
                'notes': [note_id]
            }
        })
        print(f"Verification response: {response.text}")
        try:
            response_json = response.json()
            if response_json.get('error'):
                notify(f"Verification error: {response_json.get('error')}")
                print(f"Verification error: {response_json.get('error')}")
                return False
            if response_json.get('result') and len(response_json['result']) > 0:
                 # Check if the note_id is present in any of the fields of the first result
                if any(str(note_id) in str(field_value) for field_value in response_json['result'][0].values()):
                     notify('Card created successfully (verified by notesInfo).')
                     return True
                # Fallback check on raw text if specific field check is too complex or note_id format varies
                elif str(note_id) in response.text: # Check if note_id is mentioned anywhere in the successful response
                    notify('Card created successfully (verified by note_id in response text).')
                    return True
            notify(f"Card verification failed, noteId {note_id} not found clearly in notesInfo response: {response.text}")
            return False
        except ValueError: # JSONDecodeError
            notify(f"Verification response was not valid JSON: {response.text}")
            print(f"Verification response was not valid JSON: {response.text}")
            # Fallback: simple check if note_id is in the raw text (less reliable)
            if str(note_id) in response.text:
                notify('Card created successfully (verified by note_id in non-JSON response text - less reliable).')
                return True
            return False


#FOR TESTING
# deck_name = '...My discoveries'
# note_type = 'Basic'
# connector = AnkiConnector(deck_name=deck_name, note_type=note_type, allow_duplicate=False)
# connector.add_card("1hat ithe colober sinr  ats?", "Polar bears have jet black skin under their white fur coats.", "https://factanimal.com/animal-facts/")