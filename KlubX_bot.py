import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from datetime import datetime
import traceback

# Token del tuo bot Telegram
TOKEN = '6684007630:AAFm6n9xe-Ct07mJSu2q4BQpHmR_145ttVk'

# Dizionario per memorizzare gli eventi (gli inserisce solo lo sviluppatore del bot)
eventi = {}

# Funzione per gestire il comando /start
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Elenca Eventi", callback_data='elenca')],
        [InlineKeyboardButton("Cerca Evento", callback_data='cerca')],
        [InlineKeyboardButton("Eventi oggi", callback_data='oggi')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Benvenuto! Scegli un'opzione:", reply_markup=reply_markup)

# Funzione per gestire il callback della tastiera inline
def button(update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'elenca':
        elenca_eventi(query.message)
    elif query.data == 'cerca':
        query.message.reply_text("Inserisci la data in formato gg/mm/aaaa per cercare gli eventi (es. 21/04/2024):")
        # Imposta lo stato per indicare che l'utente sta inserendo la data per la ricerca
        context.user_data['cerca_data'] = True
    elif query.data == 'oggi':
        eventi_oggi = {evento: info for evento, info in eventi.items() if info['data'].date() == datetime.now().date()}
        if eventi_oggi:
            text = "Eventi oggi:\n"
            for evento, info in eventi_oggi.items():
                text += f"{evento}: {info['descrizione']}\n"
        else:
            text = "Nessun evento programmato per oggi."
        query.message.reply_text(text)

# Funzione per gestire i messaggi testuali
def text_message(update, context):
    # Se lo stato indica che l'utente sta cercando un evento, cerca per quella data
    if 'cerca_data' in context.user_data and context.user_data['cerca_data']:
        data_cercata = update.message.text.strip()
        try:
            data_cercata = datetime.strptime(data_cercata, '%d/%m/%Y')
        except ValueError:
            update.message.reply_text("Formato data non valido. Utilizza il formato gg/mm/aaaa.")
            return
        
        eventi_trovati = [evento for evento, info in eventi.items() if info['data'].date() == data_cercata.date()]
        
        if eventi_trovati:
            text = f"Eventi in programma il {data_cercata.strftime('%d/%m/%Y')}:\n"
            for evento in eventi_trovati:
                text += f"{evento}: {eventi[evento]['descrizione']}\n"
            update.message.reply_text(text)
        else:
            update.message.reply_text(f"Nessun evento programmato per il {data_cercata.strftime('%d/%m/%Y')}.")
        
        # Reset dello stato di ricerca
        del context.user_data['cerca_data']
    else:
        update.message.reply_text("Comando non valido. Usa /help per vedere i comandi disponibili.")

# Funzione per gestire il comando /help
def help_command(update, context):
    help_text = """
    Questo bot ti aiuta a gestire gli eventi e le serate in città.
    Ecco i comandi disponibili:
    /start - Avvia il bot
    /help - Mostra l'elenco dei comandi disponibili
    /elenca - Mostra tutti gli eventi in ordine cronologico
    /cerca <data> - Cerca gli eventi in una data specifica (formato: gg/mm/aaaa)
    /stop - Arresta il bot
    """
    update.message.reply_text(help_text)

# Comando per elencare gli eventi in ordine cronologico
def elenca_eventi(message):
    if not eventi:
        message.reply_text("Nessun evento programmato al momento.")
        return
    
    elenco_eventi = sorted(eventi.items(), key=lambda x: x[1]['data'])
    text = "Eventi in programma:\n"
    for evento, info in elenco_eventi:
        text += f"{evento}: {info['data'].strftime('%d/%m/%Y')} - {info['descrizione']}\n"
    message.reply_text(text)

# Comando per cercare un evento in una data specifica
def cerca_evento(update, context):
    if not context.args:
        update.message.reply_text("Utilizzo: /cerca <data>. Es. /cerca 21/04/2024")
        return
    
    data_cercata = context.args[0]
    try:
        data_cercata = datetime.strptime(data_cercata, '%d/%m/%Y')
    except ValueError:
        update.message.reply_text("Formato data non valido. Utilizza il formato gg/mm/aaaa.")
        return
    
    eventi_trovati = [evento for evento, info in eventi.items() if info['data'].date() == data_cercata.date()]
    
    if eventi_trovati:
        text = f"Eventi in programma il {data_cercata.strftime('%d/%m/%Y')}:\n"
        for evento in eventi_trovati:
            text += f"{evento}: {eventi[evento]['descrizione']}\n"
        update.message.reply_text(text)
    else:
        update.message.reply_text(f"Nessun evento programmato per il {data_cercata.strftime('%d/%m/%Y')}.")

# Funzione per leggere gli eventi da un canale Telegram
def leggi_eventi_da_canale():
    try:
        # Sostituisci CHANNEL_ID con l'ID effettivo del canale Telegram
        messages = updater.bot.get_chat_history(chat_id='testeventsbottt', limit=20)
        
        for message in messages:
            # Consideriamo solo i messaggi di testo
            if message.text:
                lines = message.text.split('\n')
                if len(lines) >= 2:
                    data_str = lines[0]
                    descrizione = '\n'.join(lines[1:])
                    try:
                        data = datetime.strptime(data_str, '%d/%m/%Y')
                        # Aggiungi l'evento al dizionario
                        eventi[message.message_id] = {'data': data, 'descrizione': descrizione}
                    except ValueError:
                        # Ignora i messaggi con data non valida
                        pass
    except Exception as e:
        print("Errore durante la lettura del canale:", e)


# Aggiungi altri comandi e funzioni come elenca_eventi, start, help_command, stop, ecc.

# Handler per gestire comandi non validi
def unknown(update, context):
    update.message.reply_text("Comando non valido. Usa /help per vedere i comandi disponibili.")

# Comando per arrestare il bot
def stop(update, context):
    update.message.reply_text("Bot arrestato.")
    updater.stop()

def main():
    global updater
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("elenca", elenca_eventi))
    dp.add_handler(CommandHandler("cerca", cerca_evento))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message))
    dp.add_handler(CallbackQueryHandler(button))

    # Leggi gli eventi dal canale all'avvio del bot
    leggi_eventi_da_canale()

    try:
        updater.start_polling()
        updater.idle()
    except Exception as e:
        # Invia una traccia degli errori al log e avvisa l'utente
        traceback.print_exc()
        updater.bot.send_message(ADMIN_CHAT_ID, f"Si è verificato un errore:\n\n{traceback.format_exc()}")

if __name__ == '__main__':
    main()
