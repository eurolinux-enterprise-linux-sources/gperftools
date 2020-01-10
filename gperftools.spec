# This package used to be called "google-perftools", but it was renamed on 2012-02-03.

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

Name:		gperftools
Version:	2.4
Release:	7%{?dist}
License:	BSD
Group:		Development/Tools
Summary:	Very fast malloc and performance analysis tools
URL:		http://code.google.com/p/gperftools/
Source0:	https://googledrive.com/host/0B6NtGsLhIcf7MWxMMF9JdTN3UVk/%{name}-%{version}.tar.gz

# For bz 1232702 - gperftools: tcmalloc debug version uses hard-coded path /tmp/google.alloc
Patch1: gperf-allow-customizing-trace-filename.patch

ExcludeArch:	s390 s390x
%ifnarch ppc %{power64}
BuildRequires:	libunwind-devel
%endif
Requires:	gperftools-devel = %{version}-%{release}
Requires:	pprof = %{version}-%{release}

%description
Perf Tools is a collection of performance analysis tools, including a 
high-performance multi-threaded malloc() implementation that works
particularly well with threads and STL, a thread-friendly heap-checker,
a heap profiler, and a cpu-profiler.

This is a metapackage which pulls in all of the gperftools (and pprof)
binaries, libraries, and development headers, so that you can use them.

%package devel
Summary:	Development libraries and headers for gperftools
Group:		Development/Libraries
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
Provides:	google-perftools-devel = %{version}-%{release}
Obsoletes:	google-perftools-devel < 2.0

%description devel
Libraries and headers for developing applications that use gperftools.

%package libs
Summary:	Libraries provided by gperftools
Provides:	google-perftools-libs = %{version}-%{release}
Obsoletes:	google-perftools-libs < 2.0

%description libs
Libraries provided by gperftools, including libtcmalloc and libprofiler.

%package -n pprof
Summary:	CPU and Heap Profiler tool
Requires:	graphviz
BuildArch:	noarch
Provides:	google-perftools = %{version}-%{release}
Obsoletes:	google-perftools < 2.0

%description -n pprof 
Pprof is a heap and CPU profiler tool, part of the gperftools suite.

%prep
%setup -q
%patch1 -p1

# Fix end-of-line encoding
sed -i 's/\r//' README_windows.txt

# No need to have exec permissions on source code
chmod -x src/*.h src/*.cc

%build
CFLAGS=`echo $RPM_OPT_FLAGS -fno-strict-aliasing -Wno-unused-local-typedefs -DTCMALLOC_LARGE_PAGES | sed -e 's|-fexceptions||g'`
CXXFLAGS=`echo $RPM_OPT_FLAGS -fno-strict-aliasing -Wno-unused-local-typedefs -DTCMALLOC_LARGE_PAGES | sed -e 's|-fexceptions||g'`
%configure --disable-static 

# Bad rpath!
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
# Can't build with smp_mflags
make 

%install
make DESTDIR=%{buildroot} docdir=%{_pkgdocdir}/ install
find %{buildroot} -type f -name "*.la" -exec rm -f {} ';'

# Delete useless files
rm -rf %{buildroot}%{_pkgdocdir}/INSTALL

%check
# http://code.google.com/p/google-perftools/issues/detail?id=153
%ifnarch ppc
# Their test suite is almost always broken.
# LD_LIBRARY_PATH=./.libs make check
%endif

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files

%files -n pprof
%{_bindir}/pprof
%{_mandir}/man1/*

%files devel
%{_pkgdocdir}/
%{_includedir}/google/
%{_includedir}/gperftools/
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%files libs
%{_libdir}/*.so.*

%changelog
* Wed Aug 26 2015 Miroslav Rezanina <mrezanin@redhat.com> 2.4-7
- Rebuild to fix NVR [bz#1269032]
- Resolves: bz#1269032
  (gperftools NVR lower than EPEL version)

* Wed Aug 26 2015 Miroslav Rezanina <mrezanin@redhat.com> 2.4-2
- gperf-allow-customizing-trace-filename.patch [bz#1232702]
- Resolves: bz#1232702
  (gperftools: tcmalloc debug version uses hard-coded path /tmp/google.alloc) 

* Tue Jun 02 2015 Miroslav Rezanina <mrezanin@redhat.com> 2.4-1
- Import to RHEL
