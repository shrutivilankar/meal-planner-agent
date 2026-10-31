from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
from workflow import generate_meal_plan, maintainRecipes
import io





async def generate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /generate command."""
    # Call the generate_meal_plan function and get the result
    result = await generate_meal_plan()
    
    file = result["recipeFile"]
    print(f"Generated Meal Plan: {file}")  # Log the result for debugging
    
    #return await update.message.reply_text(formatted_recipe)
        # Send the result back to the user
    await update.message.reply_document(document=file)

    maintainRecipes(file)

    return 
     



def create_bot_app():
    """Create and return the Telegram bot application."""
    bot_app = Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    bot_app.add_handler(CommandHandler("generate", generate_handler))
    return bot_app

