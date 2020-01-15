Name:           sfxbridge
Version:        %{major_version}
Release:        %{minor_version}%{?dist}
Url:            http://github.com/aiven/sfxbridge
Summary:        Bridge metrics from telegraf to SignalFX
License:        ASL 2.0
Source0:        sfxbridge-rpm-src.tar.gz
Requires:       systemd-python3, python3-requests, python3-aiohttp
BuildRequires:  systemd-python3, python3-requests, python3-aiohttp
BuildRequires:  python3-devel, python3-pytest, python3-pylint
BuildArch:      noarch

%description
sfxbridge is a daemon receives metrics from telegraf http output
and converts and sends them to SignalFX via their REST API.


%prep
%setup -q -n sfxbridge


%build


%install
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot}
sed -e "s@#!/bin/python@#!%{_bindir}/python@" -i %{buildroot}%{_bindir}/*
%{__install} -Dm0644 sfxbridge.unit %{buildroot}%{_unitdir}/sfxbridge.service
%{__install} -Dm0644 sfxbridge.json %{buildroot}%{_sysconfdir}/sfxbridge/config.json
sed -e "s,/usr/bin/sfxbridge,%{_bindir}/sfxbridge,g" \
    -e "s,/etc/sfxbridge,%{_sysconfdir}/sfxbridge,g" \
    -e "s,/var/lib/sfxbridge,%{_localstatedir}/lib/sfxbridge,g" \
    -i %{buildroot}%{_unitdir}/sfxbridge.service
%{__mkdir_p} %{buildroot}%{_localstatedir}/lib/sfxbridge


%check


%files
%defattr(-,root,root,-)
%doc LICENSE
%config %{_sysconfdir}/sfxbridge/config.json
%{_bindir}/sfxbridge*
%{_unitdir}/sfxbridge.service
%{_localstatedir}/lib/sfxbridge
%{python3_sitelib}/*


%changelog
* Mon Oct 18 2019 Marko Teiste <mte@aiven.io> - 1.0.0
- Initial RPM package spec
