import json
import os
import requests
import wikipedia
import base64
from googletrans import Translator, LANGUAGES
from typing import Dict, Any, Optional, List
from config import GEMINI_API_KEY

def gemini_chat(prompt):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def gemini_vision_analyze(image_path: str, prompt: str = "Describe what you see in this image in detail"):
    """Analyze image using Gemini Vision API"""
    try:
        # Read and encode image to base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode()
        
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }]
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "I couldn't analyze this image. Please try again."
            
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

class AIServices:
    def __init__(self):
        # Initialize translator per request to avoid connection issues
        self.translator = None
        wikipedia.set_lang("en")
    
    def chat_with_ai(self, message: str, user_id: str) -> str:
        """Chat with Gemini AI (default)"""
        try:
            prompt = f"You are a helpful AI assistant in a Telegram bot. Provide concise, accurate, and friendly responses. Keep responses under 1000 characters when possible.\n\nUser: {message}"
            response = gemini_chat(prompt)
            
            # Extract text from response
            if 'candidates' in response and len(response['candidates']) > 0:
                content = response['candidates'][0]['content']['parts'][0]['text']
                return content
            else:
                return "I'm having trouble processing your request right now."
                
        except Exception as e:
            return f"❌ Gemini Error: {str(e)}"
    
    def chat_with_gemini(self, message: str, user_id: str) -> str:
        """Chat with Google Gemini with humor and personality"""
        try:
            prompt = f"""You are a fun, witty, and engaging AI assistant with a great sense of humor. You should:
- Add appropriate jokes, puns, and witty comments to your responses
- Use playful language and creative expressions  
- Include light humor and wordplay when suitable
- Be entertaining while still being helpful
- Use casual, friendly tone with personality
- Add funny observations or comparisons
- Keep it appropriate and family-friendly
- Make conversations enjoyable and memorable
- Use emojis and fun expressions
- Tell jokes when appropriate
- Be clever and creative with responses

Provide concise, accurate, and entertaining responses. Keep responses under 1000 characters when possible.

User: {message}"""
            response = gemini_chat(prompt)
            
            # Extract text from response
            if 'candidates' in response and len(response['candidates']) > 0:
                content = response['candidates'][0]['content']['parts'][0]['text']
                return content
            else:
                funny_errors = [
                    "Oops! My brain.exe has stopped working. Have you tried turning me off and on again? 🤖",
                    "Error 404: Humor not found... wait, that was a joke! But seriously, I'm having issues. Try again! 😄",
                    "My comedy circuits are sparking! Give me a moment to reboot. 🔧",
                    "I was about to tell you a joke about UDP, but you might not get it... Also, I'm broken right now! 😅"
                ]
                import random
                return random.choice(funny_errors)
                
        except Exception as e:
            return f"❌ Gemini Error: Even my error messages are funnier than this! {str(e)} 😂"
    
    def search_wikipedia(self, query: str) -> str:
        """Search Wikipedia for information"""
        try:
            # Search for articles
            search_results = wikipedia.search(query, results=3)
            if not search_results:
                return f"❌ No Wikipedia articles found for '{query}'"
            
            # Get the first article
            try:
                page = wikipedia.page(search_results[0])
                title = page.title
                summary = wikipedia.summary(search_results[0], sentences=3)
                url = page.url
                
                response = f"📖 **{title}**\n\n{summary}\n\n🔗 [Read more]({url})"
                
                # Add related articles if available
                if len(search_results) > 1:
                    related = ", ".join(search_results[1:3])
                    response += f"\n\n**Related articles:** {related}"
                
                return response
                
            except wikipedia.DisambiguationError as e:
                # Handle disambiguation
                options = e.options[:5]
                response = f"🔍 Multiple articles found for '{query}':\n\n"
                for i, option in enumerate(options, 1):
                    response += f"{i}. {option}\n"
                response += f"\nTry searching for a more specific term."
                return response
                
        except Exception as e:
            return f"❌ Wikipedia Error: {str(e)}"
    
    def educational_qa(self, question: str) -> str:
        """Answer educational questions using Gemini AI"""
        try:
            educational_prompt = f"""You are an educational AI tutor. Answer this question in a clear, educational manner suitable for students. Include:
1. A direct answer
2. A brief explanation
3. An example if applicable
4. Related concepts to explore

Keep the response under 1500 characters.

Question: {question}"""

            response = gemini_chat(educational_prompt)
            
            # Extract text from response
            if 'candidates' in response and len(response['candidates']) > 0:
                content = response['candidates'][0]['content']['parts'][0]['text']
                return f"🎓 **Educational Answer**\n\n{content}"
            else:
                return "I'm having trouble processing your educational question right now."
            
        except Exception as e:
            return f"❌ Unable to process educational question: {str(e)}"
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        """Translate text between languages"""
        try:
            # Validate target language
            if target_lang not in LANGUAGES:
                available_langs = list(LANGUAGES.keys())[:10]
                return f"❌ Unsupported language '{target_lang}'. Available languages include: {', '.join(available_langs)}..."
            
            # Reinitialize translator to avoid coroutine issues
            from googletrans import Translator
            translator = Translator()
            
            # Perform translation with retry logic
            try:
                result = translator.translate(text, dest=target_lang, src=source_lang)
                
                # Ensure result is not a coroutine
                if hasattr(result, '__await__'):
                    # If it's async, use a different approach
                    import asyncio
                    if asyncio.iscoroutine(result):
                        # Handle async case - but googletrans should be sync
                        return f"❌ Translation service temporarily unavailable. Please try again."
                
                # Extract source language safely
                detected_src = getattr(result, 'src', source_lang)
                translated_text = getattr(result, 'text', text)
                
                # Format response
                source_language = LANGUAGES.get(detected_src, detected_src).title()
                target_language = LANGUAGES.get(target_lang, target_lang).title()
                
                response = f"🌐 **Translation**\n\n"
                response += f"**From:** {source_language}\n"
                response += f"**To:** {target_language}\n\n"
                response += f"**Original:** {text}\n\n"
                response += f"**Translation:** {translated_text}"
                
                return response
                
            except Exception as translation_error:
                # Fallback to simple response if detailed translation fails
                return f"❌ Translation failed: {str(translation_error)}"
            
        except Exception as e:
            return f"❌ Translation Error: {str(e)}"
    
    def get_supported_languages(self) -> str:
        """Get list of supported languages for translation"""
        lang_list = []
        for code, name in list(LANGUAGES.items())[:20]:  # Show first 20
            lang_list.append(f"`{code}` - {name.title()}")
        
        response = "🌐 **Supported Languages** (first 20):\n\n"
        response += "\n".join(lang_list)
        response += f"\n\n**Total:** {len(LANGUAGES)} languages supported"
        response += "\n\nUse language codes (e.g., `en`, `es`, `fr`) with the translate command."
        
        return response

    def get_crypto_price(self, symbol: str) -> str:
        """Get current cryptocurrency price and basic info"""
        try:
            import requests
            
            # Use CoinGecko API (free, no API key required)
            symbol = symbol.lower()
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                # Try with common symbol mappings
                symbol_map = {
                    'btc': 'bitcoin',
                    'eth': 'ethereum', 
                    'bnb': 'binancecoin',
                    'ada': 'cardano',
                    'sol': 'solana',
                    'xrp': 'ripple',
                    'dot': 'polkadot',
                    'doge': 'dogecoin',
                    'avax': 'avalanche-2',
                    'matic': 'matic-network',
                    'link': 'chainlink',
                    'uni': 'uniswap',
                    'ltc': 'litecoin',
                    'atom': 'cosmos',
                    'icp': 'internet-computer'
                }
                
                if symbol in symbol_map:
                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol_map[symbol]}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
                    response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    coin_id = list(data.keys())[0]
                    coin_data = data[coin_id]
                    
                    price = coin_data.get('usd', 0)
                    change_24h = coin_data.get('usd_24h_change', 0)
                    market_cap = coin_data.get('usd_market_cap', 0)
                    
                    change_emoji = "📈" if change_24h >= 0 else "📉"
                    change_color = "🟢" if change_24h >= 0 else "🔴"
                    
                    # Format market cap
                    if market_cap > 1000000000:
                        market_cap_str = f"${market_cap/1000000000:.2f}B"
                    elif market_cap > 1000000:
                        market_cap_str = f"${market_cap/1000000:.2f}M"
                    else:
                        market_cap_str = f"${market_cap:,.2f}"
                    
                    return f"""💰 **{symbol.upper()} Price Update**

💵 **Current Price:** ${price:,.4f}
{change_emoji} **24h Change:** {change_color} {change_24h:+.2f}%
📊 **Market Cap:** {market_cap_str}

*Data from CoinGecko*"""
                
            return f"❌ Could not find price data for {symbol.upper()}. Try common symbols like BTC, ETH, ADA, SOL, etc."
            
        except Exception as e:
            return f"❌ Error fetching crypto data: {str(e)}"

    def get_crypto_prediction(self, symbol: str) -> str:
        """Generate AI-powered crypto price prediction and analysis"""
        try:
            # First get current price data
            current_data = self.get_crypto_price(symbol)
            
            if "❌" in current_data:
                return current_data
            
            # Generate AI prediction using current market data
            prediction_prompt = f"""You are a cryptocurrency market analyst. Based on the following current data for {symbol.upper()}, provide a detailed price prediction and market analysis.

Current data: {current_data}

Provide:
1. Short-term prediction (1-7 days)
2. Medium-term outlook (1-4 weeks) 
3. Key factors affecting price
4. Support and resistance levels
5. Risk assessment
6. Trading suggestions

Be realistic and mention this is speculative analysis, not financial advice. Use technical analysis concepts and market trends."""

            prediction = self.chat_with_gemini(prediction_prompt, "crypto_analysis")
            
            return f"""🔮 **{symbol.upper()} Price Prediction & Analysis**

{current_data}

---

🧠 **AI Market Analysis:**

{prediction}

---

⚠️ **Disclaimer:** This is AI-generated analysis for educational purposes only. Not financial advice. Always do your own research before investing."""

        except Exception as e:
            return f"❌ Error generating prediction: {str(e)}"

    def get_crypto_portfolio(self, symbols: list) -> str:
        """Get portfolio overview for multiple cryptocurrencies"""
        try:
            portfolio_data = []
            
            for symbol in symbols[:10]:  # Limit to 10 coins
                try:
                    import requests
                    symbol_lower = symbol.lower()
                    
                    # Symbol mapping for common coins
                    symbol_map = {
                        'btc': 'bitcoin', 'eth': 'ethereum', 'bnb': 'binancecoin',
                        'ada': 'cardano', 'sol': 'solana', 'xrp': 'ripple',
                        'dot': 'polkadot', 'doge': 'dogecoin', 'avax': 'avalanche-2',
                        'matic': 'matic-network', 'link': 'chainlink', 'uni': 'uniswap'
                    }
                    
                    coin_id = symbol_map.get(symbol_lower, symbol_lower)
                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
                    
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            coin_data = list(data.values())[0]
                            price = coin_data.get('usd', 0)
                            change = coin_data.get('usd_24h_change', 0)
                            
                            change_emoji = "📈" if change >= 0 else "📉"
                            portfolio_data.append(f"{symbol.upper()}: ${price:.4f} {change_emoji} {change:+.2f}%")
                
                except:
                    portfolio_data.append(f"{symbol.upper()}: Data unavailable")
            
            if portfolio_data:
                return f"""📊 **Crypto Portfolio Overview**

{chr(10).join(portfolio_data)}

*Updated just now from CoinGecko*"""
            else:
                return "❌ No valid cryptocurrency symbols found"
                
        except Exception as e:
            return f"❌ Error fetching portfolio data: {str(e)}"
    
    def analyze_image(self, image_path: str, user_question: Optional[str] = None) -> str:
        """Analyze image using Gemini Vision API based on user's question"""
        try:
            if not os.path.exists(image_path):
                return "❌ Image file not found for analysis."
            
            # Create appropriate prompt based on user's question
            if user_question:
                # Check if user is asking about the image content
                question_lower = user_question.lower()
                if any(phrase in question_lower for phrase in [
                    'what', 'describe', 'see', 'show', 'tell me about', 
                    'what is', 'what are', 'analyze', 'explain', 'identify'
                ]):
                    prompt = f"The user is asking: '{user_question}'. Please analyze this image and provide a detailed response to their question."
                else:
                    prompt = user_question
            else:
                prompt = "Describe what you see in this image in detail, including objects, people, colors, setting, and any notable features."
            
            result = gemini_vision_analyze(image_path, prompt)
            return f"🖼️ **Image Analysis:**\n\n{result}"
            
        except Exception as e:
            return f"❌ Error analyzing image: {str(e)}"
    
    def analyze_video_frame(self, video_path: str, user_question: Optional[str] = None) -> str:
        """Analyze video by extracting a frame and analyzing it"""
        try:
            if not os.path.exists(video_path):
                return "❌ Video file not found for analysis."
            
            # For now, we'll provide a response about video analysis capability
            # In the future, this could extract frames using FFmpeg
            if user_question:
                question_lower = user_question.lower()
                if any(phrase in question_lower for phrase in [
                    'what', 'describe', 'see', 'show', 'tell me about',
                    'what is', 'what are', 'analyze', 'explain', 'identify'
                ]):
                    return f"🎥 **Video Analysis:**\n\nI can see you've uploaded a video and you're asking: '{user_question}'. While I can download and store your video, detailed frame-by-frame analysis is coming soon. For now, I can tell you that your video has been safely stored and I can provide general information about video files."
            
            return "🎥 **Video received:** I can see your video and have stored it for analysis. Advanced video content analysis is coming soon!"
            
        except Exception as e:
            return f"❌ Error analyzing video: {str(e)}"

# Global instance
ai_services = AIServices()
