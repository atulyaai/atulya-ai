"""
Atulya AI - Web Tools (v0.1.0)
Full production web search and scraping tools
"""

import requests
import json
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

from .tool_registry import tool

@tool(description="Search the web using DuckDuckGo", category="web_search")
def web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Search the web using DuckDuckGo API"""
    try:
        # Use DuckDuckGo Instant Answer API
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        results = []
        
        # Extract abstract
        if data.get("Abstract"):
            results.append({
                "title": data.get("Heading", "Abstract"),
                "url": data.get("AbstractURL", ""),
                "snippet": data.get("Abstract", ""),
                "type": "abstract"
            })
        
        # Extract related topics
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append({
                    "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                    "url": topic.get("FirstURL", ""),
                    "snippet": topic.get("Text", ""),
                    "type": "related_topic"
                })
        
        # Extract definitions
        if data.get("Definition"):
            results.append({
                "title": "Definition",
                "url": data.get("DefinitionURL", ""),
                "snippet": data.get("Definition", ""),
                "type": "definition"
            })
        
        return {
            "success": True,
            "query": query,
            "total_results": len(results),
            "results": results[:max_results],
            "search_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "results": []
        }

@tool(description="Get current weather information", category="web_search")
def get_weather(location: str) -> Dict[str, Any]:
    """Get weather information for a location"""
    try:
        # Use wttr.in service for weather data
        url = f"https://wttr.in/{location}?format=j1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data or "current_condition" not in data:
            return {
                "success": False,
                "error": "No weather data available",
                "location": location
            }
        
        current = data["current_condition"][0]
        weather = data["weather"][0]
        
        weather_info = {
            "location": location,
            "temperature": {
                "celsius": current["temp_C"],
                "fahrenheit": current["temp_F"]
            },
            "condition": current["weatherDesc"][0]["value"],
            "humidity": current["humidity"],
            "wind_speed": current["windspeedKmph"],
            "wind_direction": current["winddir16Point"],
            "pressure": current["pressure"],
            "visibility": current["visibility"],
            "feels_like": {
                "celsius": current["FeelsLikeC"],
                "fahrenheit": current["FeelsLikeF"]
            },
            "forecast": {
                "date": weather["date"],
                "max_temp": weather["hourly"][0]["tempC"],
                "min_temp": weather["hourly"][0]["tempC"],
                "condition": weather["hourly"][0]["weatherDesc"][0]["value"]
            }
        }
        
        return {
            "success": True,
            "weather": weather_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "location": location
        }

@tool(description="Get current time for a location", category="web_search")
def get_time(location: str = "UTC") -> Dict[str, Any]:
    """Get current time for a location"""
    try:
        # Use worldtimeapi.org for time data
        if location.lower() in ["utc", "gmt"]:
            url = "http://worldtimeapi.org/api/timezone/Etc/UTC"
        else:
            # Try to get timezone for the location
            url = f"http://worldtimeapi.org/api/timezone/{location}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        time_info = {
            "location": location,
            "datetime": data["datetime"],
            "timezone": data["timezone"],
            "utc_offset": data["utc_offset"],
            "day_of_week": data["day_of_week"],
            "day_of_year": data["day_of_year"],
            "week_number": data["week_number"]
        }
        
        return {
            "success": True,
            "time": time_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "location": location
        }

@tool(description="Get currency exchange rates", category="web_search")
def get_exchange_rate(from_currency: str, to_currency: str) -> Dict[str, Any]:
    """Get currency exchange rate"""
    try:
        # Use exchangerate-api.com for currency data
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if to_currency.upper() not in data["rates"]:
            return {
                "success": False,
                "error": f"Currency {to_currency} not found",
                "from_currency": from_currency,
                "to_currency": to_currency
            }
        
        rate = data["rates"][to_currency.upper()]
        
        return {
            "success": True,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "exchange_rate": rate,
            "base_date": data["date"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "from_currency": from_currency,
            "to_currency": to_currency
        }

@tool(description="Get news headlines", category="web_search")
def get_news(category: str = "general", country: str = "us") -> Dict[str, Any]:
    """Get news headlines"""
    try:
        # Use NewsAPI (requires API key, but we'll use a fallback)
        # For now, we'll scrape a news site
        url = "https://news.ycombinator.com/"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Simple parsing of Hacker News
        content = response.text
        
        # Extract news items
        news_items = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if 'class="titleline"' in line and i + 1 < len(lines):
                # Extract title and link
                title_match = re.search(r'<a[^>]*>([^<]+)</a>', line)
                link_match = re.search(r'href="([^"]+)"', line)
                
                if title_match and link_match:
                    title = title_match.group(1)
                    link = link_match.group(1)
                    
                    # Get score if available
                    score = "0"
                    if i > 0 and "points" in lines[i-1]:
                        score_match = re.search(r'(\d+)\s+points', lines[i-1])
                        if score_match:
                            score = score_match.group(1)
                    
                    news_items.append({
                        "title": title,
                        "url": link,
                        "score": score,
                        "source": "Hacker News"
                    })
        
        return {
            "success": True,
            "category": category,
            "country": country,
            "total_results": len(news_items),
            "news": news_items[:10],  # Limit to 10 items
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "category": category,
            "country": country
        }

@tool(description="Check if a website is online", category="web_search")
def check_website_status(url: str) -> Dict[str, Any]:
    """Check if a website is online and get status"""
    try:
        # Add protocol if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        start_time = time.time()
        response = requests.get(url, timeout=10, allow_redirects=True)
        response_time = time.time() - start_time
        
        status_info = {
            "url": url,
            "status_code": response.status_code,
            "response_time": round(response_time, 3),
            "content_length": len(response.content),
            "content_type": response.headers.get('content-type', ''),
            "server": response.headers.get('server', ''),
            "is_online": response.status_code < 400
        }
        
        return {
            "success": True,
            "status": status_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "url": url,
            "is_online": False
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection error",
            "url": url,
            "is_online": False
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "is_online": False
        }

@tool(description="Get IP address information", category="web_search")
def get_ip_info(ip_address: Optional[str] = None) -> Dict[str, Any]:
    """Get information about an IP address"""
    try:
        if ip_address is None:
            # Get own IP
            response = requests.get("https://httpbin.org/ip", timeout=10)
            response.raise_for_status()
            data = response.json()
            ip_address = data["origin"]
        
        # Get IP information
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") == "success":
            ip_info = {
                "ip": data["query"],
                "country": data["country"],
                "country_code": data["countryCode"],
                "region": data["regionName"],
                "city": data["city"],
                "zip": data["zip"],
                "lat": data["lat"],
                "lon": data["lon"],
                "timezone": data["timezone"],
                "isp": data["isp"],
                "org": data["org"],
                "as": data["as"]
            }
        else:
            return {
                "success": False,
                "error": "Could not get IP information",
                "ip_address": ip_address
            }
        
        return {
            "success": True,
            "ip_info": ip_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ip_address": ip_address
        }

@tool(description="Get random facts", category="web_search")
def get_random_fact() -> Dict[str, Any]:
    """Get a random fact"""
    try:
        # Use a simple facts API
        url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True,
            "fact": data["text"],
            "source": data.get("source", "Unknown"),
            "language": data.get("language", "en"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 