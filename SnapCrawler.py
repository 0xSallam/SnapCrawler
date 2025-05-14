import argparse, os, re, time, json, csv, requests # load libs for CLI, OS I/O, regex, timing, data formats, HTTP
from urllib.parse import urljoin, urlparse # parse and join URLs
from urllib.robotparser import RobotFileParser # parse robots.txt rules
from collections import deque # FIFO queue for BFS crawl
from bs4 import BeautifulSoup  # HTML parsing
from playwright.sync_api import sync_playwright # browser automation for screenshots

DEFAULT_FOLDER = 'screenshots' # default directory to save screenshots

print(r"""
   _____                    _____                    _           
  / ____|                  / ____|                  | |          
 | (___  _ __   __ _ _ __ | |     _ __ __ ___      _| | ___ _ __ 
  \___ \| '_ \ / _` | '_ \| |    | '__/ _` \ \ /\ / / |/ _ \ '__|
  ____) | | | | (_| | |_) | |____| | | (_| |\ V  V /| |  __/ |   
 |_____/|_| |_|\__,_| .__/ \_____|_|  \__,_| \_/\_/ |_|\___|_|   
                    | |                                          
                    |_|                                          
                Developed 💻 by 0xSallam
""")

def get_robots(url, ua): # fetch and parse robots.txt for a given site
    p = urlparse(url)
    rp = RobotFileParser()
    rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
    try: rp.read()
    except: pass
    rp.user_agent = ua
    return rp

def clean_name(url): # generate a safe filename from a URL
    s = urlparse(url).netloc + urlparse(url).path 
    return re.sub(r"[^0-9A-Za-z]", "_", s)[:200] or 'root'

def take_screenshot(page, url, folder=DEFAULT_FOLDER): # take a screenshot of a page
    page.goto(url, timeout=15000)
    time.sleep(1) # wait briefly to allow rendering
    fn = os.path.join(folder, clean_name(url)+'.png')
    page.screenshot(path=fn, full_page=True)
    print(f"[+] {fn}")

def fetch_links(html, base): # extract all links from HTML
    return [urljoin(base,a['href']).split('#')[0]
            for a in BeautifulSoup(html,'html.parser').select('a[href]')]

def crawl(start, depth, delay, ua, folder=DEFAULT_FOLDER): # main crawler function
    os.makedirs(folder,exist_ok=True) 
    rp = get_robots(start,ua)
    host = urlparse(start).netloc
    q, seen, out = deque([(start,0)]), set(), [] 
    with sync_playwright() as p:
        page = p.chromium.launch(headless=True).new_page(user_agent=ua) # launch headless Chromium with custom UA
        while q:
            url,d = q.popleft()
            if url in seen or d>depth or urlparse(url).netloc!=host or not rp.can_fetch(ua,url): continue 
            print(url) 
            seen.add(url); out.append({'url':url})
            take_screenshot(page,url,folder)
            try:
                r=requests.get(url,headers={'User-Agent':ua},timeout=5) # make HTTP GET request
                if 'text/html' in r.headers.get('Content-Type',''): 
                    for link in fetch_links(r.text,url): # extract links
                        if link not in seen: q.append((link,d+1)) 
            except: pass
            time.sleep(delay) # wait before next request
    return out # return crawl results

def save(data, file): # save crawl results to a file
    ext = os.path.splitext(file)[1].lower()
    if ext=='.json': json.dump(data, open(file,'w', encoding='utf-8'), indent=2)
    elif ext=='.csv': 
        w=csv.writer(open(file,'w',newline=''))
        w.writerow(['url']); [w.writerow([i['url']]) for i in data]
    else:
        with open(file,'w',encoding='utf-8') as f: [f.write(f"{i['url']}\n") for i in data]

if __name__=='__main__': 
    p=argparse.ArgumentParser() 
    p.add_argument('start'); p.add_argument('-d','--depth',type=int,default=2)
    p.add_argument('-o','--output',default='results.txt'); p.add_argument('--delay',type=float,default=1) 
    p.add_argument('--user-agent',default='LinkCrawler/1.0') 
    args=p.parse_args()
    res=crawl(args.start,args.depth,args.delay,args.user_agent) 
    save(res,args.output) 
    print(f"Done: {len(res)} links found! -> {args.output}")