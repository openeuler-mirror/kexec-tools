%global eppic_ver d84c3541035d95077aa8571f5d5c3e07c6ef510b
%global eppic_shortver %(c=%{eppic_ver}; echo ${c:0:7})
%global mkdf_ver 1.6.7

Name: kexec-tools
Version: 2.0.20
Release: 14
License: GPLv2
Summary: The kexec/kdump userspace component
URL:     https://www.kernel.org/
Source0: http://kernel.org/pub/linux/utils/kernel/kexec/%{name}-%{version}.tar.xz
Source1: kdumpctl
Source2: kdump.sysconfig
Source3: kdump.sysconfig.x86_64
Source4: kdump.sysconfig.i386
Source5: kdump.sysconfig.ppc64
Source7: mkdumprd
Source8: kdump.conf
Source9: http://downloads.sourceforge.net/project/makedumpfile/makedumpfile/%{mkdf_ver}/makedumpfile-%{mkdf_ver}.tar.gz
Source12: mkdumprd.8
Source13: 98-kexec.rules
Source14: 98-kexec.rules.ppc64
Source15: kdump.conf.5
Source16: kdump.service
Source18: kdump.sysconfig.s390x
Source19: https://github.com/lucchouina/eppic/archive/%{eppic_ver}/eppic-%{eppic_shortver}.tar.gz
Source20: kdump-lib.sh
Source21: kdump-in-cluster-environment.txt
Source22: kdump-dep-generator.sh
Source23: kdump-lib-initramfs.sh
Source24: kdump.sysconfig.ppc64le
Source25: kdumpctl.8
Source26: live-image-kdump-howto.txt
Source27: early-kdump-howto.txt
Source28: kdump-udev-throttler
Source29: kdump.sysconfig.aarch64

Source100: dracut-kdump.sh
Source101: dracut-module-setup.sh
Source102: dracut-monitor_dd_progress
Source103: dracut-kdump-error-handler.sh
Source104: dracut-kdump-emergency.service
Source105: dracut-kdump-error-handler.service
Source106: dracut-kdump-capture.service
Source107: dracut-kdump-emergency.target
Source108: dracut-early-kdump.sh
Source109: dracut-early-kdump-module-setup.sh
Source110: dracut-kdump-wait-for-target.sh

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(pre): coreutils sed zlib
Requires: dracut >= 047-34.git20180604
Requires: dracut-network >= 044-117
Requires: dracut-squash >= 049-4
Requires: ethtool
BuildRequires: zlib-devel zlib zlib-static elfutils-devel-static glib2-devel bzip2-devel ncurses-devel bison flex lzo-devel snappy-devel
BuildRequires: pkgconfig intltool gettext
BuildRequires: systemd-units
BuildRequires: automake autoconf libtool
%ifarch %{ix86} x86_64
Obsoletes: diskdumputils netdump kexec-tools-eppic
%endif

%ifnarch s390x
Requires:       systemd-udev%{?_isa}
%endif

%undefine _hardened_build

Patch0:  kexec-tools-2.0.20-fix-broken-multiboot2-buliding-for-i386.patch
Patch1:  kexec-tools-2.0.20-eppic-Remove-duplicated-variable-declaration.patch
Patch2:  kexec-tools-2.0.20-makedumpfile-Remove-duplicated-variable-declarations.patch
Patch3:  kexec-tools-2.0.20-Remove-duplicated-variable-declarations.patch
Patch4:  kexec-tools-2.0.20-makedumpfile-Introduce-check-params-option.patch
Patch5:  kexec-add-variant-helper-functions-for-handling-memory-regions.patch
Patch6:  arm64-kexec-allocate-memory-space-avoiding-reserved-regions.patch

%ifarch aarch64
Patch7:  arm64-support-more-than-one-crash-kernel-regions.patch
%endif

Patch8:  add-secure-compile-options-for-makedumpfile.patch

Patch9:  bugfix-get-the-paddr-of-mem_section-return-error-address.patch
Patch10: fix-header-offset-overflow-when-large-pfn.patch

%description
kexec-tools provides /sbin/kexec binary that facilitates a new
kernel to boot using the kernel's kexec feature either on a
normal or a panic reboot. This package contains the /sbin/kexec
binary and ancillary utilities that together form the userspace
component of the kernel's kexec feature.

%package    help
Summary:    Doc files for %{name}
Buildarch:  noarch

%description    help
The %{name}-help package contains doc files for %{name}.

%prep
%setup -q

mkdir -p -m755 kcp
tar -z -x -v -f %{SOURCE9}
tar -z -x -v -f %{SOURCE19}

%patch0  -p1
%patch1  -p1
%patch2  -p1
%patch3  -p1
%patch4  -p1
%patch5  -p1
%patch6  -p1
%ifarch aarch64
%patch7  -p1
%endif

%patch8  -p1
%patch9  -p1
%patch10 -p1

%build
autoreconf
%configure --sbindir=/usr/sbin \
    CFLAGS="${CFLAGS} -fstack-protector-strong -Wl,-z,now -pie -fPIC -fPIE"
rm -f kexec-tools.spec.in
# for docs
cp %{SOURCE21} %{SOURCE26} %{SOURCE27} .

make
%ifarch %{ix86} x86_64 aarch64
make -C eppic-%{eppic_ver}/libeppic
make -C makedumpfile-%{mkdf_ver} LINKTYPE=dynamic USELZO=on USESNAPPY=on
make -C makedumpfile-%{mkdf_ver} LDFLAGS="$LDFLAGS -I../eppic-%{eppic_ver}/libeppic -L../eppic-%{eppic_ver}/libeppic" eppic_makedumpfile.so
%endif

%install
mkdir -p -m755 %{buildroot}/usr/sbin
mkdir -p -m755 %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p -m755 %{buildroot}%{_localstatedir}/crash
mkdir -p -m755 %{buildroot}%{_mandir}/man8/
mkdir -p -m755 %{buildroot}%{_mandir}/man5/
mkdir -p -m755 %{buildroot}%{_docdir}
mkdir -p -m755 %{buildroot}%{_datadir}/kdump
mkdir -p -m755 %{buildroot}%{_udevrulesdir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p -m755 %{buildroot}%{_bindir}
mkdir -p -m755 %{buildroot}%{_libdir}
mkdir -p -m755 %{buildroot}%{_prefix}/lib/kdump
install -m 755 %{SOURCE1} %{buildroot}%{_bindir}/kdumpctl

install -m 755 build/sbin/kexec %{buildroot}/usr/sbin/kexec
install -m 755 build/sbin/vmcore-dmesg %{buildroot}/usr/sbin/vmcore-dmesg
install -m 644 build/man/man8/kexec.8 %{buildroot}%{_mandir}/man8/
install -m 644 build/man/man8/vmcore-dmesg.8 %{buildroot}%{_mandir}/man8/

SYSCONFIG=%{_sourcedir}/kdump.sysconfig.%{_target_cpu}
[ -f $SYSCONFIG ] || SYSCONFIG=%{_sourcedir}/kdump.sysconfig.%{_arch}
[ -f $SYSCONFIG ] || SYSCONFIG=%{_sourcedir}/kdump.sysconfig
install -m 644 $SYSCONFIG %{buildroot}%{_sysconfdir}/sysconfig/kdump

install -m 755 %{SOURCE7} %{buildroot}/usr/sbin/mkdumprd
install -m 644 %{SOURCE8} %{buildroot}%{_sysconfdir}/kdump.conf
install -m 644 kexec/kexec.8 %{buildroot}%{_mandir}/man8/kexec.8
install -m 644 %{SOURCE12} %{buildroot}%{_mandir}/man8/mkdumprd.8
install -m 644 %{SOURCE25} %{buildroot}%{_mandir}/man8/kdumpctl.8
install -m 755 %{SOURCE20} %{buildroot}%{_prefix}/lib/kdump/kdump-lib.sh
install -m 755 %{SOURCE23} %{buildroot}%{_prefix}/lib/kdump/kdump-lib-initramfs.sh
install -m 755 %{SOURCE28} $RPM_BUILD_ROOT%{_udevrulesdir}/../kdump-udev-throttler
install -m 644 %{SOURCE15} %{buildroot}%{_mandir}/man5/kdump.conf.5
install -m 644 %{SOURCE16} %{buildroot}%{_unitdir}/kdump.service
install -m 755 -D %{SOURCE22} %{buildroot}%{_prefix}/lib/systemd/system-generators/kdump-dep-generator.sh
install -m 644 %{SOURCE13} $RPM_BUILD_ROOT%{_udevrulesdir}/98-kexec.rules
install -m 644 %{SOURCE14} %{buildroot}%{_udevrulesdir}/98-kexec.rules

%ifarch %{ix86} x86_64 aarch64
install -m 755 makedumpfile-%{mkdf_ver}/makedumpfile $RPM_BUILD_ROOT/usr/sbin/makedumpfile
install -m 644 makedumpfile-%{mkdf_ver}/makedumpfile.8.gz $RPM_BUILD_ROOT/%{_mandir}/man8/makedumpfile.8.gz
install -m 644 makedumpfile-%{mkdf_ver}/makedumpfile.conf.5.gz $RPM_BUILD_ROOT/%{_mandir}/man5/makedumpfile.conf.5.gz
install -m 644 makedumpfile-%{mkdf_ver}/makedumpfile.conf $RPM_BUILD_ROOT/%{_sysconfdir}/makedumpfile.conf.sample
install -m 755 makedumpfile-%{mkdf_ver}/eppic_makedumpfile.so $RPM_BUILD_ROOT/%{_libdir}/eppic_makedumpfile.so
mkdir -p $RPM_BUILD_ROOT/usr/share/makedumpfile/eppic_scripts/
install -m 644 makedumpfile-%{mkdf_ver}/eppic_scripts/* $RPM_BUILD_ROOT/usr/share/makedumpfile/eppic_scripts/
%endif

%define remove_dracut_prefix() %(echo -n %1|sed 's/.*dracut-//g')
%define remove_dracut_early_kdump_prefix() %(echo -n %1|sed 's/.*dracut-early-kdump-//g')

# For dracut modules
mkdir -p -m755 %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase
cp %{SOURCE100} %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE100}}
cp %{SOURCE101} %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE101}}
cp %{SOURCE102} %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE102}}
cp %{SOURCE103} %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE103}}
cp %{SOURCE104} %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE104}}
cp %{SOURCE105} %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE105}}
cp %{SOURCE106} %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE106}}
cp %{SOURCE107} %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE107}}
cp %{SOURCE110} $RPM_BUILD_ROOT/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE110}}
chmod 755 %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE100}}
chmod 755 %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE101}}
mkdir -p -m755 %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99earlykdump
cp %{SOURCE108} %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99earlykdump/%{remove_dracut_prefix %{SOURCE108}}
cp %{SOURCE109} %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99earlykdump/%{remove_dracut_early_kdump_prefix %{SOURCE109}}
chmod 755 %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99earlykdump/%{remove_dracut_prefix %{SOURCE108}}
chmod 755 %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99earlykdump/%{remove_dracut_early_kdump_prefix %{SOURCE109}}
chmod 755 %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/99kdumpbase/%{remove_dracut_prefix %{SOURCE103}}

%define dracutlibdir %{_prefix}/lib/dracut
# For custom dracut modules
mkdir -p %{buildroot}/%{dracutlibdir}/modules.d/
mv %{buildroot}/etc/kdump-adv-conf/kdump_dracut_modules/* %{buildroot}/%{dracutlibdir}/modules.d/

%post
%systemd_post kdump.service

touch /etc/kdump.conf
# Fix up broken boxes
if [ -d /proc/bus/mckinley ]
then
	# for HP zx1 machines
	sed -e's/\(^KDUMP_COMMANDLINE_APPEND.*\)\("$\)/\1 machvec=dig"/' \
	/etc/sysconfig/kdump > /etc/sysconfig/kdump.new
	mv /etc/sysconfig/kdump.new /etc/sysconfig/kdump
elif [ -d /proc/sgi_sn ]
then
	# for SGI SN boxes
	sed -e's/\(^KEXEC_ARGS.*\)\("$\)/\1 --noio"/' \
	/etc/sysconfig/kdump > /etc/sysconfig/kdump.new
	mv /etc/sysconfig/kdump.new /etc/sysconfig/kdump
fi


%postun
%systemd_postun_with_restart kdump.service

%preun
%systemd_preun kdump.service

%triggerun -- kexec-tools < 2.0.2-3
# Save runlevel info for future migration
/usr/bin/systemd-sysv-convert --save kdump >/dev/null 2>&1 ||:
# Not needed after uninstall
/sbin/chkconfig --del kdump >/dev/null 2>&1 || :
/bin/systemctl try-restart kdump.service >/dev/null 2>&1 || :

%triggerin -- kernel-kdump
touch %{_sysconfdir}/kdump.conf

%triggerpostun -- kernel kernel-xen kernel-debug kernel-PAE kernel-kdump
# Search for kernel installs, if not found, remove kdump initrd
IMGDIR=/boot
for i in `ls $IMGDIR/initramfs*kdump.img 2>/dev/null`
do
	KDVER=`echo $i | sed -e's/^.*initramfs-//' -e's/kdump.*$//'`
	if [ ! -e $IMGDIR/vmlinuz-$KDVER ]
	then
		rm -f $i
	fi
done


%files
%doc News
%doc TODO
%license COPYING
%config(noreplace,missingok) %{_sysconfdir}/sysconfig/kdump
%config(noreplace,missingok) %verify(not mtime) %{_sysconfdir}/kdump.conf
%config %{_udevrulesdir}
%{_udevrulesdir}/../kdump-udev-throttler
%dir %{_localstatedir}/crash
/usr/sbin/kexec
/usr/sbin/mkdumprd
/usr/sbin/vmcore-dmesg
%{_bindir}/*
%{_datadir}/kdump
%{_prefix}/lib/kdump
%{dracutlibdir}/modules.d/*
%{_unitdir}/kdump.service
%{_prefix}/lib/systemd/system-generators/kdump-dep-generator.sh
%ifarch %{ix86} x86_64 aarch64
%{_libdir}/eppic_makedumpfile.so
/usr/share/makedumpfile/
%endif
%ifarch %{ix86} x86_64 aarch64
%{_sysconfdir}/makedumpfile.conf.sample
%endif
%ifarch %{ix86} x86_64 aarch64
/usr/sbin/makedumpfile
%endif

%files help
%doc early-kdump-howto.txt
%doc kdump-in-cluster-environment.txt
%doc live-image-kdump-howto.txt
%{_mandir}/man8/kdumpctl.8.gz
%{_mandir}/man8/kexec.8.gz
%{_mandir}/man8/mkdumprd.8.gz
%{_mandir}/man8/vmcore-dmesg.8.gz
%{_mandir}/man5/*
%ifarch %{ix86} x86_64 aarch64
%{_mandir}/man8/makedumpfile.8.gz
%endif

%changelog
* Fri Nov 27 2020 yangzhuangzhuang <yangzhuangzhuang1@huawei.com> - 2.0.20-14
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix issue about iomem file that contains too many contens.As a result,the kdump service failed

* Tue May 19 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.0.20-13
- Type:enhancement
- ID:NA
- SUG:restart
- DESC:fix kdump service failed on x86 because of KDUMP_FILE_LOAD is set to on

* Thu May 14 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.0.20-12
- Type:enhancement
- ID:NA
- SUG:restart
- DESC:fix kdump kernel stuck

* Sun Apr 26 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.0.20-11
- Type:enhancement
- ID:NA
- SUG:restart
- DESC:upgrage to 2.0.20

* Wed Jan 1 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.0.17-15
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:modify patch

* Tue Dec 31 2019 Jialong Chen <chenjialong@huawei.com> - 2.0.17-14
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:modify SECTION_SIZE_BITS to 30 and keep the same as the kernel configuration.
       add executable permissions for kdump-error-handler.sh.

* Thu Dec 19 2019 chengquan <chengquan3@huawei.com> - 2.0.17-13
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:add url for package

* Wed Sep 25 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.0-17.12
- add secure compile options and merge bugfix patches from community
  xen: Avoid overlapping segments in low memory
  x86: Check /proc/mounts before mtab for mounts
  x86: Find mounts by FS type, not name
  kexec/kexec.c: Add the missing close() for fd used for kexec_file_load()
  kexec-uImage-arm64.c: Fix return value of uImage_arm64_probe()
  kexec/kexec-zlib.h: Add 'is_zlib_file()' helper function
  kexec/arm64: Add support for handling zlib compressed (Image.gz) image

* Thu Sep 21 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.0-17.11
- Package init

* Thu Aug 22 2019 Yeqing Peng<pengyeqing@huawei.com> - 2.0-17.10.h1
- Type:bugfix
- ID:NA
- SUG:restart
- DESC: fix bugs as follows:
	1.dmesg fix infinite loop if log buffer wraps around.
	2.arm64 error out if kernel command line is too long.
	3.fix an error that can not parse the e820 reserved region.
	4.x86 fix BAD_FREE in get_efi_runtime_map().
	5.fix check against 'fdt_add_subnode' return value.
	6.arm64 add error handling check against return value of 'set_bootargs()'.
	7.fix adding '/chosen' node for cases where it is not available in dtb
	  passed via --dtb option.
	8.fix '/chosen' v/s 'chosen' node being passed to fdt helper functions.
	9.arm64 wipe old initrd addresses when patching the DTB.
	10.arm64 increase the command line buf space to 1536.
	11.arm64 bugfix get the paddr of mem_section return error address.
	12.arm64 support more than one crash kernel regions.
	13.modify SECTIONS_SIZE_BITS to 27 for arm64.
