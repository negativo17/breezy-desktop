# modules/sombrero
%global commit1 6d90aa8621bebae07c870940c1a728559bf19141
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})
# ui/modules/PyXRLinuxDriverIPC
%global commit2 75a3e3ee81f590f22a6dfd07719207f701f9c168
%global shortcommit2 %(c=%{commit2}; echo ${c:0:7})

%global uuid breezydesktop@xronlinux.com

Name:           breezy-desktop
Version:        2.12.2
Release:        4%{?dist}
Summary:        XR virtual desktop for GNOME and KDE Plasma
License:        GPL-3.0-or-later
URL:            https://github.com/wheaney/breezy-desktop
# Same architectures supported by XRLinuxDriver:
ExclusiveArch:  x86_64 aarch64

Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/wheaney/sombrero/archive/%{commit1}.tar.gz#/sombrero-%{shortcommit1}.tar.gz
Source2:        https://github.com/wheaney/PyXRLinuxDriverIPC/archive/%{commit2}.tar.gz#/PyXRLinuxDriverIPC-%{shortcommit2}.tar.gz
Source3:        com.xronlinux.BreezyDesktop.metainfo.xml
Source4:        com.xronlinux.BreezyDesktop.KWin.metainfo.xml
Patch0:         %{name}-system-paths.patch
Patch1:         %{name}-virtualdisplayrow.patch

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  extra-cmake-modules
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  glib2-devel
BuildRequires:  gtk-update-icon-cache
BuildRequires:  kwin-devel
BuildRequires:  libappstream-glib
BuildRequires:  libdrm-devel
BuildRequires:  libepoxy-devel
BuildRequires:  librsvg2-tools
BuildRequires:  libxcb-devel
BuildRequires:  meson
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  python3-devel
BuildRequires:  cmake(KF6Config)
BuildRequires:  cmake(KF6ConfigWidgets)
BuildRequires:  cmake(KF6CoreAddons)
BuildRequires:  cmake(KF6GlobalAccel)
BuildRequires:  cmake(KF6I18n)
BuildRequires:  cmake(KF6KCMUtils)
BuildRequires:  cmake(KF6WindowSystem)
BuildRequires:  cmake(KF6XmlGui)
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6DBus)
BuildRequires:  cmake(Qt6Network)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  qt6-qtquick3d

%description
Breezy Desktop is an XR desktop for supported XR glasses, providing virtual
displays that are anchored in space. It requires XRLinuxDriver to be installed
and running.

%package        gnome
Summary:        Breezy Desktop GNOME Shell extension and control panel
%if 0%{?rhel}
License:        GPL-3.0-or-later AND LGPL-2.1-or-later
%endif
BuildArch:      noarch
Requires:       gnome-shell >= 46
Requires:       gstreamer1
Requires:       gtk4
Requires:       libadwaita
Requires:       pipewire-gstreamer
Requires:       python3-gobject
Requires:       xr-driver
%if 0%{?fedora}
Requires:       python3-gstreamer1
Requires:       python3-pydbus
%else
Provides:       bundled(python3-pydbus) = 0.6.0
%endif

%description    gnome
Breezy Desktop is an XR desktop for supported XR glasses, providing virtual
displays that are anchored in space. It requires XRLinuxDriver to be installed
and running.

This package contains the GNOME Shell extension and its control panel.

%package        kwin
Summary:        Breezy Desktop KWin effect
Requires:       kwin-common%{?_isa}
Requires:       python3
Requires:       qt6-qtquick3d%{?_isa}
Requires:       xr-driver%{?_isa}

%description    kwin
Breezy Desktop is an XR desktop for supported XR glasses, providing virtual
displays that are anchored in space. It requires XRLinuxDriver to be installed
and running.

This package contains the KWin effect and its configuration module.

%prep
%autosetup -p1

tar -xzf %{SOURCE1} --strip-components=1 -C modules/sombrero
tar -xzf %{SOURCE2} --strip-components=1 -C ui/modules/PyXRLinuxDriverIPC

# Files copied in place by the upstream KWin setup script
cp VERSION kwin/
cp ui/modules/PyXRLinuxDriverIPC/xrdriveripc.py kwin/src/xrdriveripc/
cp modules/sombrero/*.png kwin/src/qml/
cp ui/data/icons/hicolor/scalable/apps/com.xronlinux.BreezyDesktop.svg kwin/src/kcm/

sed -i -e '1{\@^#!@d}' ui/src/virtualdisplay.py kwin/src/xrdriveripc/xrdriveripc_runner.py

%build
pushd ui
%meson
%meson_build
popd

pushd kwin
%cmake_kf6 \
    -DBUILD_TESTING=OFF
%cmake_build
popd

%install
pushd ui
%meson_install
popd
chmod 0755 %{buildroot}%{_bindir}/{breezydesktop,virtualdisplay}

pushd kwin
%cmake_install
popd

%if 0%{?fedora}
rm -fr %{buildroot}%{_datadir}/breezydesktop/breezydesktop/lib
%endif
%py_byte_compile %{python3} %{buildroot}%{_datadir}/breezydesktop/breezydesktop
%py_byte_compile %{python3} %{buildroot}%{_kf6_datadir}/kwin/effects/breezy_desktop

# Settings schema is installed system wide by the control panel
mkdir -p %{buildroot}%{_datadir}/gnome-shell/extensions/%{uuid}
cp -rL gnome/src/* %{buildroot}%{_datadir}/gnome-shell/extensions/%{uuid}/
rm -fr %{buildroot}%{_datadir}/gnome-shell/extensions/%{uuid}/schemas

install -p -m 0755 -D gnome/bin/breezy_gnome_logs %{buildroot}%{_bindir}/breezy_gnome_logs
install -p -m 0755 -D kwin/bin/breezy_kwin_logs %{buildroot}%{_bindir}/breezy_kwin_logs

# Replaces the upstream file
install -p -m 0644 %{SOURCE3} %{SOURCE4} %{buildroot}%{_metainfodir}/

for size in 64 128 256; do
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps
    rsvg-convert -w $size -h $size ui/data/icons/hicolor/scalable/apps/com.xronlinux.BreezyDesktop.svg \
        -o %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/com.xronlinux.BreezyDesktop.png
done

%find_lang breezydesktop

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop
appstream-util validate --nonet %{buildroot}%{_metainfodir}/*.metainfo.xml

%files gnome -f breezydesktop.lang
%license LICENSE
%doc README.md
%{_bindir}/breezy_gnome_logs
%{_bindir}/breezydesktop
%{_bindir}/virtualdisplay
%{_datadir}/applications/com.xronlinux.BreezyDesktop.desktop
%{_datadir}/breezydesktop
%{_datadir}/glib-2.0/schemas/com.xronlinux.BreezyDesktop.gschema.xml
%{_datadir}/gnome-shell/extensions/%{uuid}
%{_datadir}/icons/hicolor/*/apps/com.xronlinux.BreezyDesktop.*
%{_metainfodir}/com.xronlinux.BreezyDesktop.metainfo.xml

%files kwin
%license LICENSE
%doc README.md
%{_bindir}/breezy_kwin_logs
%{_kf6_datadir}/applications/breezy_desktop.desktop
%{_kf6_datadir}/icons/hicolor/*/apps/com.xronlinux.BreezyDesktop.*
%{_kf6_datadir}/kwin/effects/breezy_desktop
%{_kf6_qtplugindir}/kwin/effects/plugins/breezy_desktop.so
%{_kf6_qtplugindir}/plasma/kcms/breezy_desktop_config.so
%{_metainfodir}/com.xronlinux.BreezyDesktop.KWin.metainfo.xml

%changelog
* Wed Oct 21 2026 Simone Caronni <negativo17@gmail.com> - 2.12.2-4
- Add AppStream metadata for the KWin effect, replace the GNOME one.
- Add PNG icons.

* Wed Oct 21 2026 Simone Caronni <negativo17@gmail.com> - 2.12.2-3
- Require xr-driver.

* Wed Oct 21 2026 Simone Caronni <negativo17@gmail.com> - 2.12.2-2
- Drop common subpackage.
- Install missing virtualdisplayrow module.

* Wed Oct 21 2026 Simone Caronni <negativo17@gmail.com> - 2.12.2-1
- First build.
