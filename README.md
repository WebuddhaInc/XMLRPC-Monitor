# Wordpress XMLRPC Monitor, Honeypot, and CSF Block Trigger

This script monitors all requests made to the Wordpress `xmlrpc.php` file, will log the remote IP and optionally sent an email notification containing the request and server details.  This script will respond with a permission denied message to dissaude investigation by the calling party.

This script was written to be installed on Apache servers running cPanel and CSF firewall in environments where multiple Wordpress CMS installations are hosted.  It utilizes the Apache `Alias` rule to capture all incoming requests to `xmlrpc.php` and direct them to a custom cgi script written in Perl.

## cPanel installation

Download the repository to your server logged in as `root` to a suitable location

```
git clone REPO /xmlrpc_monitor
```

Copy `xmlrpc.cgi` to your system cgi folder (`/usr/local/cpanel/cgi-sys/` by default) and rename the file to obfuscate it's presense (eg xmlrpc_xf4cj2.cgi).  

```
cp /xmlrpc_monitor/xmlrpc.cgi /usr/local/cpanel/cgi-sys/xmlrpc_xxxxxx.cgi
```

Set the ownership of your `xmlrpc_xxxxxx.cgi` file to `root`, group to `wheel`, and chmod to `0755`.

```
chown root:wheel /usr/local/cpanel/cgi-sys/xmlrpc_xxxxxx.cgi
```

Edit the `xmlrpc.cgi` file and update the log path to your repository location.

```
vi /usr/local/cpanel/cgi-sys/xmlrpc_xxxxxx.cgi
```

Set your log file permissions so they may be updated by the script.

```
chmod 0777 /xmlrpc_monitor/deny.history
chmod 0777 /xmlrpc_monitor/log.history
```

## Apache Alias configuration

This monitor works by aliasing all requests to `xmlrpc.php` to your custom cgi.  To do this we will use the Apache `Alias` configuration directive.

Insert the following Alias rule in your virtualhost configuration(s).  In the WHM GUI you will find it under **Apache Configuration > Include Editor**.  Add the following to the Post VirtualHost configuration file for **All Versions** which is then applied to all accounts when apache is reloaded.

```
Alias /xmlrpc.php /usr/local/cpanel/cgi-sys/xmlrpc_xxxxxx.cgi
```

## CSF Firewall configuration

This monitor includes a cron operation that will ban IP addresses via CSF firewall by periodically scanning the request log for repeated requests.  To enable this feature you will create a root cron event.

As the `root` user open the crontab editor.

```
crontab -e
```

Then add the following to the end of the file, save, and close (CTRL+O, ENTER, CTRL+X).

```
# XMLRPC Monitor
* * * * * /xmlrpc_monitor/cron.cgi > /dev/null 2>&1
```

## Configuration Options

Edit `config.cgi` and customize the runtime options.

```
vi /xmlrpc_monitor/config.cgi
```

### Ignore Remote IPs

Apply any IP addresses to this array that you may want to ignore.  This would be requests from your office machines or penetration testing servers.

```
our @ipIgnore = ('192.168.1.1', '192.168.1.2');
```

### Paths to log files

If you wish to move the location of your log files you will need to specify that here.  Use absolute paths.

```
our $ipLogPath = 'log.history';
our $ipDenyLogPath = 'deny.history';
```

### Request Limit before Firewall Block

If CSF firewall is installed and you wish to block Remote IP addresses after they have requested `xmlrpc.php` then you will set this to number of requests to capture (allow) before blocking.

```
our $requestLimit = 3;
```

### Email Notifications

If you wish to receive a notification with the request body every time `xmlrpc.php` is requested then you will provide a single email address.

```
our $notifyEmail = 'notifyme@website.com';
```

### Remote IP in fake response

All requests receive a fake 403 response message.  You may choose to include a Remote IP parameter in the response to help debug during testing.  Set this to 1 to enable.

```
our $srcResponse = 0;
```

The `<?xml>` response tag will be appended with a `src` parameter:

```
<?xml version="1.0" encoding="UTF-8" src="192.168.1.1"?>
```

## Testing

From your machine you can test using curl.

```
curl -X POST http://www.yourwebsite.com/xmlrpc.php
```

You should receive a valid XML response indicating faultCode 403.

```
<?xml version="1.0" encoding="UTF-8">
<methodResponse>
  <fault>
    <value>
      <struct>
        <member>
          <name>faultCode</name>
          <value><int>403</int></value>
        </member>
        <member>
          <name>faultString</name>
          <value><string>Incorrect username or password.</string></value>
        </member>
      </struct>
    </value>
  </fault>
</methodResponse>
```