import string
import secrets
import json
import os
from cryptography.fernet import Fernet
from nicegui import ui
import logging

DATA_FILE = "passwords_vault.json"
KEY_FILE = "secret.key"

def load_or_create_key() -> bytes:
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key
    
    with open(KEY_FILE, "rb") as f:
        return f.read()

def get_vault_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_password(service_name: str, plain_password: str) -> bool:
    vault = get_vault_data()
    
    if service_name in vault:
        ui.notify(f"⚠️ Error: '{service_name}' already exists in the vault!", type='negative')
        return False

    key = load_or_create_key()
    cipher = Fernet(key)
    
    encrypted_bytes = cipher.encrypt(plain_password.encode('utf-8'))
    vault[service_name] = encrypted_bytes.decode('utf-8')
    
    with open(DATA_FILE, "w") as f:
        json.dump(vault, f, indent=4)
        
    ui.notify(f"✅ Successfully saved password for '{service_name}'.", type='positive')
    return True

def handle_delete(delname, target_card):
    with ui.dialog() as confirm_dialog, ui.card().classes('items-center text-center p-6 bg-grey-10 text-white'):
        ui.html('''
            <lottie-player 
                src="https://lottie.host/7e0b5710-1845-48b0-8a16-d446973167df/V0Dq1i8j7L.json" 
                background="transparent" 
                speed="1" 
                style="width: 250px; height: 250px;" 
                autoplay>
            </lottie-player>
        ''')

        ui.label(f"YOU WILL DELETE {delname}⚠").classes('text-3xl text-red')
        ui.notify(f"YOU WILL DELETE {delname}⚠", type='warning')
        
        ui.button("'DELETE 🗑️", color='red', on_click=lambda y=delname, z=target_card, d=confirm_dialog: delete(y, z, d))
    
    confirm_dialog.open()

def delete(x, c, d):
    vault = get_vault_data()
    vault.pop(x, None)
    
    with open(DATA_FILE, 'w') as f:
        json.dump(vault, f, indent=4)
        
    c.delete()
    d.close()

def print_vault_file():
    if not os.path.exists(DATA_FILE):
        ui.notify("⚠️ Vault file 'passwords_vault.json' does not exist yet.", type='negative')
        return

    key = load_or_create_key()
    cipher = Fernet(key)

    with open(DATA_FILE, "r") as f:
        content = json.load(f)

    with ui.column().classes('w-full justify-start items-stretch gap-4 p-4'):
        for name_key, encrypted_password in content.items():
            try:
                decrypted_bytes = cipher.decrypt(encrypted_password.encode('utf-8'))
                real_password = decrypted_bytes.decode('utf-8')

                cardpass = ui.card().style("background-color: #16211D")
                with cardpass:
                    with ui.row():
                        ui.label(name_key).classes('text-2xl text-blue')
                    ui.label(real_password).classes('text-xl text-white')
                    with ui.row():
                        ui.button("🗐 copy", color='green', on_click=lambda p=real_password: ui.clipboard.write(p))
                        ui.button('DELETE 🗑️', color='red', on_click=lambda m=name_key, c=cardpass: handle_delete(m, c))
            except Exception as e:
                ui.notify(f"Error decrypting {name_key}", type='negative')

ui.add_head_html("""
<style>
    body{
    background-color:#0D1210
    }
</style>
""")

with ui.dialog() as dialog, ui.card().classes('items-center text-center p-6 bg-grey-10 text-white'):
    ui.html('''
        <lottie-player 
            src="https://lottie.host/7e0b5710-1845-48b0-8a16-d446973167df/V0Dq1i8j7L.json" 
            background="transparent" 
            speed="1" 
            style="width: 250px; height: 250px;" 
            autoplay>
        </lottie-player>
    ''')

    ui.label("ENTER NAME FOR PASSWORD").classes('text-3xl text-yellow')
    name = ui.input('NAME').classes('bg-red')
    ui.button("save", icon='save', color='green', on_click=lambda: savecard())

with ui.header().classes('justify-end').style("color: #0D1210;background: #0D1210"):
    exit = ui.button('╰┈➤EXIT➡🚪', on_click=lambda: ui.navigate.to('/'), icon='home', color='red').classes('px-2 py-0.5 text-xs h-6 min-h-0 text-black')
    exit.set_visibility(False)

with ui.card().classes("w-full").style("background-color: #16211D"):
    with ui.row().classes("w-full justify-center text-l text-green"):
        ui.label("RANDOM PASSWORD GENERATOR").style("""
            font-family: Georgia, 'Times New Roman', serif;
            font-weight: 900;
            letter-spacing: 2px;
        """).classes('text-6xl p-6 text-white')

ui.label("")
ui.label("")

with ui.row().classes("w-full justify-center gap-50"):
    new = ui.button("GENERATE NEW ONE", color=None, on_click=lambda: newpassword()).classes("text-4xl text-white").style("background-color:#16211D")
    saved = ui.button("SAVED PASSWORDS", color=None, on_click=lambda: savedpassword()).classes("text-4xl text-white").style("background-color:#16211D")

def newpassword():
    global saved, new, lenght, cards, num, letter, sp, card, result_label
    saved.set_visibility(False)
    new.set_visibility(False)
    exit.set_visibility(True)
    card = ui.card().classes('w-full items-center justify-center p-8').style('background-color: #16211D')
    
    with card:
        with ui.column():
            num = ui.checkbox("Numbers", value=True).classes("text-white text-3xl")
            letter = ui.checkbox("Letters").classes("text-white text-3xl")
            with ui.row():
                sp = ui.checkbox("""Special Characters""").classes("text-white text-3xl")
                ui.label("""[
            ! @ # $ % ^ & * ( ) _ + - = { } [ ] | \\ : ; " ' < > , . ? / ~ `]""").classes('text-xl text-[#7C8F86]')
            ui.label("")
            ui.label("LENGHT OF PASSWORD").classes("text-yellow text-2xl")
            lenght = ui.number(value=4, min=4, max=100000, precision=0) \
                .props('outlined dense dark no-error-icon') \
                .classes('w-20 bg-[#0a1210] rounded-lg text-center font-bold text-white') \
                .style('border: 1px solid #1a332c;')
            ui.button("GENERATE", on_click=lambda: generate(), color='yellow').classes('text-black text-xl')

def generate():
    global cards, lenght, num, letter, sp, card, result_label, copy
    result_label = ui.label('').classes('text-lg font-bold text-primary')
    if lenght.value == "":
        lenght.props('color="negative" error-message="Wrong input!" error=true')
        ui.notify("SET LENGHT OF PASSWORD 4 OR UPPER", type='warning')
    elif int(lenght.value) >= 4:
        lenght.props('color="positive" error-message="" error=false')
        
        card.clear()
        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        digits = string.digits
        symbols = string.punctuation
        password = []
        all_characters = ""
        x = 0
        if num.value:
            all_characters += digits
            password.append(secrets.choice(digits))
            x += 1
        if letter.value:
            all_characters += lower + upper
            password.append(secrets.choice(lower)) 
            password.append(secrets.choice(upper)) 
            x += 2
        if sp.value:
            all_characters += symbols     
            password.append(secrets.choice(symbols)) 
            x += 1

        password += [secrets.choice(all_characters) for _ in range(int(lenght.value) - x)]
        secrets.SystemRandom().shuffle(password)

        with card:
            with ui.card().classes('p-6 bg-red shadow-md'):
                copy = ''.join(password)
                result_label = ui.label(''.join(password)).classes('text-2xl font-bold text-black')
            with ui.row().classes('justify-start'):
                ui.button("⿻ COPY", color='blue', on_click=lambda: [ui.clipboard.write(copy), ui.notify("copied", type='info')])
                ui.button("SAVE", icon='save', color='green', on_click=lambda: dialog.open())
    else:
        lenght.props('color="negative" error-message="Wrong input!" error=true')
        ui.notify("SET LENGHT OF PASSWORD 4 OR UPPER", type='warning')

def savecard():
    if name.value == "":
        ui.notify("ENTER NAME!", type='warning')
    else:
        save_password(name.value, copy)
        dialog.close()

def save():
    pass

def savedpassword():
    global saved, new
    saved.set_visibility(False)
    new.set_visibility(False)
    exit.set_visibility(True)
    print_vault_file()
logging.getLogger('nicegui').setLevel(logging.ERROR)

port = int(os.environ.get("PORT", 8080))

ui.run(host="0.0.0.0", port=port, reload=False)