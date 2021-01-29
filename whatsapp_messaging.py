from twilio.rest import Client
import requests
from collections import deque
from bs4 import BeautifulSoup


observables = ["USD", "EURO", "UF"]
observed_values = { value: deque([0 for _ in range(30)]) for value in observables }

to_float = lambda x: float(x.replace(",", ""))

def get_prices():

    # Valor usd, euro y uf
    page = requests.get("https://si3.bcentral.cl/Bdemovil/BDE/IndicadoresDiarios")
    soup = BeautifulSoup(page.content, 'html.parser')
    body = soup.body

    items_div = body.find_all(
            "table", class_="tableUnits")

    EURO = to_float(items_div[2].find("td", class_="col-xs-2").find("p").text)
    # print(f"EURO: ${EURO}")

    USD = to_float(items_div[1].find("td", class_="col-xs-2").find("p").text)
    # print(f"USD: ${USD}")

    UF = to_float(items_div[0].find("td", class_="col-xs-2").find("p").text)
    # print(f"UF: ${UF}")

    # Update values
    observed_values["EURO"].append(EURO)
    observed_values["EURO"].popleft()
    observed_values["USD"].append(USD)
    observed_values["USD"].popleft()
    observed_values["UF"].append(UF)
    observed_values["UF"].popleft()


def get_vars(obs):
    # actual value
    aval = obs[-1]

    # 1-day var
    if not obs[-2]:
        oday = "--"
    else:
        oday = round(100 * (aval - obs[-2]) / obs[-2], 2)

    # 30-day var
    if not obs[0]:
        tday = "--"
    else:
        tday = round(100 * (aval - obs[0]) / obs[0], 2)

    return aval, oday, tday


def get_sticker(var):
    if var == "--":
        return ""
    if var > 0:
        return "⬆️"
    return "⬇️"


def get_body(name):
    ausd, ousd, tusd = get_vars(observed_values['USD'])
    aeur, oeur, teur = get_vars(observed_values['EURO'])
    auf, ouf, tuf = get_vars(observed_values['UF'])

    body = f"""
Good morning {name}!📈

*USD*
    *Value*: ${ausd}
    *1-Day var*: {ousd}% {get_sticker(ousd)}
    *30-Day var*: {tusd}% {get_sticker(tusd)}

*EURO*
    *Value*: ${aeur}
    *1-Day var*: {oeur}% {get_sticker(oeur)}
    *30-Day var*: {teur}% {get_sticker(teur)}

*UF*
    *Value*: ${auf}
    *1-Day var*: {ouf}% {get_sticker(ouf)}
    *30-Day var*: {tuf}% {get_sticker(tuf)}
"""
    
    return body


def send_msg(event=None, context=None):

    get_prices()

    # get your sid and auth token from twilio
    twilio_sid = 'AC6443994b07b023085bc108d63a98316e'
    auth_token = '03e4f3ffa73fed76ced8b1629a410272'

    whatsapp_client = Client(twilio_sid, auth_token)

    # keep adding contacts to this dict to send
    # them the message
    contact_directory = {'Juan Carlos': '+56978531166'}

    for name, number in contact_directory.items():

        msg = whatsapp_client.messages.create(
                body = get_body(name),
                from_= 'whatsapp:+14155238886',
                to='whatsapp:' + number,
            )

        print(msg.sid)


get_prices()
get_prices()
send_msg()
