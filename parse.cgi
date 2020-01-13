#!/usr/bin/perl

#
# Under Development
#
# This script will parse the username/passwords from a request.
# The goal is to log these for reporting and analysis.
# More testing with actual data is needed.
#

use Switch;
use XML::LibXML;

sub getMethodKeys {
  my($methodName) = @_;
  my @methodKeys;
  switch($methodName) {
    case 'wp.getProfile' { @methodKeys = ('id', 'username', 'password'); }
    case 'wp.getUserBlogs' { @methodKeys = ('username', 'password'); }
  }
  return @methodKeys;
}

sub parseMethodCalls {
  my($dom) = @_;
  my $methodName;
  my %methodParams;
  if (my $methodName = $dom->find('methodName')) {
    $methodName = "$methodName";
    my @methodKeys = ();
    my @methodData = ();
    my @methodCalls = ();
    if ($methodName eq "system.multicall") {
      foreach my $data ($dom->findnodes('params/param/value/array/data/value')) {
        foreach my $member ($data->findnodes('struct/member')) {
          if ($member->find('name') eq 'methodName') {
            $methodName = $member->find('value/string');
            $methodName = "$methodName";
            @methodKeys = getMethodKeys($methodName);
          }
          if ($member->find('name') eq 'params') {
            foreach my $param ($member->findnodes('value/array/data/value/array/data/value')) {
              push @methodData, $param->find('string')->to_literal();
            }
            @methodParams{@methodKeys} = @methodData;
            push @methodCalls, {
              'method' => $methodName,
              'params' => \%methodParams
              };
          }
        }
      }
      return @methodCalls;
    }
    @methodKeys = getMethodKeys($methodName);
    foreach my $param ($dom->findnodes('/methodCall/params/param')) {
      push @methodData, $param->find('value')->to_literal();
      if (@methodData >= @methodKeys) {
        last;
      }
    }
    @methodParams{@methodKeys} = @methodData;
    push @methodCalls, {
      'method' => $methodName,
      'params' => \%methodParams
      };
    return @methodCalls;
  }
  return undef;
}

my $filename = 'sample_rpc.xml';
my $dom = XML::LibXML->load_xml(location => $filename);
my @methodCalls = parseMethodCalls( $dom->findnodes('/methodCall') );
print $filename . "\n";
foreach my $methodCall (@methodCalls) {
  print $$methodCall{'method'} .' - '. $$methodCall{'params'}{'username'} .' - '. $$methodCall{'params'}{'password'} . "\n";
}

my $filename = 'sample_multirpc.xml';
my $dom = XML::LibXML->load_xml(location => $filename);
my @methodCalls = parseMethodCalls( $dom->findnodes('/methodCall') );
print $filename . "\n";
foreach my $methodCall (@methodCalls) {
  print $$methodCall{'method'} .' - '. $$methodCall{'params'}{'username'} .' - '. $$methodCall{'params'}{'password'} . "\n";
}
