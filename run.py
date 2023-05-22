import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

class Domain101Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        url = "https://my.101domain.com/login.html"
        headers = {
            'origin': 'https://my.101domain.com',
            'referer': 'https://my.101domain.com/login.html',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Whale/3.20.182.14 Safari/537.36'
        }
        payload = {
            'username': self.username,
            'password': self.password,
            'view_lang': 'en_US',
            'submit': 'Login'
        }
        response = self.session.post(url, headers=headers, data=payload)
        return response.status_code == 200

    def get_account_balance(self):
        headers = {
            'origin': 'https://my.101domain.com',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Whale/3.20.182.14 Safari/537.36'
        }
        response = self.session.get("https://my.101domain.com", headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.find('a', id='menuitem-account')

        if element:
            href_value = "https://my.101domain.com" + element['href']
            headers['Cookie'] = 'DSI=' + self.session.cookies.get_dict().get('DSI', '')
            response = self.session.get(href_value, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            element = soup.find('a', id='link-account-balance')

            if element:
                href_value = "https://my.101domain.com" + element['href']
                response = self.session.get(href_value, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                element = soup.find('div', class_='account-balance')

                if element:
                    account_balance = element.text.replace("Account Balance", "").replace("USD", "").replace(" ", "").replace(",", "")
                    return account_balance

        return None

client = Domain101Client(username='USERNAME', password='PASSWORD')

app = Flask(__name__)
@app.route('/', methods=['GET'])
def get_balance():
    if client.login():
        account_balance = client.get_account_balance()
        if account_balance:
            return jsonify({
                'STATUS': 'OK',
                'BALANCE': account_balance
            })
        else:
            return jsonify({
                'STATUS': 'ERR',
                'MSG': 'ACCOUNT BALANCE NOT FOUND'
            })
    else:
        return jsonify({
            'STATUS': 'ERR',
            'MSG': 'LOGIN FAILED'
        })

app.run(host="0.0.0.0", port=1106)
