#!/usr/bin/perl

use File::Spec;
use File::Basename;
use Sys::Hostname;

#
# Configuration
#

  our $path = dirname(__FILE__);
  require $path . '/config.cgi';

#
# Abort if no IP available (local request)
#

  if (not defined $ENV{REMOTE_ADDR}) {
    exit;
  }

#
# Get Buffer
#

  my $buffer = '';
  if($ENV{CONTENT_LENGTH}) {
    read(STDIN, $buffer, $ENV{CONTENT_LENGTH});
  }
  my $bufferSize = length($buffer);

#
# Log IP for Banning
# Banning operation is managed by a separate script with IPTABLE control
#

  if (!(grep {$_ eq $ENV{REMOTE_ADDR}} @ipIgnore)) {
    open($fh, '>>', getAbsLogPath($ipLogPath));
    print $fh $ENV{REMOTE_ADDR} . "\n";
    close $fh;
  }

#
# If enabled, append the REMOTE_ADDR to the response (for testing)
#

  my $xmlExtra = '';
  if ($srcResponse) {
    $xmlExtra = " src=\"$ENV{REMOTE_ADDR}\"";
  }

#
# Send fake result to discourage interest
#

  if ($buffer =~ /system\.multicall/) {
    $xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"$xmlExtra?>
      <methodResponse>
        <params>
          <param>
            <value>
            <array><data>
              <value><struct>
                <member>
                  <name>faultCode</name>
                  <value><int>403</int></value>
                </member>
                <member>
                  <name>faultString</name>
                  <value><string>Incorrect username or password.</string></value>
                </member>
              </struct></value>
            </data></array>
            </value>
          </param>
        </params>
      </methodResponse>";
  }
  else {
    $xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"$xmlExtra?>
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
      </methodResponse>";
  }
  $xml =~ s/\n\s{6}/\n/g;

  print "Content-Type: text/xml; charset=UTF-8\n\n";
  print $xml;

#
# Send a Notification email
# This option is not reasonable for long term use as the number of messages can be staggering
#

if ($notifyEmail) {

  my $email_body = "Domain: ". $ENV{HTTP_HOST} . "\n";
  $email_body = "Server: ". hostname() . "\n";
  $email_body .= "Remote IP: ". $ENV{REMOTE_ADDR} . "\n";
  $email_body .= "\n";

  $email_body .= "Request ($bufferSize chars) \n\n";
  $email_body .= "\t" . $buffer . "\n";
  $email_body .= "\n";

  $email_body .= "Environment Details\n\n";
  while ( my($env_name,$env_value) = each %ENV ) {
    $email_body .= "\t$env_name = $env_value\n";
  }
  $email_body .= "\n";

  $from = 'xmlrpc-monitor@' . $ENV{SERVER_NAME};
  $subject = 'XMLRPC Log: ' . $ENV{SERVER_NAME};
  $message = $email_body;

  open(MAIL, "|/usr/sbin/sendmail -t");
  print MAIL "To: $notifyEmail\n";
  print MAIL "From: $from\n";
  print MAIL "Subject: $subject\n\n";
  print MAIL $message;
  close(MAIL);

}

exit;

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
