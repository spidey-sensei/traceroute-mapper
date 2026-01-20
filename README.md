# Traceroute Map Visualizer 

# Requirements
- traceroute installed
- pip install requests folium

# Overview

This project implements a Traceroute Map Visualizer that mimics the behavior of the terminal traceroute command and visualizes network paths on an interactive world map.

The pipeline followed is:

Destinations → Traceroute → Hop-wise IP extraction → IP Geolocation → Map Visualization

The visualization concept is inspired by: https://stefansundin.github.io/traceroute-mapper/

# Features

- Reads multiple destinations from a file
- Executes traceroute using ICMP (reliable across ISPs)
- Parses output hop-by-hop (terminal-accurate)
- Handles multiple IP responses per hop (load balancing)
- Filters private IP addresses (RFC 1918)
- Geolocates public IPs using ipinfo.io api token
- Interactive map visualization using Folium
- Different color for each destination route

# How It Works

1. Traceroute Execution

- Uses ICMP-based traceroute: 
 traceroute -I -n destination

- -I ensures reliability;
  -n disables DNS lookups

2. Hop-wise Parsing

- Each traceroute line is treated as one hop
- Multiple IP responses per hop are supported
- "* * *" hops are safely ignored

3. IP Filtering

- Private IPs (10.x.x.x, 192.168.x.x, 172.16–31.x.x) are excluded
- Only public IPs are geolocated

4. Visualization

- Each destination is assigned a unique color
- Hops are shown as circle markers
- Routes are connected using polylines
- Popups show hop number, IP, and location

* Note: The traceroute output was parsed hop-by-hop to preserve routing structure. For hops returning multiple probe responses due to load balancing, the first publicly routable IP address was selected. Private IP addresses and non-responsive hops were filtered as they cannot be geolocated using public IP databases.


