import tls_client

TOTAL = 0
def mass_req():
    global TOTAL
    PROXY = "http://uovnckrq225gzb:U1oOdE569s4j5EE@res.razorproxies.com:8080"
    session = tls_client.Session(client_identifier="chrome_120")
    session.proxies = {"http": PROXY, "https": PROXY}
    while True:
        req = session.get("https://www.sih.gov.in/")
        print(f"Total requests: {TOTAL}")
        #print(req.text)
        TOTAL += 1

if __name__ == "__main__":
    mass_req()