%define app waterfox
%define dev BrowserWorks
%define appdir %{_prefix}/%_lib/%{app}
%define release_tag ${TAG} # this line gets updated automatically by Github Actions
%define debug_package %{nil}
%define github_rpm_src https://raw.githubusercontent.com/DeltaCopy/waterfox-fedora-copr-ci/refs/heads/main/sources

Name: %{app}
Version: %{release_tag}
Release: 1%{?dist}
Summary: A privacy-focused browser built for power users who value customization and control over their online experience
Group: System/GUI/Internet
License: MPL-2.0

URL: https://github.com/%{dev}/%{app}

Source0: https://cdn1.%{app}.net/%{app}/releases/%{version}/Linux_x86_64/%{app}-%{version}.tar.bz2
Source1: %{github_rpm_src}/vendor.js
Source2: %{github_rpm_src}/%{app}.desktop
Source3: %{github_rpm_src}//distribution.ini
Source4: %{github_rpm_src}/%{app}-browser.appdata.xml
Source5: %{github_rpm_src}/policies.json

ExclusiveArch: x86_64

BuildRequires: curl
BuildRequires: coreutils

Obsoletes: %{app} <= %{version}

%description
A privacy-focused browser built for power users who value customization and control over their online experience

%prep
%autosetup -n %{_builddir}/%{app} -p1

for s in vendor.js %{app}.desktop distribution.ini  \
  %{app}-browser.appdata.xml policies.json SHA256SUMS; do
  curl -Ls %{github_rpm_src}/$s -o %{_sourcedir}/$s 
done

cd %{_sourcedir} && sha256sum -c SHA256SUMS && test $? -ne 0 && echo "sha256sum = failed" && exit 1 || echo "sha256sum = ok"

%install

mkdir -p %{buildroot}%{_bindir}

%{__install} -Dm 644 %{SOURCE1} %{buildroot}%{appdir}/browser/defaults/preferences/vendor.js

for i in 16 32 48 64 128; do
  %{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps
  ln -Tsrf %{buildroot}%{appdir}/browser/chrome/icons/default/default$i.png \
    %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/%{app}.png
done

%{__install} -Dm 644 %{SOURCE2} %{buildroot}%{_datadir}/applications/%{app}.desktop

%{__install} -Dm 644 %{SOURCE3} %{buildroot}%{appdir}/distribution/distribution.ini

%{__cp} %{app} %{buildroot}%{_bindir}

%{__install} -Dm 644 %{SOURCE4} %{buildroot}%{_datadir}/appdata/%{app}-browser.appdata.xml

%{__install} -Dm 644 %{SOURCE5} %{buildroot}%{appdir}/distribution/policies.json

%{__cp} -r %{_builddir}/%{app} %{buildroot}/%{_libdir}

# Backwards compatibility symlinks
ln -Tsrf %{_libdir}/%{app}/%{app} %{buildroot}/%{_bindir}/%{app}-g

ln -Tsrf %{_libdir}/%{app}/%{app} %{buildroot}/%{_bindir}/%{app}

%files

%{_bindir}/%{app}
%{_bindir}/%{app}-g
%{_datadir}/applications/%{app}.desktop
%{_datadir}/appdata
%{_datadir}/icons/hicolor/16x16/apps/%{app}.png
%{_datadir}/icons/hicolor/32x32/apps/%{app}.png
%{_datadir}/icons/hicolor/48x48/apps/%{app}.png
%{_datadir}/icons/hicolor/64x64/apps/%{app}.png
%{_datadir}/icons/hicolor/128x128/apps/%{app}.png
%{appdir}

%changelog
%autochangelog

%clean
rm -rf %{buildroot}