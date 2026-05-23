import discord
from discord import app_commands
from discord.ext import commands
import os
import httpx

class UniversalBot(commands.Bot):
    def __init__(self, ai_key=None):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.ai_key = ai_key # This is automatically detected

    async def setup_hook(self):
        # Add a dynamic AI command if a key exists
        if self.ai_key:
            print("✨ AI Key detected! Enabling AI features...")
            @self.tree.command(name="ask", description="Ask the AI anything")
            async def ask(interaction: discord.Interaction, question: str):
                await interaction.response.defer()
                # Example for Groq/OpenAI compatible API
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {self.ai_key}"}
                    # Simplified logic - you can expand this per AI provider
                    payload = {"model": "mixtral-8x7b-32768", "messages": [{"role": "user", "content": question}]}
                    try:
                        resp = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
                        answer = resp.json()['choices'][0]['message']['content']
                        await interaction.followup.send(answer[:2000])
                    except:
                        await interaction.followup.send("❌ AI request failed. Check API key.")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"🚀 Bot {self.user.name} is now hosting successfully!")
        await self.tree.sync()

# This is how you would start one bot instance manually
if __name__ == "__main__":
    # In production, these are pulled from your Database
    TOKEN = os.getenv("CUSTOMER_TOKEN")
    AI_KEY = os.getenv("CUSTOMER_AI_KEY")
    
    bot = UniversalBot(ai_key=AI_KEY)
    bot.run(TOKEN)
