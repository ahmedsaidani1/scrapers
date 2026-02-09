# Glo24.de VPN/Proxy Setup Guide

## Problem
Glo24.de is only accessible from Germany. When accessing from outside Germany, you'll get blocked or see errors.

## Solution Options

### Option 1: HTTP/HTTPS Proxy (Recommended - Easiest)

Use a German proxy service to route your traffic through Germany.

#### Popular German Proxy Services:
1. **Bright Data** (formerly Luminati) - https://brightdata.com
   - Residential proxies in Germany
   - Pay-as-you-go pricing
   - Format: `http://username:password@proxy-server:port`

2. **Smartproxy** - https://smartproxy.com
   - German residential/datacenter proxies
   - Starting at $12.5/GB
   - Format: `http://username:password@gate.smartproxy.com:7000`

3. **Oxylabs** - https://oxylabs.io
   - German datacenter proxies
   - Enterprise-grade
   - Format: `http://username:password@de.oxylabs.io:8001`

4. **ProxyMesh** - https://proxymesh.com
   - German proxy servers
   - $10-50/month
   - Format: `http://username:password@de.proxymesh.com:31280`

#### Setup Steps:

1. **Sign up for a proxy service** (choose one from above)

2. **Get your proxy credentials**:
   - Username
   - Password
   - Proxy server address
   - Port number

3. **Update config.py**:
```python
"glo24": {
    "base_url": "https://glo24.de",
    "sitemap_url": "https://glo24.de/sitemap.xml",
    "requires_login": False,
    "platform": "Unknown (Cloudflare protected - uses cloudscraper)",
    "custom_headers": {},
    "delay_override": None,
    "proxy": "http://username:password@de-proxy.example.com:8080",  # Your proxy here
},
```

4. **Test the scraper**:
```bash
python glo24_scraper.py
```

---

### Option 2: SOCKS5 Proxy

If you have a SOCKS5 proxy (more advanced):

1. **Install additional dependency**:
```bash
pip install requests[socks]
```

2. **Update config.py**:
```python
"proxy": "socks5://username:password@de-proxy.example.com:1080",
```

---

### Option 3: VPN on Server (If running on a server)

If you're running the scraper on a Linux server, you can set up a VPN:

#### Using OpenVPN:

1. **Install OpenVPN**:
```bash
sudo apt-get update
sudo apt-get install openvpn
```

2. **Get German VPN config** from providers like:
   - NordVPN (Germany servers)
   - ExpressVPN (Germany servers)
   - ProtonVPN (Germany servers)

3. **Connect to VPN**:
```bash
sudo openvpn --config germany-server.ovpn
```

4. **Run scraper** (no proxy config needed - all traffic goes through VPN):
```bash
python glo24_scraper.py
```

#### Using WireGuard (Faster):

1. **Install WireGuard**:
```bash
sudo apt-get install wireguard
```

2. **Configure with German VPN provider**

3. **Start VPN**:
```bash
sudo wg-quick up wg0
```

---

### Option 4: Free Proxy Lists (Not Recommended - Unreliable)

You can try free German proxies, but they're often slow and unreliable:

- https://www.proxy-list.download/HTTPS
- https://free-proxy-list.net/
- Filter by Germany (DE)

**Warning**: Free proxies are:
- Often blocked by Cloudflare
- Slow and unreliable
- May log your traffic
- Frequently go offline

---

## Testing Your Setup

### Test 1: Check if proxy works
```python
# test_glo24_proxy.py
import cloudscraper

scraper = cloudscraper.create_scraper()
scraper.proxies = {
    'http': 'http://username:password@proxy:port',
    'https': 'http://username:password@proxy:port'
}

try:
    response = scraper.get('https://glo24.de')
    print(f"Status: {response.status_code}")
    print(f"Success! Site is accessible")
except Exception as e:
    print(f"Error: {e}")
```

### Test 2: Check your IP location
```python
import cloudscraper

scraper = cloudscraper.create_scraper()
scraper.proxies = {
    'http': 'your-proxy-here',
    'https': 'your-proxy-here'
}

response = scraper.get('https://ipapi.co/json/')
data = response.json()
print(f"Your IP: {data['ip']}")
print(f"Country: {data['country_name']}")
print(f"City: {data['city']}")
```

---

## Current Implementation

The glo24_scraper.py has been updated to support proxies:

```python
def __init__(self):
    super().__init__(SCRAPER_NAME)
    
    self.config = SCRAPER_CONFIGS.get(SCRAPER_NAME, {})
    self.base_url = self.config.get("base_url", "https://glo24.de")
    
    # Get proxy from config
    self.proxy = self.config.get("proxy", None)
    
    # Initialize cloudscraper
    self.scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    # Configure proxy if provided
    if self.proxy:
        self.scraper.proxies = {
            'http': self.proxy,
            'https': self.proxy
        }
        self.logger.info(f"Using proxy: {self.proxy}")
```

---

## Recommended Solution

**For production use**: Use a paid proxy service like Smartproxy or Bright Data
- Reliable
- Fast
- Good for Cloudflare bypass
- German residential IPs
- Cost: ~$50-100/month for moderate usage

**For testing**: Try ProxyMesh or a free trial from Smartproxy
- Quick setup
- Test before committing

**For server deployment**: Set up VPN on the server
- One-time setup
- All traffic routed through Germany
- No per-request proxy overhead

---

## Troubleshooting

### Error: "Connection refused"
- Proxy server is down or incorrect
- Check proxy credentials and address

### Error: "403 Forbidden" or "Access Denied"
- Proxy IP is blocked by Cloudflare
- Try residential proxies instead of datacenter
- Rotate proxy IPs

### Error: "Timeout"
- Proxy is too slow
- Increase timeout in config
- Try different proxy provider

### Site still blocks you
- Use residential proxies (not datacenter)
- Add German headers:
```python
"custom_headers": {
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8"
}
```

---

## Cost Comparison

| Service | Type | Price | Best For |
|---------|------|-------|----------|
| Smartproxy | Residential | $12.5/GB | Testing |
| Bright Data | Residential | $15/GB | Production |
| Oxylabs | Datacenter | $300/month | Enterprise |
| ProxyMesh | Datacenter | $10-50/month | Budget |
| NordVPN | VPN | $12/month | Server VPN |
| Free Proxies | Mixed | Free | Not recommended |

---

## Next Steps

1. Choose a proxy service
2. Sign up and get credentials
3. Update `config.py` with proxy URL
4. Test with: `python glo24_scraper.py`
5. Monitor logs for any issues

Need help? Check the logs at `logs/glo24.log`
