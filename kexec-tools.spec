Name: kexec-tools
Version: 2.0.17
Release: 15
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
Source9: http://downloads.sourceforge.net/project/makedumpfile/makedumpfile/1.6.4/makedumpfile-1.6.4.tar.gz
Source12: mkdumprd.8
Source14: 98-kexec.rules
Source15: kdump.conf.5
Source16: kdump.service
Source18: kdump.sysconfig.s390x
Source19: eppic_050615.tar.gz
Source20: kdump-lib.sh
Source21: kdump-in-cluster-environment.txt
Source22: kdump-dep-generator.sh
Source23: kdump-lib-initramfs.sh
Source24: kdump.sysconfig.ppc64le
Source25: kdumpctl.8
Source26: live-image-kdump-howto.txt
Source27: early-kdump-howto.txt

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

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(pre): coreutils sed zlib
Requires: dracut >= 047-34.git20180604
Requires: dracut-network >= 044-117
Requires: ethtool
BuildRequires: zlib-devel zlib zlib-static elfutils-devel-static glib2-devel bzip2-devel ncurses-devel bison flex lzo-devel snappy-devel
BuildRequires: pkgconfig intltool gettext
BuildRequires: systemd-units
BuildRequires: automake autoconf libtool
%ifarch %{ix86} x86_64
Obsoletes: diskdumputils netdump kexec-tools-eppic
%endif

%undefine _hardened_build

Patch101: kexec-tools-2.0.17-kexec-fix-for-Unhandled-rela-relocation-R_X86_64_PLT.patch

Patch6000: vmcore-dmesg-fix-infinite-loop-if-log-buffer-wraps-a.patch
Patch6001: arm64-error-out-if-kernel-command-line-is-too-long.patch
Patch6002: kdump-fix-an-error-that-can-not-parse-the-e820-reser.patch
Patch6003: x86-fix-BAD_FREE-in-get_efi_runtime_map.patch
Patch6004: kexec-dt-ops.c-Fix-check-against-fdt_add_subnode-ret.patch
Patch6005: kexec-kexec-arm64.c-Add-error-handling-check-against.patch
Patch6006: kexec-dt-ops.c-Fix-adding-chosen-node-for-cases-wher.patch
Patch6007: kexec-dt-ops.c-Fix-chosen-v-s-chosen-node-being-pass.patch
Patch6008: arm64-wipe-old-initrd-addresses-when-patching-the-DT.patch
Patch6009: xen-Avoid-overlapping-segments-in-low-memory.patch
Patch6010: x86-Check-proc-mounts-before-mtab-for-mounts.patch
Patch6011: x86-Find-mounts-by-FS-type-not-name.patch
Patch6012: kexec-kexec.c-Add-the-missing-close-for-fd-used-for-kexec_file_load.patch
Patch6013: kexec-uImage-arm64.c-Fix-return-value-of-uImage_arm64_probe.patch
Patch6014: kexec-kexec-zlib.h-Add-is_zlib_file-helper-function.patch
Patch6015: kexec-arm64-Add-support-for-handling-zlib-compressed-image.patch

%ifarch aarch64
Patch9000: kexec-tools-2.0.8-increase-the-buf-space-to-1536.patch
Patch9001: bugfix-get-the-paddr-of-mem_section-return-error-address.patch
Patch9002: arm64-support-more-than-one-crash-kernel-regions.patch
%endif

Patch9003: add-secure-compile-options-for-makedumpfile.patch

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

%patch101 -p1

%{lua:for i=0,8 do print(string.format("%%patch600%u -p1\n", i)) end}
%patch6009 -p1
%patch6010 -p1
%patch6011 -p1
%patch6012 -p1
%patch6013 -p1
%patch6014 -p1
%patch6015 -p1

%ifarch aarch64
%{lua:for i=0,2 do print(string.format("%%patch900%u -p1\n", i)) end}
%endif

%patch9003 -p1

%build
autoreconf
%configure --sbindir=/sbin \
    CFLAGS="${CFLAGS} -fstack-protector-strong -Wl,-z,now -pie -fPIC -fPIE"
rm -f kexec-tools.spec.in
# for docs
cp %{SOURCE21} %{SOURCE26} %{SOURCE27} .

make
%ifarch %{ix86} x86_64 aarch64
make -C eppic/libeppic
make -C makedumpfile-1.6.4 LINKTYPE=dynamic USELZO=on USESNAPPY=on
make -C makedumpfile-1.6.4 LDFLAGS="-I../eppic/libeppic -L../eppic/libeppic" eppic_makedumpfile.so
%endif

%install
mkdir -p -m755 %{buildroot}/sbin
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

install -m 755 build/sbin/kexec %{buildroot}/sbin/kexec
install -m 755 build/sbin/vmcore-dmesg %{buildroot}/sbin/vmcore-dmesg
install -m 644 build/man/man8/kexec.8 %{buildroot}%{_mandir}/man8/
install -m 644 build/man/man8/vmcore-dmesg.8 %{buildroot}%{_mandir}/man8/

SYSCONFIG=%{_sourcedir}/kdump.sysconfig.%{_target_cpu}
[ -f $SYSCONFIG ] || SYSCONFIG=%{_sourcedir}/kdump.sysconfig.%{_arch}
[ -f $SYSCONFIG ] || SYSCONFIG=%{_sourcedir}/kdump.sysconfig
install -m 644 $SYSCONFIG %{buildroot}%{_sysconfdir}/sysconfig/kdump

install -m 755 %{SOURCE7} %{buildroot}/sbin/mkdumprd
install -m 644 %{SOURCE8} %{buildroot}%{_sysconfdir}/kdump.conf
install -m 644 kexec/kexec.8 %{buildroot}%{_mandir}/man8/kexec.8
install -m 644 %{SOURCE12} %{buildroot}%{_mandir}/man8/mkdumprd.8
install -m 644 %{SOURCE25} %{buildroot}%{_mandir}/man8/kdumpctl.8
install -m 755 %{SOURCE20} %{buildroot}%{_prefix}/lib/kdump/kdump-lib.sh
install -m 755 %{SOURCE23} %{buildroot}%{_prefix}/lib/kdump/kdump-lib-initramfs.sh
install -m 644 %{SOURCE15} %{buildroot}%{_mandir}/man5/kdump.conf.5
install -m 644 %{SOURCE16} %{buildroot}%{_unitdir}/kdump.service
install -m 755 -D %{SOURCE22} %{buildroot}%{_prefix}/lib/systemd/system-generators/kdump-dep-generator.sh
install -m 644 %{SOURCE14} %{buildroot}%{_udevrulesdir}/98-kexec.rules

%ifarch %{ix86} x86_64 aarch64
install -m 755 makedumpfile-1.6.4/makedumpfile %{buildroot}/sbin/makedumpfile
install -m 644 makedumpfile-1.6.4/makedumpfile.8.gz %{buildroot}/%{_mandir}/man8/makedumpfile.8.gz
install -m 644 makedumpfile-1.6.4/makedumpfile.conf.5.gz %{buildroot}/%{_mandir}/man5/makedumpfile.conf.5.gz
install -m 644 makedumpfile-1.6.4/makedumpfile.conf %{buildroot}/%{_sysconfdir}/makedumpfile.conf.sample
install -m 755 makedumpfile-1.6.4/eppic_makedumpfile.so %{buildroot}/%{_libdir}/eppic_makedumpfile.so
mkdir -p %{buildroot}/usr/share/makedumpfile/eppic_scripts/
install -m 644 makedumpfile-1.6.4/eppic_scripts/* %{buildroot}/usr/share/makedumpfile/eppic_scripts/
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
%config(noreplace,missingok) %{_sysconfdir}/kdump.conf
%config %{_udevrulesdir}
%dir %{_localstatedir}/crash
/sbin/kexec
/sbin/mkdumprd
/sbin/vmcore-dmesg
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
/sbin/makedumpfile
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
