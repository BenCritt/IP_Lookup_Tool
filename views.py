# This is the code for the IP Address Lookup Tool app.
# Decorator to set cache control headers to prevent caching of the page
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ip_tool(request):
    # Initialize an empty dictionary to store results
    results = {}
    # Initialize error message as None
    error_message = None
    # Create an instance of the IPForm

    form = IPForm()

    # Check if the request method is POST
    if request.method == "POST":
        # Populate form with POST data
        form = IPForm(request.POST)
        # Validate the form input
        if form.is_valid():
            # Retrieve the cleaned IP address
            ip_address = form.cleaned_data["ip_address"]
            # PTR Record Lookup
            try:
                # Perform reverse DNS lookup to find PTR records
                rev_name = dns.reversename.from_address(ip_address)
                # Resolve PTR records for the reverse name
                ptr_records = dns.resolver.resolve(rev_name, "PTR")
                # Store PTR records in the results dictionary
                results["PTR"] = [r.to_text() for r in ptr_records]
            except Exception as e:
                # Handle any exceptions during PTR lookup
                results["PTR"] = [f"Error retrieving PTR records: {str(e)}"]
                error_message = "An error occurred while retrieving PTR records."

            # Geolocation and ISP Information (Example using ip-api.com)
            try:
                # Make a request to the IP geolocation API
                response = requests.get(f"http://ip-api.com/json/{ip_address}")
                # Parse the response as JSON
                geo_data = response.json()
                if geo_data["status"] == "success":
                    # If the API request is successful, store geolocation data in the results dictionary
                    results["Geolocation"] = {
                        "Country": geo_data.get("country"),
                        "Region": geo_data.get("regionName"),
                        "City": geo_data.get("city"),
                        "Latitude": geo_data.get("lat"),
                        "Longitude": geo_data.get("lon"),
                        "ISP": geo_data.get("isp"),
                        "Organization": geo_data.get("org"),
                        "AS": geo_data.get("as"),
                    }
                else:
                    # Handle failure to retrieve geolocation data
                    results["Geolocation"] = ["Failed to retrieve geolocation data."]
            except Exception as e:
                # Handle any exceptions during geolocation lookup
                results["Geolocation"] = [
                    f"Error retrieving geolocation data: {str(e)}"
                ]

            # Blacklist Check (Example using DNS-based blacklist lookup)
            try:
                # Reverse the IP address to check against DNS-based blacklists
                reversed_ip = ".".join(reversed(ip_address.split(".")))
                # List of DNS blacklist servers
                blacklist_servers = ["zen.spamhaus.org", "bl.spamcop.net"]
                # Initialize a list to store blacklist check results
                blacklist_results = []
                for server in blacklist_servers:
                    # Formulate the query for the blacklist server
                    query = f"{reversed_ip}.{server}"
                    try:
                        # Perform DNS resolution for the blacklist query
                        dns.resolver.resolve(query, "A")
                        # If successful, IP is listed on the blacklist server
                        blacklist_results.append(f"Listed on {server}")
                    except dns.resolver.NXDOMAIN:
                        # If NXDOMAIN, IP is not listed on the blacklist server
                        blacklist_results.append(f"Not listed on {server}")
                    except Exception as e:
                        # Handle any exceptions during blacklist checking
                        blacklist_results.append(f"Error checking {server}: {str(e)}")
                # Store blacklist results in the results dictionary
                results["Blacklist"] = blacklist_results
            except Exception as e:
                # Handle any exceptions during the overall blacklist checking process
                results["Blacklist"] = [f"Error checking blacklists: {str(e)}"]

    # Render the template with form, results, and error message
    response = render(
        request,
        "projects/ip_tool.html",
        {"form": form, "results": results, "error_message": error_message},
    )

    # Sets additional anti-caching headers directly on the response object
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    # Return the HTTP response
    return response
