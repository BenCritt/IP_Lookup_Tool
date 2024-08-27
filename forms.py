# This is the form for the IP Tool app.
class IPForm(forms.Form):
    # Define a form field for the IP address input
    ip_address = forms.CharField(
        # Label that will be displayed with the input field
        label="Enter IP Address:",
        # Maximum length of the input string, suitable for IPv6 addresses
        max_length=45,
        # help_text="Enter a valid IPv4 or IPv6 address.",
    )

    # Method to clean and validate the IP address input
    def clean_ip_address(self):
        # Retrieve the cleaned data for the IP address field
        ip = self.cleaned_data["ip_address"]
        try:
            # Validate the IP address using the ipaddress module
            ipaddress.ip_address(ip)
        except ValueError:
            # If validation fails, raise a ValidationError
            raise forms.ValidationError("Enter a valid IP address.")
        # Return the validated IP address
        return ip
