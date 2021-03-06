%global	_node_image_dir /usr/share/%{name}/image/
%global	_node_image_file %{_node_image_dir}/%{name}-4.3.8-1.el7.squashfs.img

# Disable compression, because the image is already compressed
%define _source_payload w0.gzdio
%define _binary_payload w0.gzdio

Name:       ovirt-node-ng-image-update
Version:    4.3.8
Release:    1.el7
License:    GPLv2
Summary:    oVirt Node Next Image Update
URL:        http://www.ovirt.org/node/
Source0:    %{name}-4.3.8.tar.gz
Source1:    ovirt-node-ng-image.squashfs.img
Source2:    product.img

Requires:   imgbased >= 0.7.2
Obsoletes:  %{name}-placeholder < %{version}-%{release}
Provides:   %{name}-placeholder = %{version}-%{release}
Obsoletes:  ovirt-node-ng-image < %{version}-%{release}
Provides:   ovirt-node-ng-image = %{version}-%{release}

BuildArch:  noarch
BuildRequires: autoconf
BuildRequires: automake

%description
This package will update an  oVirt Node Next host with the new image.

%prep
%setup -q -n %{name}-4.3.8

%build
%configure
make %{?_smp_mflags}

%install
# Install the image
/usr/bin/install -d %{buildroot}/%{_node_image_dir}
/usr/bin/install -m 644 %{SOURCE1} %{buildroot}/%{_node_image_file}
/usr/bin/install -m 644 %{SOURCE2} %{buildroot}/%{_node_image_dir}/product.img

%pre
local_sds=($(find / -xdev -name "__DIRECT_IO_TEST__"))

if [ "$local_sds" ]; then
    echo "Local storage domains were found on the same filesystem as / ! Please migrate the data to a new LV before upgrading, or you will lose the VMs"
    echo "See: https://bugzilla.redhat.com/show_bug.cgi?id=1550205#c3"
    echo "Storage domains were found in:"
    for sd in "${local_sds[@]}"; do
        echo -e "\t$(dirname $sd)"
    done
    exit 1
fi

%post
set -e
# Some magic to ensure that imgbase from
# the new image is used for updates
export IMGBASED_IMAGE_UPDATE_RPM=$(lsof -p $PPID 2>/dev/null | grep image-update | awk '{print $9}')
export MNTDIR="$(mktemp -d)"
mount "%{_node_image_file}" "$MNTDIR"
mount "$MNTDIR"/LiveOS/rootfs.img "$MNTDIR"
export PYTHONPATH=$(find $MNTDIR/usr/lib/python* -name imgbased -type d -exec dirname {} \; | sort | tail -1):$PYTHONPATH
imgbase --debug update --format liveimg %{_node_image_file} >> /var/log/imgbased.log 2>&1
umount "$MNTDIR"
umount "$MNTDIR"

%files
%dir %{_node_image_dir}
%{_node_image_file}
%{_node_image_dir}/product.img

%changelog
* Thu Mar 5 2020 di.wang <di.wang@cs2c.com.cn> - 4.3.8-1
- Package Initialization
