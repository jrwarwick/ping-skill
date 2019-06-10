# <img src='https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/satellite-dish.svg' card_color='#35752E' width='50' height='50' style='vertical-align:bottom'/> Network Ping
Send network pings (a.k.a. ICMP echo requests) to internet nodes

## About
This is a 3rd party skill that uses keywords to get either a server's ping time or status via ICMP echo requests. This can be used to check that a server is responding correctly. Alternatively, one can use this to send simple HTTP GET requests to a server to start or stop services. By using the Network Ping Skill, custom commands can be created for webhook-enabled online services.

For instance, saying, *Mycroft: Send a Ping to network node Google* garners a reply of `Pinged in 9.03 milliseconds.`

If a keyword is set to get the server response, then Mycroft will reply, `Server says: OK 200`, or ` Bad Gateway 502`, et cetera.

---

Configuration of network node aliases is stored in a text file, `hosts.txt`, with one "keyword,setting,URL" per line:

    google,0,https://google.com
    
This line will tell the Ping Skill that **google** is the keyword, **0** is for a *Ping* response and then the URL to ping. Alternatively, this

    linux,1,https://linux.com
    
will respond to the **linux** keyword and return the server *Status* of `linux.com`, because of the **1** after the keyword.

If you are running server software that can respond to GET requests, such as [Huginn](https://github.com/cantino/huginn), or there is a webservice without a prepackaged Mycroft skill that accepts webhooks, then a line like

    hug, 1, https://www.HuginnDomain.com/users/1/web_requests/2/supersecretstring?service=start

and the corresponding settings on the remote end will make the Ping Skill into a basic remote control. Saying *Mycroft: Send a Ping Hug* will load that URL, which will execute code on the server. Mycroft will reply, in the case of Huginn with a default Webhook Agent, with the custom server response, `Event Created 201`, to confirm the instruction was received and followed.

## Examples
* "Send a Ping to network node Google"
* "Send ICMP echo to ten dot zero dot zero dot thirty"
* "Send ping to dns name mycroft dot AI"

## Credits
@nogre @jrwarwick

## Category
**IoT**

## Tags
#network
#ping
#utility

