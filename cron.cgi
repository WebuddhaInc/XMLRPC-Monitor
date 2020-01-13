#!/usr/bin/perl

use File::Spec;
use File::Basename;

#
# Configuration
#

  our $path = dirname(__FILE__);
  require $path . '/config.cgi';


#
# Start
#

  print getDateTime() . "\n";

#
# Load the IP Log
#

  my @ipList;
  my %ipCount;
  open($fh, '<', getAbsLogPath( $ipLogPath ));
  while (<$fh>) {
    chomp;
    push @ipList, $_;
    if (exists $ipCount{ $_ }) {
      $ipCount{ $_ }++;
    }
    else {
      $ipCount{ $_ } = 1;
    }
  }
  close $fh;
  print 'Checking ' . (keys %ipCount) . " addresses\n";

#
# Check for IP's that have exceeded the limit
# Block if they are not in the $ipIgnore list
#

  $blocked = 0;
  foreach my $ip (keys %ipCount) {
    if ($ipCount{ $ip } > $requestLimit && !(grep {$_ eq $ENV{REMOTE_ADDR}} @ipIgnore)) {
      print "Block " . $ip . ' for ' . $ipCount{ $ip } . " requests\n";
      print `csf -td $ip 86400 "XMLRPC Request Source"`;
      open($fh, '>>', getAbsLogPath( $ipDenyLogPath ));
      print $fh getDateTime() . ' ' . $ip . ' ' . $ipCount{ $ip } . "\n";
      close $fh;
      $ipCount{ $ip } = 0;
      $blocked++;
    }
  }

#
# Rebuild the IP Log, removing blocked IPs
#

  if ($blocked) {
    open($fh, '>', getAbsLogPath( $ipLogPath ));
    foreach my $ip (@ipList) {
      if ($ipCount{ $ip } > 0) {
        print $fh $ip."\n";
      }
    }
    close $fh;
  }
  print 'Blocked ' . $blocked . " addresses\n";

#
# Method to get absolute log path
#

  sub getAbsLogPath {
    my ($file) = @_;
    if ($file =~ /^\//) {
      return $file;
    }
    return $path . '/' . $file;
  }

#
# Method to get a formatted datetime string
#

  sub getDateTime {
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
    return sprintf("%04d-%02d-%02d %02d:%02d:%02d", 1900 + $year, $mon + 1, $mday, $hour, $min, $sec);
  }