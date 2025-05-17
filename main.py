from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
import openpyxl
import os
from datetime import datetime

# Estados de la conversación
MODELO, CLIENTE, FECHA, DESCRIPCION, TELEFONO, PRECIO, GANANCIA = range(7)

# Ruta del archivo Excel
EXCEL_PATH = "CELL.xlsx"

# Asegurar que el archivo Excel exista con encabezados
if not os.path.exists(EXCEL_PATH):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Modelo", "Cliente", "Fecha", "Descripción", "Teléfono", "Precio", "Ganancia"])
    wb.save(EXCEL_PATH)

# Función para iniciar la conversación
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Vamos a sacar tu turno.\n¿Qué modelo de celular querés reparar?")
    return MODELO

async def modelo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['modelo'] = update.message.text
    await update.message.reply_text("Nombre del cliente:")
    return CLIENTE

async def cliente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cliente'] = update.message.text
    await update.message.reply_text("Fecha del turno (dd/mm/aaaa):")
    return FECHA

async def fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        fecha = datetime.strptime(update.message.text, "%d/%m/%Y")
        context.user_data['fecha'] = fecha.strftime("%d/%m/%Y")
        await update.message.reply_text("¿Qué reparación necesita?")
        return DESCRIPCION
    except ValueError:
        await update.message.reply_text("⚠️ Fecha inválida. Usá el formato dd/mm/aaaa:")
        return FECHA

async def descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['descripcion'] = update.message.text
    await update.message.reply_text("Número de teléfono:")
    return TELEFONO

async def telefono(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['telefono'] = update.message.text
    await update.message.reply_text("Precio estimado:")
    return PRECIO

async def precio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['precio'] = update.message.text
    await update.message.reply_text("Ganancia estimada:")
    return GANANCIA

async def ganancia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ganancia'] = update.message.text

    try:
        wb = openpyxl.load_workbook(EXCEL_PATH)
        ws = wb.active
        ws.append([
            context.user_data['modelo'],
            context.user_data['cliente'],
            context.user_data['fecha'],
            context.user_data['descripcion'],
            context.user_data['telefono'],
            context.user_data['precio'],
            context.user_data['ganancia']
        ])
        wb.save(EXCEL_PATH)
        await update.message.reply_text("✅ ¡Turno registrado correctamente!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al guardar los datos: {e}")
    
    return ConversationHandler.END

# Cancelar la conversación
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Operación cancelada.")
    return ConversationHandler.END

# Token del bot
BOT_TOKEN = "8167419850:AAGPxEXwDHP82n68edrsL5GaLuR040X5a9Y"

# Función principal
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MODELO: [MessageHandler(filters.TEXT & ~filters.COMMAND, modelo)],
            CLIENTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cliente)],
            FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, fecha)],
            DESCRIPCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, descripcion)],
            TELEFONO: [MessageHandler(filters.TEXT & ~filters.COMMAND, telefono)],
            PRECIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, precio)],
            GANANCIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ganancia)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("🤖 Bot corriendo... Esperando mensajes.")
    app.run_polling()

if __name__ == "__main__":
    main()
