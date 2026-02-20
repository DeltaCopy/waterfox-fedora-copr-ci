%define app waterfox
%define appdir %{_prefix}/%_lib/waterfox
%define dev BrowserWorks
%define release_tag 6.6.7
%define versioned_python_package python3.11
%define python_binary_name python3.11
%define github_repo https://github.com/%{dev}/%{app}
%define debug_package %{nil}
%global create_debuginfo  1

Name: %{app}
Version: %{release_tag}
Release: 1%{?dist}
Summary: A privacy-focused browser built for power users who value customization and control over their online experience
License: MPL-2.0

URL: %{github_repo}

Source0: https://github.com/%{dev}/%{app}/archive/refs/tags/%{version}.tar.gz
Source1: release_tag.txt
Source2: vendor.js
Source3: %{app}.desktop
Source4: distribution.ini

BuildRequires: cbindgen
BuildRequires: diffutils
BuildRequires: imake
BuildRequires: lld
BuildRequires: mold
BuildRequires: clang-devel
BuildRequires: mercurial
BuildRequires: mesa-dri-drivers
BuildRequires: nasm
BuildRequires: nodejs
BuildRequires: alsa-lib-devel

%if 0%{?versioned_python_package:1}
BuildRequires:  %{versioned_python_package}
%else
BuildRequires:  pkgconfig(python3) >= 3.7
BuildRequires:  python3 >= 3.7
%endif
BuildRequires: rust
BuildRequires: unzip
BuildRequires:  llvm
BuildRequires: llvm-devel
BuildRequires: yasm
BuildRequires: zip
BuildRequires: cargo >= 0.78
BuildRequires: libdrm-devel
BuildRequires: libnotify-devel
BuildRequires: libproxy-devel

BuildRequires: pkgconfig(jack)
BuildRequires: pkgconfig(xt)
BuildRequires: pkgconfig(gdk-x11-2.0)
BuildRequires: pkgconfig(glib-2.0) >= 2.22
BuildRequires: pkgconfig(gobject-2.0)
BuildRequires: pkgconfig(gtk+-2.0) >= 2.18.0
BuildRequires: pkgconfig(gtk+-3.0) >= 3.4.0
BuildRequires: pkgconfig(gtk+-unix-print-2.0)
BuildRequires: pkgconfig(gtk+-unix-print-3.0)
BuildRequires: libcurl-devel
BuildRequires: pkgconfig(libffi)
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(nspr) >= 4.35
BuildRequires: pkgconfig(nss) >= 3.101
BuildRequires: pkgconfig(gl)

ExclusiveArch:  x86_64

Obsoletes:      %{app} <= %{version}

%description
A privacy-focused browser built for power users who value customization and control over their online experience

%prep
%autosetup -p1

cd %{_builddir}/%{app}-%{version}

mkdir -p "%{_sourcedir}/mozbuild"

if [ -f .mozconfig ]; then
    rm .mozconfig
fi 
cat >mozconfig <<END

mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/obj

ac_add_options --enable-application=browser
ac_add_options --prefix="%{_prefix}"
ac_add_options --libdir="%{_libdir}"
ac_add_options --enable-alsa
ac_add_options --enable-pulseaudio
ac_add_options --enable-jack
ac_add_options --enable-release
ac_add_options --enable-hardening
ac_add_options --enable-optimize
ac_add_options --enable-rust-simd
ac_add_options --enable-jxl

ac_add_options --disable-elf-hack
ac_add_options --disable-bootstrap
ac_add_options --disable-profiling
ac_add_options --disable-tests
ac_add_options --enable-linker=mold

# System libraries
ac_add_options --with-system-nspr
ac_add_options --with-system-nss

# Branding
ac_add_options --with-app-name=waterfox
ac_add_options --with-app-basename=Waterfox
ac_add_options --with-branding=waterfox/browser/branding
ac_add_options --with-distribution-id=fedora
ac_add_options --with-unsigned-addon-scopes=app,system
ac_add_options --allow-addon-sideload

# Features
ac_add_options --enable-alsa
ac_add_options --enable-jack
ac_add_options --enable-crashreporter
ac_add_options --disable-updater
ac_add_options --disable-tests

ac_add_options --without-sysroot
ac_add_options --without-wasm-sandboxed-libraries
ac_add_options --with-libclang-path=`llvm-config --libdir`
ac_add_options --enable-default-toolkit=cairo-gtk3-wayland
ac_add_options --with-system-zlib

ac_add_options --enable-profile-generate=cross

END

# Use correct python version for mach
sed -i -e 's|#!/usr/bin/env python3|#!/usr/bin/env %{python_binary_name}|' mach

# Remove reference to empty locales dir 
sed -i -e '/"locales",/d' waterfox/browser/moz.build
%build

export MOZ_INCLUDE_SOURCE_INFO=1
export MOZ_SOURCE_CHANGESET=$(awk -F ': ' '/^commit:/ {print $2; exit}' %{SOURCE1})
export MOZ_APP_REMOTINGNAME=waterfox

export WFX_RELEASE=1

export MOZ_SOURCE_REPO=https://github.com/BrowserWorks/Waterfox
export WF_VERSION=%{version}
export GALLIUM_DRIVER=llvmpipe
export CBINDGEN=/usr/bin/cbindgen

export MOZ_NOSPAM=1
export MOZBUILD_STATE_PATH="%{_sourcedir}/mozbuild"
export MACH_BUILD_PYTHON_NATIVE_PACKAGE_SOURCE=system
export MOZ_TELEMETRY_REPORTING=0

MOZ_OPT_FLAGS=$(echo "%{optflags}" | sed -e 's/-fexceptions//')

export CFLAGS="$MOZ_OPT_FLAGS"
export CXXFLAGS="$MOZ_OPT_FLAGS"
export LDFLAGS="$MOZ_LINK_FLAGS"
export GEN_PGO=1
export LDFLAGS="$MOZ_LINK_FLAGS"

export CC=clang
export CXX=clang++

# LTO needs more open files
ulimit -n 4096
echo "Building instrumented browser..."

./mach build --priority normal

echo "Profiling instrumented browser..."
./mach package
LLVM_PROFDATA=llvm-profdata \
  JARLOG_FILE="$PWD/jarlog" \
  dbus-run-session \
  xvfb-run -s "-screen 0 1920x1080x24 -nolisten local" \
  ./mach python build/pgo/profileserver.py

stat -c "Profile data found (%s bytes)" merged.profdata
test -s merged.profdata

stat -c "Jar log found (%s bytes)" jarlog
test -s jarlog

echo "Removing instrumented browser..."
./mach clobber objdir

echo "Building optimized browser..."
cat >mozconfig - <<END
ac_add_options --enable-lto=cross
ac_add_options --enable-profile-use=cross
ac_add_options --with-pgo-profile-path="$PWD"/merged.profdata
ac_add_options --with-pgo-jarlog="$PWD"/jarlog
END

%install
export MOZ_SOURCE_REPO=%{github_repo}
export MOZ_SOURCE_CHANGESET=$(awk -F ': ' '/^commit:/ {print $2; exit}' %{SOURCE1})
export WF_VERSION=%{version}

export MACH_BUILD_PYTHON_NATIVE_PACKAGE_SOURCE=system
export MOZ_NOSPAM=1
export MOZBUILD_STATE_PATH="%{_sourcedir}/mozbuild"

DESTDIR=%{buildroot} ./mach install

for i in 16 32 48 64 128; do
  %{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps
  ln -Tsrf %{buildroot}%{appdir}/browser/chrome/icons/default/default$i.png \
    %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/%{app}.png
done

%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/192x192/apps
%{__install} -Dm644 waterfox/browser/branding/content/about-logo.png \
  "%{buildroot}%{_datadir}/icons/hicolor/192x192/apps/%{app}.png"

%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/384x384/apps
%{__install} -Dm644 waterfox/browser/branding/content/about-logo@2x.png \
  "%{buildroot}%{_datadir}/icons/hicolor/384x384/apps/%{app}.png"

# create a .desktop file
cat > %{app}.desktop <<END

END

%{__mkdir_p} %{buildroot}{%{_libdir},%{_bindir},%{_datadir}/applications}
desktop-file-install --dir %{buildroot}%{_datadir}/applications %{SOURCE3}

# Use system-provided dictionaries
rm -rf "%{buildroot}%{appdir}/dictionaries"

%{__install} -Dm 644 %{SOURCE2} %{buildroot}%{appdir}/browser/defaults/preferences/vendor.js

cat > %{buildroot}%{appdir}/browser/defaults/preferences/spellcheck.js <<END
pref("spellchecker.dictionary_path", "/usr/share/myspell");
END

# Add distribution.ini
%{__mkdir_p} %{buildroot}%{appdir}/distribution
%{__cp} %{SOURCE4} %{buildroot}%{appdir}/distribution/distribution.ini

# Install a wrapper to avoid confusion about binary path
%{__install} -Dm755 /dev/stdin "%{buildroot}%{_bindir}/%{app}" <<END
#!/bin/sh
exec %{appdir}/%{app} "\$@"
END

%post
# update mime and desktop database
%mime_database_post
%desktop_database_post
%icon_theme_cache_post
exit 0

%postun
%icon_theme_cache_postun
%desktop_database_postun
%mime_database_postun
exit 0

%files
%defattr(-,root,root)
%{appdir}
%doc %{_mandir}/man1/*
%{_datadir}/applications/%{appname}.desktop
%{_bindir}/%{appname}
%{_bindir}/waterfox
%{_bindir}/waterfox-g
%dir /etc/%{appname}
%config /etc/%{appname}/syspref.js

for i in 16 32 48 64 128 192 384; do
    %{_datadir}/icons/hicolor/${i}x${i}/apps/%{appname}.png
done

%{_datadir}/appdata/
%dir %{_datadir}/icons/hicolor/384x384
%dir %{_datadir}/icons/hicolor/384x384/apps

%changelog
%autochangelog

%clean
rm -rf %{buildroot}
