import subprocess
import re
import requests
import folium
import time
import ipaddress

DEST_FILE = "destination_list.txt"
OUTPUT_MAP = "traceroute_map.html"
IPINFO_TOKEN = "a851fd146fa295"  


# 1: Read destinations

def read_destinations(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

# 2: Run traceroute (ICMP)

def run_traceroute(destination):
    print(f"[*] Tracerouting {destination}")
    try:
        output = subprocess.check_output(
            ["traceroute", "-I", "-n", destination],
            stderr=subprocess.STDOUT,
            text=True
        )
        return output
    except subprocess.CalledProcessError as e:
        return e.output


# 3: Parse traceroute output hop-by-hop

def parse_traceroute(output):

    hops = []
    lines = output.splitlines()[1:] 

    for line in lines:
        if "* * *" in line:
            hops.append([])
            continue

        ips = re.findall(r"(\d+\.\d+\.\d+\.\d+)", line)
        hops.append(ips)

    return hops

# 4: Select first PUBLIC IP per hop

def select_public_hops(hops):
    selected = []
    for hop in hops:
        for ip in hop:
            try:
                if not ipaddress.ip_address(ip).is_private:
                    selected.append(ip)
                    break
            except ValueError:
                continue
    return selected

# 5: Geolocate IPs

def geolocate_ip(ip):
    url = f"https://ipinfo.io/{ip}/json"
    params = {}
    if IPINFO_TOKEN:
        params["token"] = IPINFO_TOKEN

    try:
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        if "loc" in data:
            lat, lon = map(float, data["loc"].split(","))
            return {
                "ip": ip,
                "lat": lat,
                "lon": lon,
                "city": data.get("city"),
                "country": data.get("country")
            }
    except Exception:
        pass

    return None

# 6: Visualize routes

def plot_routes(routes):
    colors = [
        "red", "blue", "green", "purple", "orange",
        "darkred", "cadetblue", "darkgreen", "darkpurple"
    ]

    first = routes[0][0]
    fmap = folium.Map(location=[first['lat'], first['lon']], zoom_start=2)

    for route_index, route in enumerate(routes):
        route_color = colors[route_index % len(colors)]
        coords = []

        for idx, hop in enumerate(route, start=1):
            coords.append((hop['lat'], hop['lon']))
            folium.CircleMarker(
                location=(hop['lat'], hop['lon']),
                radius=5,
                color=route_color,
                fill=True,
                fill_color=route_color,
                popup=(
                    f"Destination {route_index + 1}<br>"
                    f"Hop {idx}<br>"
                    f"IP: {hop['ip']}<br>"
                    f"{hop.get('city', '')} {hop.get('country', '')}"
                )
            ).add_to(fmap)

        folium.PolyLine(
            coords,
            color=route_color,
            weight=3,
            opacity=0.8
        ).add_to(fmap)

    fmap.save(OUTPUT_MAP)
    print(f"[+] Map saved to {OUTPUT_MAP}")

def main():
    destinations = read_destinations(DEST_FILE)
    all_routes = []

    for dest in destinations:
        output = run_traceroute(dest)
        hops = parse_traceroute(output)
        public_ips = select_public_hops(hops)

        print("[DEBUG] Selected hop IPs:", public_ips)

        route = []
        for ip in public_ips:
            geo = geolocate_ip(ip)
            if geo:
                route.append(geo)
            time.sleep(1)

        if route:
            all_routes.append(route)

    if all_routes:
        plot_routes(all_routes)
    else:
        print("[!] No routes to plot")


if __name__ == "__main__":
    main()
