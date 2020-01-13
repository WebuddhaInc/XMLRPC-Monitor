#!/usr/bin/perl

# IPs that you don't want to block
our @ipIgnore = ();

# Full path to IP Log file
our $ipLogPath = 'log.history';

# Full path to IP Deny Log file
our $ipDenyLogPath = 'deny.history';

# How many requests are logged before the IP is blocked
our $requestLimit = 3;

# Email address if you want email notifications
our $notifyEmail = '';

# Include detected Remote IP in fake response
our $srcResponse = 0;

# done
return true;
