import asyncio

import cv2
import numpy as np
import websockets
import base64
import json
import os


# CORONA_TEMPLATE_PATH_1 = os.path.dirname(os.path.abspath(__file__)) + '/tem1.png'
# CORONA_TEMPLATE_PATH_2 = os.path.dirname(os.path.abspath(__file__)) + '/tem2.png'
# CORONA_TEMPLATE_PATH_3 = os.path.dirname(os.path.abspath(__file__)) + '/tem3.png'
# CORONA_TEMPLATE_PATH_4 = os.path.dirname(os.path.abspath(__file__)) + '/tem4.png'
# CORONA_TEMPLATE_PATH_5 = os.path.dirname(os.path.abspath(__file__)) + '/tem5.png'
# CORONA_TEMPLATE_PATH_6 = os.path.dirname(os.path.abspath(__file__)) + '/tem6.png'
# Queen
CORONA_TEMPLATE_PATH_7  = os.path.dirname(os.path.abspath(__file__)) + '/tem7.png'
# CORONA_TEMPLATE_PATH_8 = os.path.dirname(os.path.abspath(__file__)) + '/tem8.png'
# CORONA_TEMPLATE_PATH_9 = os.path.dirname(os.path.abspath(__file__)) + '/tem9.png'
# CORONA_TEMPLATE_PATH_10 = os.path.dirname(os.path.abspath(__file__)) + '/tem10.png'
CORONA_SCALE_RATIO = 0.5


# corona_template_image_1 = cv2.imread(CORONA_TEMPLATE_PATH_1, 0)
# corona_template_image_2 = cv2.imread(CORONA_TEMPLATE_PATH_2, 0)
# corona_template_image_3 = cv2.imread(CORONA_TEMPLATE_PATH_3, 0)
# corona_template_image_4 = cv2.imread(CORONA_TEMPLATE_PATH_4, 0)
# corona_template_image_5 = cv2.imread(CORONA_TEMPLATE_PATH_5, 0)
# corona_template_image_6 = cv2.imread(CORONA_TEMPLATE_PATH_6, 0)
# Queen
corona_template_image_7 = cv2.imread(CORONA_TEMPLATE_PATH_7, 0)
# corona_template_image_8 = cv2.imread(CORONA_TEMPLATE_PATH_8, 0)
# corona_template_image_9 = cv2.imread(CORONA_TEMPLATE_PATH_9, 0)
# corona_template_image_10 = cv2.imread(CORONA_TEMPLATE_PATH_10, 0)




# corona_template_image_1 = cv2.resize(corona_template_image_1, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# corona_template_image_2 = cv2.resize(corona_template_image_2, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# corona_template_image_3 = cv2.resize(corona_template_image_3, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# corona_template_image_4 = cv2.resize(corona_template_image_4, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# corona_template_image_5 = cv2.resize(corona_template_image_5, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# corona_template_image_6 = cv2.resize(corona_template_image_6, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# Queen
corona_template_image_7 = cv2.resize(corona_template_image_7, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# corona_template_image_8 = cv2.resize(corona_template_image_8, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# corona_template_image_9 = cv2.resize(corona_template_image_9, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
# corona_template_image_10 = cv2.resize(corona_template_image_10, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)



corona_template = []
# corona_template.append(corona_template_image_1)
# corona_template.append(corona_template_image_2)
# corona_template.append(corona_template_image_3)
# corona_template.append(corona_template_image_4)
# corona_template.append(corona_template_image_5)
# corona_template.append(corona_template_image_6)
# Queen
corona_template.append(corona_template_image_7)
# corona_template.append(corona_template_image_8)
# corona_template.append(corona_template_image_9)
# corona_template.append(corona_template_image_10)


def catch_corona(wave_image, threshold=0.8):
    wave_image_gray = cv2.cvtColor(wave_image, cv2.COLOR_BGR2GRAY)
    results = [[]]

    for template in corona_template:
        res = cv2.matchTemplate(wave_image_gray, template, cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val < threshold:
            return []

        width, height = template.shape[::-1]
        top_left = max_loc
        bottom_right = (top_left[0] + width, top_left[1] + height)
        results.append([[top_left, bottom_right]])

    return results

def base64_to_image(base64_data):
    encoded_data = base64_data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    return img

async def play_game(websocket, path):
    print('Corona Killer is ready to play!')
    catchings = []
    last_round_id = ''
    wave_count = 0
    
    while True:

        ### receive a socket message (wave)
        try:
            data = await websocket.recv()
        except Exception as e:
            print('Error: ' + e)
            break

        json_data = json.loads(data)

        ### check if starting a new round
        if json_data["roundId"] != last_round_id:
            print(f'> Catching corona for round {json_data["roundId"]}...')
            last_round_id = json_data["roundId"]

        ### catch corona in a wave image
        wave_image = base64_to_image(json_data['base64Image'])
        results = catch_corona(wave_image)


        print(f'>>> Wave #{wave_count:03d}: {json_data["waveId"]}')
        wave_count = wave_count + 1

        ### store catching positions in the list
        for result in results:
            for res in result:
                catchings.append({
                    "positions": [
                        {
                            "x": (res[0][0] + res[1][0]) / 2, 
                            "y": (res[0][1] + res[1][1]) / 2
                        }
                    ],
                    "waveId": json_data["waveId"]
                })

        ### send result to websocket if it is the last wave
        if json_data["isLastWave"]:
            round_id = json_data["roundId"]
            print(f'> Submitting result for round {round_id}...')

            json_result = {
                "roundId": round_id,
                "catchings": catchings,
            }

            await websocket.send(json.dumps(json_result))
            print('> Submitted.')

            catchings = []
            wave_count = 0


start_server = websockets.serve(play_game, "localhost", 8765, max_size=100000000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()