#Module-Specific definitions
%define mod_name mod_asn
%define mod_conf B54_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	mod_asn looks up the AS and network prefix of IP address
Name:		apache-%{mod_name}
Version:	1.3
Release: 	%mkrel 2
Group:		System/Servers
License:	Apache License
URL:		http://mirrorbrain.org/
Source0:	http://mirrorbrain.org/files/releases/%{mod_name}-%{version}.tar.gz
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires(pre):	apache-mod_dbd >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
Requires:	apache-mod_dbd >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	python-sphinx
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_asn is an Apache module doing lookups of the autonomous system (AS)[1], and
the network prefix[2] which contains a given (clients) IP address.

It is written with scalability in mind. To do high-speed lookups, it uses the
PostgreSQL ip4r datatype[3] that is indexable with a Patricia Trie[4] algorithm
to store network prefixes. This is the only algorithm that can search through
the ~250.000 existing prefixes in a breeze.

It comes with script to create such a database (and keep it up to date) with
snapshots from global routing data - from a router's "view of the
world", so to speak.

Apache-internally, the module sets the looked up data as env table variables,
for perusal by other Apache modules. In addition, it can send it as response
headers to the client.

It is published under the Apache License, Version 2.0.

Source code can be obtained here: http://svn.mirrorbrain.org/svn/mod_asn/

Links:
[1] http://en.wikipedia.org/wiki/Autonomous_system_(Internet)
[2] http://en.wikipedia.org/wiki/Subnetwork
[3] http://pgfoundry.org/projects/ip4r/
[4] http://en.wikipedia.org/wiki/Radix_tree

Author: Peter Poeml

%prep

%setup -q -n %{mod_name}-%{version}

cp %{SOURCE1} %{mod_conf}

%build
%{_sbindir}/apxs -c %{mod_name}.c

# make the docs
pushd docs
    make html
popd

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules

install -m0755 .libs/%{mod_so} %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_bindir}
install -m0755 asn_import.py %{buildroot}%{_bindir}/asn_import
install -m0755 asn_get_routeviews.py %{buildroot}%{_bindir}/asn_get_routeviews

# fix docs
rm -rf html; mkdir -p html
cp docs/_build/html/*{html,js} html/
cp -rp docs/_build/html/_static html/

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc html asn.sql docs/_build/html/_sources/*.txt
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_bindir}/*

