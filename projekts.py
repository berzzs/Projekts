import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import PySimpleGUI as sg
import sqlite3

# Iestata Spotify API akreditācijas datus
CLIENT_ID = 'e071519fa3f94df6b1b72a11ae926fb4'
CLIENT_SECRET = '1675bc1653da4b0b915f1bf08b03cc9b'

# Izveidoju API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Izveidojam savienojumu ar SQLite datubāzi
connection = sqlite3.connect('lietotāju_dziesmu_datubāze.db')
cursor = connection.cursor()

# Izveidojam tabulu datubāzē, ja tā vēl neeksistē
cursor.execute('''CREATE TABLE IF NOT EXISTS dziesmas (
                    id INTEGER PRIMARY KEY,
                    lietotāja_id TEXT,
                    nosaukums TEXT,
                    mākslinieki TEXT,
                    albums TEXT,
                    izdošanas_datums TEXT)''')
connection.commit()

# Funkcija, lai saglabātu dziesmu datubāzē
def saglabāt_dziesmu_datus(lietotāja_id, dziesmas_info):
    cursor.execute('''INSERT INTO dziesmas (lietotāja_id, nosaukums, mākslinieki, albums, izdošanas_datums)
                      VALUES (?, ?, ?, ?, ?)''', (lietotāja_id, dziesmas_info['Nosaukums'], dziesmas_info['Mākslinieki'],
                                                  dziesmas_info['Albums'], dziesmas_info['Izdošanas datums']))
    connection.commit()

# Funkcija, lai meklētu dziesmu Spotify
def meklēt_dziesmu(uzvaicājums):
    rezultāti = sp.search(q=uzvaicājums, type='track', limit=1)
    if rezultāti['tracks']['items']:
        dziesma = rezultāti['tracks']['items'][0]
        dziesmas_info = {
            'Nosaukums': dziesma['name'],
            'Mākslinieki': ', '.join([mākslinieks['name'] for mākslinieks in dziesma['artists']]),
            'Albums': dziesma['album']['name'],
            'Izdošanas datums': dziesma['album']['release_date']
        }
        return dziesmas_info
    else:
        return None

# PySimpleGUI izkārtojums
izkārtojums = [
    [sg.Text('Ievadi dziesmas nosaukumu:'), sg.InputText(key='-UZVAICĀJUMS-'), sg.Button('Meklēt')],
    [sg.Text(size=(40, 4), key='-DZIESMAS_INFO-')]
]

# Izveido logu
logs = sg.Window('Spotify Dziesmu meklēšana', izkārtojums)

# Notikumu cikls
while True:
    notikums, vērtības = logs.read()
    if notikums == sg.WINDOW_CLOSED:
        break
    elif notikums == 'Meklēt':
        uzvaicājums = vērtības['-UZVAICĀJUMS-']
        if uzvaicājums:
            dziesmas_info = meklēt_dziesmu(uzvaicājums)
            if dziesmas_info:
                dziesmas_info_str = '\n'.join([f"{atslēga}: {vērtība}" for atslēga, vērtība in dziesmas_info.items()])
                logs['-DZIESMAS_INFO-'].update(dziesmas_info_str)
                
                # Saglabājam dziesmu datubāzē ar lietotāja ID
                lietotāja_id = 'piemērs_lietotājam'
                saglabāt_dziesmu_datus(lietotāja_id, dziesmas_info)
            else:
                logs['-DZIESMAS_INFO-'].update('Dziesma nav atrasta.')
        else:
            logs['-DZIESMAS_INFO-'].update('Lūdzu, ievadi dziesmas nosaukumu.')

logs.close()

# Aizveram datubāzes savienojumu
connection.close()
