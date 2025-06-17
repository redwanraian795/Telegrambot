import json
import requests
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import random

class PublicAPIService:
    """Integration with authentic public APIs for real data"""
    
    def __init__(self):
        self.session = None
        self.api_endpoints = {
            # News APIs
            "newsapi": "https://newsapi.org/v2/top-headlines",
            "guardian": "https://content.guardianapis.com/search",
            
            # Weather APIs
            "openweather": "https://api.openweathermap.org/data/2.5/weather",
            "weatherapi": "https://api.weatherapi.com/v1/current.json",
            
            # Entertainment APIs
            "tmdb": "https://api.themoviedb.org/3",
            "spotify": "https://api.spotify.com/v1",
            "omdb": "https://www.omdbapi.com",
            
            # Educational APIs
            "wikipedia": "https://en.wikipedia.org/api/rest_v1",
            "quotable": "https://api.quotable.io/random",
            "numbersapi": "http://numbersapi.com",
            
            # Finance APIs
            "coindesk": "https://api.coindesk.com/v1/bpi/currentprice.json",
            "exchangerate": "https://api.exchangerate-api.com/v4/latest",
            
            # Fun APIs
            "catfacts": "https://catfact.ninja/fact",
            "dogapi": "https://dog.ceo/api/breeds/image/random",
            "advice": "https://api.adviceslip.com/advice",
            "jokes": "https://official-joke-api.appspot.com/random_joke",
            "facts": "https://uselessfacts.jsph.pl/random.json?language=en",
            
            # Science APIs
            "nasa": "https://api.nasa.gov/planetary/apod",
            "spacex": "https://api.spacexdata.com/v4/launches/latest",
            
            # Utility APIs
            "ipapi": "https://ipapi.co/json",
            "qrcode": "https://api.qrserver.com/v1/create-qr-code",
            "urlshortener": "https://is.gd/create.php"
        }
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_news(self, category: str = "general", country: str = "us") -> Dict[str, Any]:
        """Get latest news from NewsAPI (requires API key)"""
        try:
            # Using free alternative: Guardian API
            url = f"{self.api_endpoints['guardian']}?order-by=newest&show-fields=headline,trailText&page-size=10"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        
                        for item in data.get('response', {}).get('results', [])[:5]:
                            articles.append({
                                'title': item.get('webTitle', ''),
                                'description': item.get('fields', {}).get('trailText', ''),
                                'url': item.get('webUrl', ''),
                                'published': item.get('webPublicationDate', '')
                            })
                        
                        return {
                            'success': True,
                            'articles': articles,
                            'source': 'The Guardian',
                            'category': category
                        }
            
            return {"error": "Failed to fetch news"}
            
        except Exception as e:
            return {"error": f"News API error: {str(e)}"}
    
    async def get_weather(self, city: str) -> Dict[str, Any]:
        """Get weather data (using free APIs)"""
        try:
            # Using wttr.in - free weather API
            url = f"https://wttr.in/{city}?format=j1"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        current = data.get('current_condition', [{}])[0]
                        
                        return {
                            'success': True,
                            'city': city,
                            'temperature': current.get('temp_C', 'N/A'),
                            'description': current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                            'humidity': current.get('humidity', 'N/A'),
                            'wind_speed': current.get('windspeedKmph', 'N/A'),
                            'feels_like': current.get('FeelsLikeC', 'N/A'),
                            'source': 'wttr.in'
                        }
            
            return {"error": "Weather data not available"}
            
        except Exception as e:
            return {"error": f"Weather API error: {str(e)}"}
    
    async def get_quote(self) -> Dict[str, Any]:
        """Get inspirational quote"""
        try:
            url = self.api_endpoints['quotable']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'quote': data.get('content', ''),
                            'author': data.get('author', ''),
                            'tags': data.get('tags', [])
                        }
            
            return {"error": "Quote not available"}
            
        except Exception as e:
            return {"error": f"Quote API error: {str(e)}"}
    
    async def get_cat_fact(self) -> Dict[str, Any]:
        """Get random cat fact"""
        try:
            url = self.api_endpoints['catfacts']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'fact': data.get('fact', ''),
                            'length': data.get('length', 0)
                        }
            
            return {"error": "Cat fact not available"}
            
        except Exception as e:
            return {"error": f"Cat fact API error: {str(e)}"}
    
    async def get_dog_image(self) -> Dict[str, Any]:
        """Get random dog image"""
        try:
            url = self.api_endpoints['dogapi']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'image_url': data.get('message', ''),
                            'status': data.get('status', '')
                        }
            
            return {"error": "Dog image not available"}
            
        except Exception as e:
            return {"error": f"Dog API error: {str(e)}"}
    
    async def get_advice(self) -> Dict[str, Any]:
        """Get random advice"""
        try:
            url = self.api_endpoints['advice']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'advice': data.get('slip', {}).get('advice', ''),
                            'id': data.get('slip', {}).get('id', '')
                        }
            
            return {"error": "Advice not available"}
            
        except Exception as e:
            return {"error": f"Advice API error: {str(e)}"}
    
    async def get_joke(self) -> Dict[str, Any]:
        """Get random joke"""
        try:
            url = self.api_endpoints['jokes']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'setup': data.get('setup', ''),
                            'punchline': data.get('punchline', ''),
                            'type': data.get('type', ''),
                            'id': data.get('id', '')
                        }
            
            return {"error": "Joke not available"}
            
        except Exception as e:
            return {"error": f"Joke API error: {str(e)}"}
    
    async def get_fun_fact(self) -> Dict[str, Any]:
        """Get random fun fact"""
        try:
            url = self.api_endpoints['facts']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'fact': data.get('text', ''),
                            'source': data.get('source', ''),
                            'source_url': data.get('source_url', '')
                        }
            
            return {"error": "Fun fact not available"}
            
        except Exception as e:
            return {"error": f"Fun fact API error: {str(e)}"}
    
    async def get_nasa_apod(self) -> Dict[str, Any]:
        """Get NASA Astronomy Picture of the Day"""
        try:
            url = f"{self.api_endpoints['nasa']}?api_key=DEMO_KEY"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'title': data.get('title', ''),
                            'explanation': data.get('explanation', ''),
                            'url': data.get('url', ''),
                            'media_type': data.get('media_type', ''),
                            'date': data.get('date', '')
                        }
            
            return {"error": "NASA APOD not available"}
            
        except Exception as e:
            return {"error": f"NASA API error: {str(e)}"}
    
    async def get_spacex_launch(self) -> Dict[str, Any]:
        """Get latest SpaceX launch info"""
        try:
            url = self.api_endpoints['spacex']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'name': data.get('name', ''),
                            'details': data.get('details', ''),
                            'date': data.get('date_utc', ''),
                            'success': data.get('success', False),
                            'rocket': data.get('rocket', ''),
                            'links': data.get('links', {})
                        }
            
            return {"error": "SpaceX launch data not available"}
            
        except Exception as e:
            return {"error": f"SpaceX API error: {str(e)}"}
    
    async def get_number_fact(self, number: int = None) -> Dict[str, Any]:
        """Get interesting fact about a number"""
        try:
            if number is None:
                number = random.randint(1, 1000)
            
            url = f"{self.api_endpoints['numbersapi']}/{number}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        fact = await response.text()
                        return {
                            'success': True,
                            'number': number,
                            'fact': fact,
                            'type': 'trivia'
                        }
            
            return {"error": "Number fact not available"}
            
        except Exception as e:
            return {"error": f"Numbers API error: {str(e)}"}
    
    async def get_bitcoin_price(self) -> Dict[str, Any]:
        """Get current Bitcoin price"""
        try:
            url = self.api_endpoints['coindesk']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        bpi = data.get('bpi', {})
                        
                        return {
                            'success': True,
                            'usd': bpi.get('USD', {}).get('rate', 'N/A'),
                            'eur': bpi.get('EUR', {}).get('rate', 'N/A'),
                            'gbp': bpi.get('GBP', {}).get('rate', 'N/A'),
                            'updated': data.get('time', {}).get('updated', ''),
                            'source': 'CoinDesk'
                        }
            
            return {"error": "Bitcoin price not available"}
            
        except Exception as e:
            return {"error": f"Bitcoin API error: {str(e)}"}
    
    async def get_exchange_rates(self, base: str = "USD") -> Dict[str, Any]:
        """Get currency exchange rates"""
        try:
            url = f"{self.api_endpoints['exchangerate']}/{base}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'base': data.get('base', ''),
                            'date': data.get('date', ''),
                            'rates': data.get('rates', {}),
                            'source': 'ExchangeRate-API'
                        }
            
            return {"error": "Exchange rates not available"}
            
        except Exception as e:
            return {"error": f"Exchange rate API error: {str(e)}"}
    
    async def create_qr_code(self, text: str, size: str = "200x200") -> Dict[str, Any]:
        """Generate QR code"""
        try:
            url = f"{self.api_endpoints['qrcode']}/?size={size}&data={text}"
            
            return {
                'success': True,
                'qr_url': url,
                'text': text,
                'size': size
            }
            
        except Exception as e:
            return {"error": f"QR code generation error: {str(e)}"}
    
    async def get_ip_info(self) -> Dict[str, Any]:
        """Get IP geolocation info"""
        try:
            url = self.api_endpoints['ipapi']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'ip': data.get('ip', ''),
                            'city': data.get('city', ''),
                            'region': data.get('region', ''),
                            'country': data.get('country_name', ''),
                            'timezone': data.get('timezone', ''),
                            'currency': data.get('currency', ''),
                            'org': data.get('org', '')
                        }
            
            return {"error": "IP info not available"}
            
        except Exception as e:
            return {"error": f"IP API error: {str(e)}"}
    
    async def get_movie_info(self, title: str) -> Dict[str, Any]:
        """Get movie information from OMDB"""
        try:
            url = f"{self.api_endpoints['omdb']}?t={title}&apikey=trilogy"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('Response') == 'True':
                            return {
                                'success': True,
                                'title': data.get('Title', ''),
                                'year': data.get('Year', ''),
                                'rated': data.get('Rated', ''),
                                'runtime': data.get('Runtime', ''),
                                'genre': data.get('Genre', ''),
                                'director': data.get('Director', ''),
                                'actors': data.get('Actors', ''),
                                'plot': data.get('Plot', ''),
                                'imdb_rating': data.get('imdbRating', ''),
                                'poster': data.get('Poster', '')
                            }
                        else:
                            return {"error": f"Movie not found: {title}"}
            
            return {"error": "Movie info not available"}
            
        except Exception as e:
            return {"error": f"Movie API error: {str(e)}"}
    
    async def get_wikipedia_summary(self, topic: str) -> Dict[str, Any]:
        """Get Wikipedia article summary"""
        try:
            url = f"{self.api_endpoints['wikipedia']}/page/summary/{topic}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'title': data.get('title', ''),
                            'extract': data.get('extract', ''),
                            'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                            'thumbnail': data.get('thumbnail', {}).get('source', '') if data.get('thumbnail') else '',
                            'lang': data.get('lang', 'en')
                        }
            
            return {"error": f"Wikipedia article not found: {topic}"}
            
        except Exception as e:
            return {"error": f"Wikipedia API error: {str(e)}"}

# Global instance
public_api_service = PublicAPIService()